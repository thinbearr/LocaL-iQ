import pytest
from pathlib import Path
from src.vault_parser import VaultParser
from src.chunker import MarkdownChunker


def test_markdown_chunker_structure_and_siblings():
    vault_dir = Path(__file__).parent.parent / "sample_vault"
    parser = VaultParser(str(vault_dir))
    notes = parser.parse_vault()

    chunker = MarkdownChunker(max_chunk_size=500, min_chunk_size=30)
    first_note = list(notes.values())[0]
    chunks = chunker.chunk_note(first_note)

    assert len(chunks) > 0
    for idx, chunk in enumerate(chunks):
        assert chunk.file_name == first_note.file_name
        assert chunk.note_name == first_note.note_name
        assert chunk.heading != ""
        assert chunk.chunk_index == idx
        if idx > 0:
            assert chunk.prev_chunk_id is not None
        if idx < len(chunks) - 1:
            assert chunk.next_chunk_id is not None
