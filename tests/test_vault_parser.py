import pytest
from pathlib import Path
from src.vault_parser import VaultParser, NoteMetadata


def test_parse_sample_vault():
    vault_dir = Path(__file__).parent.parent / "sample_vault"
    assert vault_dir.exists(), "sample_vault directory must exist"

    parser = VaultParser(str(vault_dir))
    notes = parser.parse_vault()

    assert len(notes) >= 15, "Should parse at least 15 notes"
    
    first_key = list(notes.keys())[0]
    note1 = notes[first_key]
    assert note1.file_name.endswith(".md")
    assert len(note1.file_hash) == 64  # SHA256 hex string length
    assert len(note1.raw_content) > 0


def test_single_file_parsing():
    vault_dir = Path(__file__).parent.parent / "sample_vault"
    md_files = list(vault_dir.rglob("*.md"))
    assert len(md_files) > 0

    parser = VaultParser()
    note = parser.parse_note(md_files[0])
    assert note.file_name == md_files[0].name
    assert note.file_hash is not None
