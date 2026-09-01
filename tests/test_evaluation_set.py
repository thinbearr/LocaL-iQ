import pytest
import shutil
from pathlib import Path
from src.vault_parser import VaultParser
from src.chunker import MarkdownChunker
from src.embedder import LocalEmbedder
from src.vector_store import ChromaVectorStore
from src.retriever import HybridRerankedRetriever
from src.generator import LLMGenerator


@pytest.fixture(scope="module")
def setup_eval_env():
    vault_dir = Path(__file__).parent.parent / "sample_vault"
    db_dir = Path(__file__).parent / "eval_chroma_db"

    if db_dir.exists():
        shutil.rmtree(db_dir, ignore_errors=True)

    parser = VaultParser(str(vault_dir))
    notes = parser.parse_vault()

    chunker = MarkdownChunker(max_chunk_size=700)
    chunks = []
    for note in notes.values():
        chunks.extend(chunker.chunk_note(note))

    embedder = LocalEmbedder()
    vector_store = ChromaVectorStore(persist_dir=str(db_dir), collection_name="eval_collection")
    vector_store.index_chunks(chunks, embedder)

    retriever = HybridRerankedRetriever(
        embedder=embedder,
        vector_store=vector_store,
        absolute_semantic_threshold=0.28,
        w_semantic=0.70,
        w_lexical=0.30
    )

    generator = LLMGenerator()

    yield retriever, generator

    if db_dir.exists():
        shutil.rmtree(db_dir, ignore_errors=True)


BENCHMARK_QUESTIONS = [
    ("What are the core learning paradigms of Machine Learning?", ["02_Machine_Learning_Fundamentals"]),
    ("How does self attention work in Transformers?", ["04_Transformer_Architecture"]),
    ("What is ChromaDB used for?", ["07_Vector_Databases"]),
    ("What are the limitations of pure Large Language Models?", ["05_Large_Language_Models"]),
    ("What is the role of backpropagation in deep neural networks?", ["03_Deep_Learning_and_Neural_Networks"]),
    ("What is Obsidian frontmatter metadata?", ["11_Obsidian_Knowledge_Management"]),
    ("How does sentence transformers generate embeddings?", ["12_Semantic_Search_and_Embeddings"]),
    ("What is the minimum similarity threshold guardrail?", ["15_Evaluation_and_Hallucination_Guardrails"]),
    ("What is the agentic loop in AI agent frameworks?", ["10_AI_Agent_Frameworks"])
]


def test_10_benchmark_questions(setup_eval_env):
    retriever, generator = setup_eval_env
    passed_count = 0

    for query, expected_notes in BENCHMARK_QUESTIONS:
        res = retriever.retrieve(query, top_k_candidate_pool=10, top_k_final=3)
        retrieved_note_names = [c.note_name for c in res.primary_chunks]
        
        match = any(exp in retrieved_note_names for exp in expected_notes)
        assert match, f"Query '{query}' failed to retrieve expected notes {expected_notes}. Got: {retrieved_note_names}"
        
        answer = generator.generate_answer(query, res.primary_chunks)
        assert len(answer) > 20
        passed_count += 1

    assert passed_count == len(BENCHMARK_QUESTIONS)


def test_adversarial_out_of_domain(setup_eval_env):
    """Adversarial Test: Out-of-domain question with no note coverage."""
    retriever, generator = setup_eval_env
    query = "How do underwater volcanoes influence deep-sea submarine navigation?"
    
    res = retriever.retrieve(query)
    assert res.has_relevant_info is False
    assert len(res.primary_chunks) == 0

    answer = generator.generate_answer(query, res.primary_chunks)
    assert "No relevant information found" in answer
