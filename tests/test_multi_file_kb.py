import pytest
import shutil
from pathlib import Path
from src.vault_parser import VaultParser
from src.chunker import MarkdownChunker
from src.embedder import LocalEmbedder
from src.vector_store import ChromaVectorStore
from src.retriever import HybridRerankedRetriever


def test_multi_file_additive_indexing_and_deletion(tmp_path):
    db_dir = tmp_path / "test_kb_chroma"
    embedder = LocalEmbedder()
    vector_store = ChromaVectorStore(persist_dir=str(db_dir), collection_name="multi_file_test")

    # File A
    file_a = tmp_path / "Document_A.md"
    file_a.write_text("# Document A\n\nThis is content for Document A discussing neural networks.", encoding="utf-8")

    # File B
    file_b = tmp_path / "Document_B.md"
    file_b.write_text("# Document B\n\nThis is content for Document B discussing vector databases.", encoding="utf-8")

    parser = VaultParser()
    chunker = MarkdownChunker()

    # 1. Additive Indexing File A
    note_a = parser.parse_note(file_a)
    chunks_a = chunker.chunk_note(note_a)
    vector_store.index_chunks(chunks_a, embedder, file_hash=note_a.file_hash)

    stats1 = vector_store.get_stats()
    assert stats1["total_files"] == 1
    assert stats1["total_chunks"] == len(chunks_a)

    # 2. Additive Indexing File B
    note_b = parser.parse_note(file_b)
    chunks_b = chunker.chunk_note(note_b)
    vector_store.index_chunks(chunks_b, embedder, file_hash=note_b.file_hash)

    stats2 = vector_store.get_stats()
    assert stats2["total_files"] == 2
    assert stats2["total_chunks"] == len(chunks_a) + len(chunks_b)

    # 3. Scope Filtering Retrieval (Targeting Document B)
    retriever = HybridRerankedRetriever(embedder=embedder, vector_store=vector_store)
    res_b = retriever.retrieve("vector databases", file_scope=["Document_B.md"])
    assert res_b.has_relevant_info is True
    assert all(c.file_name == "Document_B.md" for c in res_b.primary_chunks)

    # 4. Delete File A
    vector_store.delete_file("Document_A.md")
    stats3 = vector_store.get_stats()
    assert stats3["total_files"] == 1
    assert stats3["total_chunks"] == len(chunks_b)
