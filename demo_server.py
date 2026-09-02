import os
import time
from pathlib import Path
from typing import List, Dict, Any
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv

# Force Gemini embeddings for the public demo BEFORE load_dotenv() or any src/ import.
# This is an unconditional override — no Render env variable (including an empty string)
# can cause get_embedder() to fall back to LocalEmbedder / SentenceTransformers / PyTorch.
os.environ["EMBEDDING_PROVIDER"] = "gemini"

load_dotenv()

from src.vault_parser import VaultParser, detect_obsidian_vault
from src.chunker import MarkdownChunker
from src.embedder import get_embedder
from src.vector_store import ChromaVectorStore
from src.retriever import HybridRerankedRetriever, RetrievalResult
from src.generator import GeminiLLMGenerator


app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})


@app.after_request
def add_cors_headers(response):
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
    return response


import threading


class DemoAppState:
    """
    Dedicated application state for public Render deployment mode.
    Operates strictly on the bundled repository `sample_vault/`.
    Completely isolated from local filesystem Obsidian discovery routines.
    """

    def __init__(self):
        self.sample_vault_path = str((Path.cwd() / "sample_vault").resolve())
        self.active_vault_path = self.sample_vault_path
        self.persist_dir = os.getenv("CHROMA_DB_DIR", "./chroma_db")
        self.embedder = get_embedder()
        self.vector_store = ChromaVectorStore(persist_dir=self.persist_dir)
        
        self.chat_history: List[Dict[str, str]] = []
        
        # Hyperparameter Settings
        self.top_k_final = 5
        self.top_k_pool = 15
        self.w_semantic = 0.70
        self.w_lexical = 0.30
        self.raw_cosine_threshold = 0.28
        self.enable_query_expansion = False

        self._indexing_lock = threading.Lock()
        self._is_indexed = False

        # Non-blocking startup check: if ChromaDB already has cached chunks, mark as indexed.
        # DO NOT call sync_sample_vault() synchronously during __init__ so Gunicorn can bind to $PORT immediately.
        current_stats = self.vector_store.get_stats()
        if current_stats["total_chunks"] > 0:
            self.last_sync_time = "Loaded from cache"
            self._is_indexed = True
        else:
            self.last_sync_time = "Not synced"
            self._is_indexed = False

    def ensure_indexed(self):
        """Lazy-indexes sample_vault on demand before retrieval if Chroma vector store is empty."""
        if not self._is_indexed:
            with self._indexing_lock:
                if not self._is_indexed:
                    current_stats = self.vector_store.get_stats()
                    if current_stats["total_chunks"] == 0 and os.path.exists(self.sample_vault_path):
                        self.sync_sample_vault()
                    else:
                        self.last_sync_time = "Loaded from cache"
                    self._is_indexed = True

    def sync_sample_vault(self):
        if not os.path.exists(self.sample_vault_path):
            return None
        vault_name = "sample_vault"
        parser = VaultParser(self.sample_vault_path)
        chunker = MarkdownChunker(max_chunk_size=800, min_chunk_size=50)
        notes = parser.parse_vault()
        sres = self.vector_store.sync_with_vault_notes(notes, self.embedder, chunker, vault_name=vault_name)
        self.last_sync_time = time.strftime("%H:%M:%S")
        self._is_indexed = True
        return sres


# Eagerly initialize application state at server startup (module load time)
# Module import takes < 10ms so Gunicorn opens the HTTP socket immediately
_state = DemoAppState()


def get_state() -> DemoAppState:
    """Returns pre-initialized DemoAppState instance instantly without request-time indexing."""
    global _state
    if _state is None:
        _state = DemoAppState()
    return _state


@app.route("/health", methods=["GET"])
def health_check():
    """Lightweight health check probe for public deployment monitoring."""
    return jsonify({"status": "healthy", "mode": "public-demo"}), 200


@app.route("/api/status", methods=["GET"])
def get_status():
    state = get_state()
    active_name = "sample_vault"
    is_vault, msg = detect_obsidian_vault(state.sample_vault_path)
    v_stats = state.vector_store.get_vault_stats(active_name)
    total_stats = state.vector_store.get_stats()
    
    return jsonify({
        "active_vault_name": active_name,
        "active_vault_path": state.sample_vault_path,
        "is_vault": is_vault,
        "detection_msg": msg,
        "active_files": v_stats["total_files"],
        "active_chunks": v_stats["total_chunks"],
        "total_files": total_stats["total_files"],
        "total_chunks": total_stats["total_chunks"],
        "last_sync_time": state.last_sync_time,
        "model_name": os.getenv("GEMINI_MODEL", "gemini-3.5-flash"),
        "mode": "public-demo"
    })


@app.route("/api/vaults", methods=["GET"])
def get_vaults():
    state = get_state()
    v_stats = state.vector_store.get_vault_stats("sample_vault")
    
    md_count = 0
    if os.path.exists(state.sample_vault_path):
        for root, _, files in os.walk(state.sample_vault_path):
            md_count += sum(1 for f in files if f.endswith(".md"))
            
    vaults_list = [{
        "path": state.sample_vault_path,
        "name": "sample_vault",
        "md_count": md_count or 17,
        "chunk_count": v_stats["total_chunks"],
        "is_active": True
    }]
    return jsonify({"vaults": vaults_list})


@app.route("/api/vaults/select", methods=["POST"])
def select_vault():
    state = get_state()
    sres = state.sync_sample_vault()
    return jsonify({"status": "success", "active_vault": state.sample_vault_path, "sync_res": sres})


@app.route("/api/vaults/rescan", methods=["POST"])
def rescan_vaults():
    state = get_state()
    state.sync_sample_vault()
    return get_vaults()


@app.route("/api/vaults/sync", methods=["POST"])
def sync_vault():
    state = get_state()
    sres = state.sync_sample_vault()
    return jsonify({"status": "success", "sync_res": sres, "last_sync_time": state.last_sync_time})


@app.route("/api/documents", methods=["GET"])
def get_documents():
    state = get_state()
    documents = state.vector_store.get_indexed_files_registry(vault_name="sample_vault")
    return jsonify({"documents": documents, "vault_scope": "sample_vault"})


@app.route("/api/documents/<path:file_name>", methods=["DELETE"])
def delete_document(file_name):
    state = get_state()
    state.vector_store.delete_file(file_name, vault_name="sample_vault")
    return jsonify({"status": "deleted", "file_name": file_name})


@app.route("/api/ask", methods=["POST"])
def ask_question():
    state = get_state()
    state.ensure_indexed()
    data = request.json or {}
    query = data.get("query", "").strip()
    if not query:
        return jsonify({"error": "Query cannot be empty"}), 400
        
    retriever = HybridRerankedRetriever(
        embedder=state.embedder,
        vector_store=state.vector_store,
        absolute_semantic_threshold=state.raw_cosine_threshold,
        w_semantic=state.w_semantic,
        w_lexical=state.w_lexical
    )
    
    res: RetrievalResult = retriever.retrieve(
        user_query=query,
        chat_history=state.chat_history,
        vault_scope=["sample_vault"],
        top_k_candidate_pool=state.top_k_pool,
        top_k_final=state.top_k_final,
        enable_query_expansion=state.enable_query_expansion
    )
    
    generator = GeminiLLMGenerator()
    answer = generator.generate_answer(query, res.primary_chunks)
    
    state.chat_history.append({"user": query, "assistant": answer})
    
    primary_chunks_data = []
    for c in res.primary_chunks:
        primary_chunks_data.append({
            "chunk_id": c.chunk_id,
            "file_name": c.file_name,
            "heading": c.heading,
            "text": c.text,
            "raw_semantic_score": c.raw_semantic_score,
            "lexical_bm25_score": c.lexical_bm25_score,
            "hybrid_score": c.hybrid_score,
            "tags": c.tags,
            "vault_name": getattr(c, "vault_name", "sample_vault")
        })

    candidates_data = []
    for c in res.all_candidates_evaluated:
        candidates_data.append({
            "rank": c.rank,
            "selected": c.selected,
            "file_name": c.file_name,
            "heading": c.heading,
            "raw_semantic_score": c.raw_semantic_score,
            "lexical_bm25_score": c.lexical_bm25_score,
            "hybrid_score": c.hybrid_score,
            "vault_name": getattr(c, "vault_name", "sample_vault")
        })
        
    return jsonify({
        "user_query": query,
        "resolved_query": res.resolved_query,
        "expanded_query": res.expanded_query,
        "answer": answer,
        "has_relevant_info": res.has_relevant_info,
        "primary_chunks": primary_chunks_data,
        "all_candidates": candidates_data,
        "max_raw_semantic": res.max_raw_semantic_score,
        "max_hybrid_score": res.max_hybrid_score,
        "latency_ms": res.retrieval_latency_ms,
        "files_contributed": res.files_contributed,
        "scope_info": {
            "vault_scope_type": "Public Demo Vault",
            "evaluated_vault_names": ["sample_vault"],
            "summary_text": "Public Demo Vault (sample_vault)"
        }
    })


@app.route("/api/settings", methods=["GET", "POST"])
def settings_handler():
    state = get_state()
    if request.method == "GET":
        return jsonify({
            "top_k_final": state.top_k_final,
            "top_k_pool": state.top_k_pool,
            "w_semantic": state.w_semantic,
            "w_lexical": state.w_lexical,
            "raw_cosine_threshold": state.raw_cosine_threshold,
            "enable_query_expansion": state.enable_query_expansion,
            "persist_dir": state.persist_dir,
            "model_name": os.getenv("GEMINI_MODEL", "gemini-3.5-flash")
        })
    else:
        data = request.json or {}
        if "top_k_final" in data:
            state.top_k_final = int(data["top_k_final"])
        if "top_k_pool" in data:
            state.top_k_pool = int(data["top_k_pool"])
        if "w_semantic" in data:
            state.w_semantic = float(data["w_semantic"])
            state.w_lexical = round(1.0 - state.w_semantic, 2)
        if "raw_cosine_threshold" in data:
            state.raw_cosine_threshold = float(data["raw_cosine_threshold"])
        if "enable_query_expansion" in data:
            state.enable_query_expansion = bool(data["enable_query_expansion"])
        if "persist_dir" in data and data["persist_dir"] != state.persist_dir:
            state.persist_dir = data["persist_dir"]
            state.vector_store = ChromaVectorStore(persist_dir=state.persist_dir)
        return settings_handler()


if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
