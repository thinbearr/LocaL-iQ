import os
from typing import List, Dict, Any, Optional, Set
import chromadb
from src.chunker import Chunk, MarkdownChunker
from src.embedder import LocalEmbedder
from src.vault_parser import NoteMetadata


class ChromaVectorStore:
    """
    Persistent ChromaDB Vector Store for direct Obsidian Vault synchronization and multi-vault management.
    Supports vault directory syncing, incremental hash updates, file deletion, and logical vault scope filtering.
    """

    def __init__(self, persist_dir: Optional[str] = None, collection_name: str = "obsidian_chunks"):
        self.persist_dir = persist_dir or os.getenv("CHROMA_DB_DIR", "./chroma_db")
        os.makedirs(self.persist_dir, exist_ok=True)
        
        self.client = chromadb.PersistentClient(path=self.persist_dir)
        self.collection_name = collection_name
        self.collection = self.client.get_or_create_collection(
            name=self.collection_name,
            metadata={"hnsw:space": "cosine"}
        )

    def clear(self):
        """Resets the collection."""
        try:
            self.client.delete_collection(self.collection_name)
        except Exception:
            pass
        self.collection = self.client.get_or_create_collection(
            name=self.collection_name,
            metadata={"hnsw:space": "cosine"}
        )

    def delete_file(self, file_name: str, vault_name: str = ""):
        """Removes all chunks associated with a specific file_name."""
        try:
            where_clause = {"file_name": file_name}
            if vault_name:
                where_clause = {"$and": [{"file_name": file_name}, {"vault_name": vault_name}]}
            self.collection.delete(where=where_clause)
        except Exception as e:
            print(f"[ChromaVectorStore] Error deleting file `{file_name}`: {e}")

    def index_chunks(self, chunks: List[Chunk], embedder: LocalEmbedder, file_hash: str = "", vault_name: str = "Default"):
        """
        Embeds and stores chunks additively into ChromaDB with rich metadata and vault isolation.
        """
        if not chunks:
            return

        ids = [f"{vault_name}_{c.chunk_id}" for c in chunks]
        texts = [f"{c.heading}\n{c.text}" for c in chunks]
        
        metadatas = []
        for c in chunks:
            metadatas.append({
                "file_name": c.file_name,
                "note_name": c.note_name,
                "heading": c.heading,
                "text": c.text,
                "tags": ",".join(c.tags),
                "chunk_index": c.chunk_index,
                "prev_chunk_id": c.prev_chunk_id or "",
                "next_chunk_id": c.next_chunk_id or "",
                "file_hash": file_hash,
                "vault_name": vault_name
            })

        embeddings = embedder.encode_texts(texts)

        # Batch upsert
        batch_size = 100
        for i in range(0, len(chunks), batch_size):
            self.collection.upsert(
                ids=ids[i:i + batch_size],
                embeddings=embeddings[i:i + batch_size],
                metadatas=metadatas[i:i + batch_size],
                documents=texts[i:i + batch_size]
            )

    def sync_with_vault_notes(
        self,
        notes: Dict[str, NoteMetadata],
        embedder: LocalEmbedder,
        chunker: MarkdownChunker,
        vault_name: str = "Default"
    ) -> Dict[str, int]:
        """
        Synchronizes ChromaDB directly with an Obsidian Vault directory:
        1. Deletes chunks for files removed from disk.
        2. Indexes new or modified files (detected via SHA256 hash mismatch).
        3. Leaves unchanged files untouched.
        """
        indexed_metadatas = self.get_indexed_file_hashes(vault_name=vault_name)
        disk_filenames = set(notes.keys())
        indexed_filenames = set(indexed_metadatas.keys())

        # 1. Purge deleted files
        deleted_files = indexed_filenames - disk_filenames
        for df in deleted_files:
            self.delete_file(df, vault_name=vault_name)

        added_count = 0
        updated_count = 0
        unchanged_count = 0

        # 2. Add or Update disk files
        for fname, nmeta in notes.items():
            existing_hash = indexed_metadatas.get(fname)

            if existing_hash is None:
                # New file
                chunks = chunker.chunk_note(nmeta)
                self.index_chunks(chunks, embedder, file_hash=nmeta.file_hash, vault_name=vault_name)
                added_count += 1
            elif existing_hash != nmeta.file_hash:
                # Modified file - re-index
                self.delete_file(fname, vault_name=vault_name)
                chunks = chunker.chunk_note(nmeta)
                self.index_chunks(chunks, embedder, file_hash=nmeta.file_hash, vault_name=vault_name)
                updated_count += 1
            else:
                unchanged_count += 1

        return {
            "added": added_count,
            "updated": updated_count,
            "deleted": len(deleted_files),
            "unchanged": unchanged_count,
            "total_disk": len(disk_filenames)
        }

    def get_indexed_file_hashes(self, vault_name: str = "") -> Dict[str, str]:
        """Returns a mapping of file_name -> file_hash for all indexed files in a vault."""
        where_clause = {"vault_name": vault_name} if vault_name else None
        res = self.collection.get(where=where_clause, include=["metadatas"])
        if not res or not res["metadatas"]:
            return {}

        file_hashes: Dict[str, str] = {}
        for meta in res["metadatas"]:
            fname = meta.get("file_name")
            fhash = meta.get("file_hash", "")
            if fname and fname not in file_hashes:
                file_hashes[fname] = fhash

        return file_hashes

    def get_chunk_by_id(self, chunk_id: str) -> Optional[Dict[str, Any]]:
        """Fetches a specific chunk by chunk_id."""
        if not chunk_id:
            return None
        res = self.collection.get(ids=[chunk_id], include=["metadatas", "documents"])
        if res and res["ids"] and len(res["ids"]) > 0:
            meta = res["metadatas"][0]
            doc = res["documents"][0]
            return {
                "chunk_id": chunk_id,
                "file_name": meta.get("file_name", ""),
                "note_name": meta.get("note_name", ""),
                "heading": meta.get("heading", ""),
                "text": meta.get("text", doc),
                "tags": meta.get("tags", "").split(",") if meta.get("tags") else [],
                "chunk_index": meta.get("chunk_index", 0),
                "prev_chunk_id": meta.get("prev_chunk_id", ""),
                "next_chunk_id": meta.get("next_chunk_id", ""),
                "vault_name": meta.get("vault_name", "Default")
            }
        return None

    def query_similar(
        self,
        query_embedding: List[float],
        top_k: int = 15,
        file_scope: Optional[List[str]] = None,
        vault_scope: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """
        Queries ChromaDB for vector similarity hits with multi-file and multi-vault logical scope filtering.
        Calculates raw cosine similarity: max(0.0, 1.0 - distance).
        """
        conditions = []
        if file_scope and len(file_scope) > 0:
            if len(file_scope) == 1:
                conditions.append({"file_name": file_scope[0]})
            else:
                conditions.append({"file_name": {"$in": file_scope}})

        if vault_scope and len(vault_scope) > 0:
            if len(vault_scope) == 1:
                conditions.append({"vault_name": vault_scope[0]})
            else:
                conditions.append({"vault_name": {"$in": vault_scope}})

        where_clause = None
        if len(conditions) == 1:
            where_clause = conditions[0]
        elif len(conditions) > 1:
            where_clause = {"$and": conditions}

        total_count = self.collection.count()
        if total_count == 0:
            return []

        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=min(top_k, max(1, total_count)),
            where=where_clause,
            include=["metadatas", "distances", "documents"]
        )

        output: List[Dict[str, Any]] = []
        if not results or not results["ids"] or not results["ids"][0]:
            return output

        ids = results["ids"][0]
        distances = results["distances"][0]
        metadatas = results["metadatas"][0]
        documents = results["documents"][0]

        for chunk_id, dist, meta, doc in zip(ids, distances, metadatas, documents):
            raw_cosine = max(0.0, min(1.0, 1.0 - dist))
            output.append({
                "chunk_id": chunk_id,
                "file_name": meta.get("file_name", ""),
                "note_name": meta.get("note_name", ""),
                "heading": meta.get("heading", ""),
                "text": meta.get("text", doc),
                "tags": meta.get("tags", "").split(",") if meta.get("tags") else [],
                "chunk_index": meta.get("chunk_index", 0),
                "prev_chunk_id": meta.get("prev_chunk_id", ""),
                "next_chunk_id": meta.get("next_chunk_id", ""),
                "vault_name": meta.get("vault_name", "Default"),
                "raw_cosine_similarity": round(raw_cosine, 4),
                "distance": dist
            })

        return output

    def get_indexed_files_registry(self, vault_name: str = "") -> List[Dict[str, Any]]:
        """Returns uniquely indexed files with chunk counts."""
        where_clause = {"vault_name": vault_name} if vault_name else None
        res = self.collection.get(where=where_clause, include=["metadatas"])
        if not res or not res["metadatas"]:
            return []

        file_counts: Dict[str, int] = {}
        for meta in res["metadatas"]:
            fname = meta.get("file_name", "unknown.md")
            file_counts[fname] = file_counts.get(fname, 0) + 1

        registry = []
        for fname, count in sorted(file_counts.items()):
            registry.append({
                "file_name": fname,
                "chunk_count": count
            })

        return registry

    def get_vault_stats(self, vault_name: str) -> Dict[str, Any]:
        """Returns chunk and file counts for a specific vault."""
        res = self.collection.get(where={"vault_name": vault_name}, include=["metadatas"])
        if not res or not res["metadatas"]:
            return {"total_files": 0, "total_chunks": 0}

        file_set = set(meta.get("file_name") for meta in res["metadatas"] if meta.get("file_name"))
        return {
            "total_files": len(file_set),
            "total_chunks": len(res["metadatas"])
        }

    def get_stats(self) -> Dict[str, Any]:
        """Returns overall storage metrics."""
        count = self.collection.count()
        registry = self.get_indexed_files_registry()
        return {
            "total_chunks": count,
            "total_files": len(registry),
            "collection_name": self.collection_name,
            "persist_dir": self.persist_dir
        }
