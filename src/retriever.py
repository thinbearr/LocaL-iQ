import time
import re
from typing import List, Dict, Set, Any, Optional
from dataclasses import dataclass, field
from rank_bm25 import BM25Okapi

from src.embedder import LocalEmbedder
from src.vector_store import ChromaVectorStore


@dataclass
class CandidateChunk:
    chunk_id: str
    file_name: str
    note_name: str
    heading: str
    text: str
    raw_semantic_score: float  # Raw Cosine Similarity in [0.0, 1.0]
    lexical_bm25_score: float  # BM25 relevance score
    hybrid_score: float        # Combined weighted score
    rank: int = 0
    selected: bool = False
    prev_chunk_id: Optional[str] = None
    next_chunk_id: Optional[str] = None
    supporting_prev_text: Optional[str] = None
    supporting_next_text: Optional[str] = None
    tags: List[str] = field(default_factory=list)


@dataclass
class RetrievalResult:
    original_query: str
    resolved_query: str
    expanded_query: str
    primary_chunks: List[CandidateChunk]
    all_candidates_evaluated: List[CandidateChunk]
    has_relevant_info: bool
    max_raw_semantic_score: float
    max_hybrid_score: float
    retrieval_latency_ms: float
    files_contributed: List[str]


class HybridRerankedRetriever:
    """
    Two-Stage Hybrid RAG Retriever:
    1. Stage 1: Dense Vector Similarity Search (ChromaDB Top-K candidate pool).
    2. Absolute Semantic Evidence Gate: Enforces raw cosine similarity >= threshold (default 0.28) to prevent hallucination.
    3. Stage 2: Lexical BM25 Reranking over candidate pool.
    4. Hybrid Score Fusion & Bounded Sibling Context Retrieval.
    5. Conversational Query Resolution & Experimental Query Expansion.
    """

    def __init__(
        self,
        embedder: LocalEmbedder,
        vector_store: ChromaVectorStore,
        absolute_semantic_threshold: float = 0.28,
        w_semantic: float = 0.70,
        w_lexical: float = 0.30
    ):
        self.embedder = embedder
        self.vector_store = vector_store
        self.absolute_semantic_threshold = absolute_semantic_threshold
        self.w_semantic = w_semantic
        self.w_lexical = w_lexical

    def resolve_conversational_query(self, user_query: str, chat_history: List[Dict[str, str]]) -> str:
        """
        Resolves ambiguous pronouns/follow-ups using recent chat history.
        """
        if not chat_history:
            return user_query

        query_lower = user_query.lower()
        pronouns = [" it", " it?", " it ", " this", " this?", " this ", " that", " that?", " the database", " the model", " the system"]
        
        has_pronoun = any(p in query_lower for p in pronouns) or len(user_query.split()) < 4

        if has_pronoun and len(chat_history) >= 1:
            last_turn = chat_history[-1]
            last_q = last_turn.get("user", "")
            last_a = last_turn.get("assistant", "")

            # Extract key nouns/topics from previous question or answer
            topics = re.findall(r'\b[A-Z][a-zA-Z0-9_\-]+\b', last_q + " " + last_a)
            if not topics:
                words = [w for w in re.findall(r'\b\w+\b', last_q) if len(w) > 3 and w.lower() not in ["what", "how", "why", "where", "does", "is", "the", "with"]]
                topics = words[:2]

            topic_str = " ".join(dict.fromkeys(topics))
            if topic_str:
                return f"{user_query} ({topic_str})"

        return user_query

    def expand_query(self, query: str) -> str:
        """
        Experimental toggleable query expansion.
        Enriches search query with key domain terminology.
        """
        expansions = {
            "rag": "retrieval augmented generation vector search context",
            "transformer": "self attention multi head query key value",
            "obsidian": "markdown wikilinks PKM vault notes",
            "chroma": "chromadb vector store database embedding",
            "cable": "cable routing path gland selection"
        }
        query_words = query.lower().split()
        added_terms = []
        for word, exp in expansions.items():
            if word in query_words:
                added_terms.append(exp)

        if added_terms:
            return f"{query} {' '.join(added_terms)}"
        return query

    def retrieve(
        self,
        user_query: str,
        chat_history: Optional[List[Dict[str, str]]] = None,
        file_scope: Optional[List[str]] = None,
        vault_scope: Optional[List[str]] = None,
        top_k_candidate_pool: int = 15,
        top_k_final: int = 5,
        enable_query_expansion: bool = False,
        w_semantic: Optional[float] = None,
        w_lexical: Optional[float] = None,
        custom_semantic_threshold: Optional[float] = None
    ) -> RetrievalResult:
        """
        Executes complete Two-Stage Hybrid Retrieval pipeline with absolute semantic gating and sibling context.
        """
        start_time = time.time()
        chat_history = chat_history or []
        
        w_sem = w_semantic if w_semantic is not None else self.w_semantic
        w_lex = w_lexical if w_lexical is not None else self.w_lexical
        sem_thresh = custom_semantic_threshold if custom_semantic_threshold is not None else self.absolute_semantic_threshold

        # Step 1: Conversational Query Resolution
        resolved_query = self.resolve_conversational_query(user_query, chat_history)

        # Step 2: Experimental Query Expansion
        expanded_query = self.expand_query(resolved_query) if enable_query_expansion else resolved_query

        # Step 3: Stage 1 Dense Vector Retrieval (ChromaDB Candidate Pool)
        query_vector = self.embedder.encode_query(expanded_query)
        raw_hits = self.vector_store.query_similar(
            query_embedding=query_vector,
            top_k=top_k_candidate_pool,
            file_scope=file_scope,
            vault_scope=vault_scope
        )

        if not raw_hits:
            elapsed_ms = round((time.time() - start_time) * 1000, 2)
            return RetrievalResult(
                original_query=user_query,
                resolved_query=resolved_query,
                expanded_query=expanded_query,
                primary_chunks=[],
                all_candidates_evaluated=[],
                has_relevant_info=False,
                max_raw_semantic_score=0.0,
                max_hybrid_score=0.0,
                retrieval_latency_ms=elapsed_ms,
                files_contributed=[]
            )

        # Step 4: Absolute Semantic Evidence Gate Check
        max_raw_sem_score = max([hit["raw_cosine_similarity"] for hit in raw_hits], default=0.0)
        has_relevant_info = max_raw_sem_score >= sem_thresh

        # Step 5: Stage 2 Lexical BM25 Reranking over Candidate Pool
        corpus_texts = [f"{h['heading']} {h['text']}" for h in raw_hits]
        tokenized_corpus = [re.findall(r'\w+', text.lower()) for text in corpus_texts]
        tokenized_query = re.findall(r'\w+', expanded_query.lower())

        bm25_scores: List[float] = []
        if tokenized_corpus and tokenized_query:
            bm25 = BM25Okapi(tokenized_corpus)
            bm25_scores = list(bm25.get_scores(tokenized_query))
        else:
            bm25_scores = [0.0] * len(raw_hits)

        # Min-Max Score Normalization
        sem_scores = [hit["raw_cosine_similarity"] for hit in raw_hits]
        min_sem, max_sem = min(sem_scores), max(sem_scores)
        sem_range = (max_sem - min_sem) if (max_sem - min_sem) > 1e-5 else 1.0
        norm_sem = [(s - min_sem) / sem_range for s in sem_scores]

        min_lex, max_lex = min(bm25_scores), max(bm25_scores)
        lex_range = (max_lex - min_lex) if (max_lex - min_lex) > 1e-5 else 1.0
        norm_lex = [(l - min_lex) / lex_range for l in bm25_scores]

        # Step 6: Hybrid Score Fusion
        candidates: List[CandidateChunk] = []
        for idx, hit in enumerate(raw_hits):
            h_score = (w_sem * norm_sem[idx]) + (w_lex * norm_lex[idx])
            cand = CandidateChunk(
                chunk_id=hit["chunk_id"],
                file_name=hit["file_name"],
                note_name=hit["note_name"],
                heading=hit["heading"],
                text=hit["text"],
                raw_semantic_score=hit["raw_cosine_similarity"],
                lexical_bm25_score=round(float(bm25_scores[idx]), 4),
                hybrid_score=round(float(h_score), 4),
                prev_chunk_id=hit.get("prev_chunk_id"),
                next_chunk_id=hit.get("next_chunk_id"),
                tags=hit.get("tags", [])
            )
            candidates.append(cand)

        # Sort candidates by hybrid score descending
        candidates.sort(key=lambda x: x.hybrid_score, reverse=True)

        for rank_idx, cand in enumerate(candidates, 1):
            cand.rank = rank_idx

        # Select Top-K Final Evidence
        top_k_candidates = candidates[:top_k_final] if has_relevant_info else []
        for cand in top_k_candidates:
            cand.selected = True

        # Step 7: Bounded Sibling & Heading Context Retrieval
        for cand in top_k_candidates:
            if cand.prev_chunk_id:
                prev_chunk_data = self.vector_store.get_chunk_by_id(cand.prev_chunk_id)
                if prev_chunk_data:
                    cand.supporting_prev_text = prev_chunk_data["text"][:180] + "..."
            if cand.next_chunk_id:
                next_chunk_data = self.vector_store.get_chunk_by_id(cand.next_chunk_id)
                if next_chunk_data:
                    cand.supporting_next_text = next_chunk_data["text"][:180] + "..."

        max_hybrid_score = max([c.hybrid_score for c in candidates], default=0.0)
        files_contributed = sorted(list(set([c.file_name for c in top_k_candidates])))
        elapsed_ms = round((time.time() - start_time) * 1000, 2)

        return RetrievalResult(
            original_query=user_query,
            resolved_query=resolved_query,
            expanded_query=expanded_query,
            primary_chunks=top_k_candidates,
            all_candidates_evaluated=candidates,
            has_relevant_info=has_relevant_info,
            max_raw_semantic_score=max_raw_sem_score,
            max_hybrid_score=max_hybrid_score,
            retrieval_latency_ms=elapsed_ms,
            files_contributed=files_contributed
        )
