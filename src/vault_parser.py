import os
import re
import hashlib
from pathlib import Path
from typing import Dict, List, Set, Optional, Tuple
from dataclasses import dataclass, field
import frontmatter


@dataclass
class NoteMetadata:
    filepath: str
    file_name: str
    note_name: str
    title: str
    file_hash: str
    frontmatter: Dict = field(default_factory=dict)
    tags: Set[str] = field(default_factory=set)
    raw_content: str = ""
    full_content: str = ""


class VaultParser:
    """
    Structure-aware Obsidian Vault Parser.
    Extracts YAML frontmatter, inline tags, titles, and SHA256 hashes directly from local Obsidian Vault directories.
    Includes directory exclusion rules to prevent indexing generated application data or .obsidian settings.
    """

    BODY_TAG_REGEX = re.compile(r'(?<![A-Za-z0-9_#])#([a-zA-Z0-9_\-\/]+)')
    
    # Exclude system/generated application directories & .obsidian settings
    EXCLUDED_DIRS = {
        ".obsidian", ".git", ".chroma_db", ".pytest_cache", ".agents", "__pycache__", 
        "venv", ".venv", ".rag_index", "node_modules", "brain"
    }

    def __init__(self, vault_dir: Optional[str] = None):
        self.vault_dir = Path(vault_dir) if vault_dir else None
        self.notes: Dict[str, NoteMetadata] = {}

    @staticmethod
    def detect_obsidian_vault(candidate_dir: str) -> Tuple[bool, str]:
        """
        Detects whether a candidate local directory is an Obsidian vault.
        Returns (is_vault: bool, detection_reason: str).
        """
        path = Path(candidate_dir)
        if not path.exists() or not path.is_dir():
            return False, "Directory does not exist"

        has_obsidian_folder = (path / ".obsidian").is_dir()
        
        # Check if Markdown files exist (excluding system dirs)
        md_count = 0
        for root, dirs, files in os.walk(path):
            dirs[:] = [d for d in dirs if d not in VaultParser.EXCLUDED_DIRS and not d.startswith(".")]
            for f in files:
                if f.endswith(".md"):
                    md_count += 1
                    if md_count >= 1:
                        break
            if md_count >= 1:
                break

        if md_count == 0:
            return False, "No Markdown notes found in directory"

        if has_obsidian_folder:
            return True, f"🟢 Obsidian Vault Detected (`.obsidian/` found, {md_count}+ notes)"
        else:
            return True, f"🟢 Markdown Vault Detected ({md_count}+ notes found)"

    def parse_vault(self, target_dir: Optional[str] = None) -> Dict[str, NoteMetadata]:
        """
        Parses all .md files in the specified vault directory, excluding system/generated folders.
        """
        dir_to_parse = Path(target_dir) if target_dir else self.vault_dir
        if not dir_to_parse or not dir_to_parse.exists():
            raise FileNotFoundError(f"Vault directory not found: {dir_to_parse}")

        self.notes.clear()

        # Walk directory with exclusion guards
        for root, dirs, files in os.walk(dir_to_parse):
            # Exclude unwanted directories in-place
            dirs[:] = [d for d in dirs if d not in self.EXCLUDED_DIRS and not d.startswith(".")]

            for file in files:
                if file.endswith(".md"):
                    full_path = Path(root) / file
                    metadata = self.parse_note(full_path)
                    self.notes[metadata.file_name] = metadata

        return self.notes

    def parse_note(self, filepath: Path) -> NoteMetadata:
        """
        Parses a single Markdown note file with metadata and SHA256 file hash computation.
        """
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            content_str = f.read()

        file_hash = hashlib.sha256(content_str.encode('utf-8')).hexdigest()

        try:
            post = frontmatter.loads(content_str)
            fm_data = post.metadata
            body_content = post.content
        except Exception:
            fm_data = {}
            body_content = content_str

        file_name = filepath.name
        note_stem = filepath.stem
        title = fm_data.get("title", note_stem)

        tags: Set[str] = set()
        fm_tags = fm_data.get("tags", [])
        if isinstance(fm_tags, list):
            tags.update(str(t).strip("#") for t in fm_tags)
        elif isinstance(fm_tags, str):
            tags.update(t.strip("#") for t in fm_tags.split(","))

        body_tags = self.BODY_TAG_REGEX.findall(body_content)
        for bt in body_tags:
            if not bt.isdigit():
                tags.add(bt)

        return NoteMetadata(
            filepath=str(filepath),
            file_name=file_name,
            note_name=note_stem,
            title=title,
            file_hash=file_hash,
            frontmatter=fm_data,
            tags=tags,
            raw_content=body_content,
            full_content=content_str
        )


# Export module-level helper function
detect_obsidian_vault = VaultParser.detect_obsidian_vault

