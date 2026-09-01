import re
from typing import List, Dict, Set, Optional
from dataclasses import dataclass, field
from src.vault_parser import NoteMetadata


@dataclass
class Chunk:
    chunk_id: str
    file_name: str
    note_name: str
    heading: str
    text: str
    chunk_index: int
    tags: List[str] = field(default_factory=list)
    prev_chunk_id: Optional[str] = None
    next_chunk_id: Optional[str] = None


class MarkdownChunker:
    """
    Structure-aware Markdown chunker.
    Splits along headings (#, ##, ###) while preserving code blocks and attaching section breadcrumbs,
    document order indices, and bounded sibling pointers.
    """

    HEADING_REGEX = re.compile(r'^(#{1,6})\s+(.+)$', re.MULTILINE)

    def __init__(self, max_chunk_size: int = 800, min_chunk_size: int = 50):
        self.max_chunk_size = max_chunk_size
        self.min_chunk_size = min_chunk_size

    def chunk_note(self, note: NoteMetadata) -> List[Chunk]:
        """
        Chunks a single note metadata object into a list of Chunk objects with sibling pointers.
        """
        raw_text = note.raw_content
        if not raw_text.strip():
            return []

        sections = self._split_by_headings(raw_text, note.title)
        raw_chunks: List[tuple] = []  # (heading, text)

        for heading_path, section_text in sections:
            section_text = section_text.strip()
            if not section_text:
                continue

            sub_texts = self._split_section_text(section_text)
            for sub_text in sub_texts:
                if len(sub_text.strip()) < self.min_chunk_size and raw_chunks:
                    prev_h, prev_t = raw_chunks[-1]
                    raw_chunks[-1] = (prev_h, prev_t + "\n\n" + sub_text.strip())
                else:
                    raw_chunks.append((heading_path, sub_text.strip()))

        chunks: List[Chunk] = []
        total_chunks = len(raw_chunks)
        clean_note_id = re.sub(r'[^a-zA-Z0-9_]', '_', note.note_name)

        for idx, (heading_path, text_body) in enumerate(raw_chunks):
            chunk_id = f"{clean_note_id}_{idx}"
            prev_id = f"{clean_note_id}_{idx - 1}" if idx > 0 else None
            next_id = f"{clean_note_id}_{idx + 1}" if idx < total_chunks - 1 else None

            chunk = Chunk(
                chunk_id=chunk_id,
                file_name=note.file_name,
                note_name=note.note_name,
                heading=heading_path,
                text=text_body,
                chunk_index=idx,
                tags=list(note.tags),
                prev_chunk_id=prev_id,
                next_chunk_id=next_id
            )
            chunks.append(chunk)

        return chunks

    def _split_by_headings(self, text: str, default_title: str) -> List[tuple]:
        """
        Splits text by markdown headings and constructs heading path breadcrumbs.
        """
        lines = text.splitlines()
        sections: List[tuple] = []
        current_heading_stack: List[str] = [default_title]
        current_lines: List[str] = []

        for line in lines:
            match = self.HEADING_REGEX.match(line)
            if match:
                if current_lines:
                    heading_breadcrumb = " > ".join(current_heading_stack)
                    sections.append((heading_breadcrumb, "\n".join(current_lines)))
                    current_lines = []

                level = len(match.group(1))
                heading_title = match.group(2).strip()

                if level == 1:
                    current_heading_stack = [default_title, heading_title]
                else:
                    current_heading_stack = current_heading_stack[:level-1]
                    current_heading_stack.append(heading_title)
            else:
                current_lines.append(line)

        if current_lines:
            heading_breadcrumb = " > ".join(current_heading_stack)
            sections.append((heading_breadcrumb, "\n".join(current_lines)))

        return sections

    def _split_section_text(self, text: str) -> List[str]:
        """
        Splits section text into chunks <= max_chunk_size while respecting code blocks (```).
        """
        if len(text) <= self.max_chunk_size:
            return [text]

        parts = []
        code_block_pattern = re.compile(r'(```[\s\S]*?```)')
        blocks = code_block_pattern.split(text)

        current_chunk = ""

        for block in blocks:
            if block.startswith("```"):
                if len(current_chunk) + len(block) > self.max_chunk_size and current_chunk.strip():
                    parts.append(current_chunk)
                    current_chunk = block
                else:
                    current_chunk += ("\n\n" if current_chunk else "") + block
            else:
                paragraphs = block.split("\n\n")
                for para in paragraphs:
                    if not para.strip():
                        continue
                    if len(current_chunk) + len(para) > self.max_chunk_size and current_chunk.strip():
                        parts.append(current_chunk)
                        current_chunk = para
                    else:
                        current_chunk += ("\n\n" if current_chunk else "") + para

        if current_chunk.strip():
            parts.append(current_chunk)

        return parts
