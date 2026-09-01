import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Ensure root is on sys.path
root_dir = Path(__file__).parent.parent
sys.path.insert(0, str(root_dir))

load_dotenv()

from src.vault_parser import VaultParser
from src.chunker import MarkdownChunker
from src.embedder import LocalEmbedder
from src.vector_store import ChromaVectorStore


def main():
    vault_path = sys.argv[1] if len(sys.argv) > 1 else "./sample_vault"
    persist_dir = os.getenv("CHROMA_DB_DIR", "./chroma_db")

    print(f"🚀 Initializing Knowledge Base Indexer...")
    print(f"📁 Target Vault: {vault_path}")
    print(f"💾 Vector Storage Path: {persist_dir}")

    parser = VaultParser(vault_path)
    notes = parser.parse_vault()
    print(f"📄 Parsed {len(notes)} Markdown files.")

    chunker = MarkdownChunker(max_chunk_size=800, min_chunk_size=50)
    all_chunks = []
    for note in notes.values():
        chunks = chunker.chunk_note(note)
        all_chunks.extend(chunks)

    print(f"🧩 Created {len(all_chunks)} structure-aware chunks.")

    embedder = LocalEmbedder()
    vector_store = ChromaVectorStore(persist_dir=persist_dir)

    print(f"⚡ Embedding & Indexing chunks into ChromaDB...")
    vector_store.index_chunks(all_chunks, embedder)

    stats = vector_store.get_stats()
    print(f"\n✅ Indexing Complete!")
    print(f"📊 Total Files Indexed: {stats['total_files']}")
    print(f"📊 Total Vector Chunks: {stats['total_chunks']}")


if __name__ == "__main__":
    main()
