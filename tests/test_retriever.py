import pytest
import os
import shutil
from pathlib import Path
from src.vault_parser import VaultParser
from src.chunker import MarkdownChunker
from src.embedder import LocalEmbedder
from src.vector_store import ChromaVectorStore
from src.retriever import HybridRerankedRetriever


@pytest.fixture(scope="module")
def setup_test_retriever():
    vault_dir = Path(__file__).parent.parent / "sample_vault"
    test_db_dir = Path(__file__).parent / "tmp_chroma_db"

    if test_db_dir.exists():
        shutil.rmtree(test_db_dir, ignore_errors=True)

    parser = VaultParser(str(vault_dir))
    notes = parser.parse_vault()

    chunker = MarkdownChunker(max_chunk_size=600)
    all_chunks = []
    for note in notes.values():
        all_chunks.extend(chunker.chunk_note(note))

    embedder = LocalEmbedder()
    vector_store = ChromaVectorStore(persist_dir=str(test_db_dir), collection_name="test_collection")
    vector_store.index_chunks(all_chunks, embedder)

    retriever = HybridRerankedRetriever(
        embedder=embedder,
        vector_store=vector_store,
        absolute_semantic_threshold=0.28,
        w_semantic=0.70,
        w_lexical=0.30
    )

    yield retriever

    if test_db_dir.exists():
        shutil.rmtree(test_db_dir, ignore_errors=True)


def test_hybrid_retrieval(setup_test_retriever):
    retriever = setup_test_retriever
    res = retriever.retrieve("What is self attention in Transformer?", top_k_candidate_pool=10, top_k_final=3)
    assert res.has_relevant_info is True
    assert len(res.primary_chunks) > 0
    assert res.max_raw_semantic_score >= 0.28
    first_hit = res.primary_chunks[0]
    assert first_hit.raw_semantic_score > 0.0
    assert first_hit.hybrid_score > 0.0


def test_absolute_semantic_evidence_gate(setup_test_retriever):
    retriever = setup_test_retriever
    # Adversarial out-of-domain query
    res = retriever.retrieve("What is the recipe for quantum banana bread on Mars?")
    assert res.has_relevant_info is False
    assert len(res.primary_chunks) == 0


def test_conversational_query_resolution(setup_test_retriever):
    retriever = setup_test_retriever
    chat_history = [
        {"user": "What is RAG?", "assistant": "RAG stands for Retrieval-Augmented Generation using vector databases."}
    ]
    resolved = retriever.resolve_conversational_query("What database does it use?", chat_history)
    assert "RAG" in resolved or "Generation" in resolved
