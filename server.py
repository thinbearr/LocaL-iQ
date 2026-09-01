import os
import time
from pathlib import Path
from typing import List, Optional, Dict, Any
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv

load_dotenv()

from src.vault_parser import VaultParser, detect_obsidian_vault
from src.vault_discovery import ObsidianVaultDiscovery, VaultInfo
from src.chunker import MarkdownChunker
from src.embedder import LocalEmbedder
from src.vector_store import ChromaVectorStore
from src.retriever import HybridRerankedRetriever, RetrievalResult
from src.generator import GeminiLLMGenerator

app = Flask(__name__)
CORS(app)


class AppState:
    def __init__(self):
        self.persist_dir = os.getenv("CHROMA_DB_DIR", "./chroma_db")
        self.embedder = LocalEmbedder()
        self.vector_store = ChromaVectorStore(persist_dir=self.persist_dir)
        self.discovery = ObsidianVaultDiscovery()
        self.discovered_vaults: Dict[str, VaultInfo] = self.discovery.discover(force_rescan=False)
        
        sample_vault_path = str((Path.cwd() / "sample_vault").resolve())
        
        # Ensure sample_vault is present in discovered vaults for demo/cloud deployment
        if os.path.exists("./sample_vault") and sample_vault_path not in self.discovered_vaults:
            self.discovered_vaults[sample_vault_path] = VaultInfo(
                path=sample_vault_path,
                name="sample_vault",
                md_count=17,
                has_obsidian_dir=True,
            )
            
        if self.discovered_vaults:
            self.active_vault_path = list(self.discovered_vaults.keys())[0]
        else:
            self.active_vault_path = sample_vault_path
            
        self.last_sync_time = "Startup"
        self.chat_history: List[Dict[str, str]] = []
        
        # Hyperparameter Settings
        self.top_k_final = 5
        self.top_k_pool = 15
        self.w_semantic = 0.70
        self.w_lexical = 0.30
        self.raw_cosine_threshold = 0.28
        self.enable_query_expansion = False
        
        # Check if database is empty; if so, initialize/index demo knowledge base (sample_vault)
        current_stats = self.vector_store.get_stats()
        if current_stats["total_chunks"] == 0 and os.path.exists(self.active_vault_path):
            self.sync_active_vault()
        else:
            # Sync active vault on startup
            self.sync_active_vault()

    def sync_active_vault(self):
        if not os.path.exists(self.active_vault_path):
            return None
        vault_name = Path(self.active_vault_path).name
        parser = VaultParser(self.active_vault_path)
        chunker = MarkdownChunker(max_chunk_size=800, min_chunk_size=50)
        notes = parser.parse_vault()
        sres = self.vector_store.sync_with_vault_notes(notes, self.embedder, chunker, vault_name=vault_name)
        self.last_sync_time = time.strftime("%H:%M:%S")
        return sres


state = AppState()


@app.route("/health", methods=["GET"])
def health_check():
    """Health check endpoint for deployment monitoring and health probes."""
    return jsonify({"status": "healthy"}), 200


@app.route("/api/status", methods=["GET"])
def get_status():
    active_name = Path(state.active_vault_path).name
    is_vault, msg = detect_obsidian_vault(state.active_vault_path)
    v_stats = state.vector_store.get_vault_stats(active_name)
    total_stats = state.vector_store.get_stats()
    
    return jsonify({
        "active_vault_name": active_name,
        "active_vault_path": state.active_vault_path,
        "is_vault": is_vault,
        "detection_msg": msg,
        "active_files": v_stats["total_files"],
        "active_chunks": v_stats["total_chunks"],
        "total_files": total_stats["total_files"],
        "total_chunks": total_stats["total_chunks"],
        "last_sync_time": state.last_sync_time,
        "model_name": os.getenv("GEMINI_MODEL", "gemini-3.6-flash")
    })


@app.route("/api/vaults", methods=["GET"])
def get_vaults():
    vaults_list = []
    for p, vi in state.discovered_vaults.items():
        v_name = vi.name
        v_stats = state.vector_store.get_vault_stats(v_name)
        vaults_list.append({
            "path": p,
            "name": v_name,
            "md_count": vi.md_count,
            "chunk_count": v_stats["total_chunks"],
            "is_active": (p == state.active_vault_path)
        })
    return jsonify({"vaults": vaults_list})


@app.route("/api/vaults/select", methods=["POST"])
def select_vault():
    data = request.json or {}
    vault_path = data.get("vault_path")
    if not vault_path or not os.path.exists(vault_path):
        return jsonify({"error": "Vault folder not found"}), 404
        
    state.active_vault_path = vault_path
    sres = state.sync_active_vault()
    return jsonify({"status": "success", "active_vault": vault_path, "sync_res": sres})


@app.route("/api/vaults/rescan", methods=["POST"])
def rescan_vaults():
    state.discovered_vaults = state.discovery.discover(force_rescan=True)
    return get_vaults()


@app.route("/api/vaults/sync", methods=["POST"])
def sync_vault():
    sres = state.sync_active_vault()
    return jsonify({"status": "success", "sync_res": sres, "last_sync_time": state.last_sync_time})


@app.route("/api/documents", methods=["GET"])
def get_documents():
    vault_scope_type = request.args.get("vault_scope", "Current Vault")
    selected_vaults_raw = request.args.get("selected_vaults", "")
    selected_vaults = [v.strip() for v in selected_vaults_raw.split(",") if v.strip()]
    active_name = Path(state.active_vault_path).name

    documents = []
    if vault_scope_type == "Current Vault":
        documents = state.vector_store.get_indexed_files_registry(vault_name=active_name)
    elif vault_scope_type == "Selected Vaults" and selected_vaults:
        all_docs = []
        for vn in selected_vaults:
            docs = state.vector_store.get_indexed_files_registry(vault_name=vn)
            for d in docs:
                d["vault_name"] = vn
                all_docs.append(d)
        documents = all_docs
    else:  # All Vaults
        documents = state.vector_store.get_indexed_files_registry(vault_name="")

    return jsonify({"documents": documents, "vault_scope": vault_scope_type})


@app.route("/api/documents/<path:file_name>", methods=["DELETE"])
def delete_document(file_name):
    active_name = Path(state.active_vault_path).name
    state.vector_store.delete_file(file_name, vault_name=active_name)
    return jsonify({"status": "deleted", "file_name": file_name})


@app.route("/api/ask", methods=["POST"])
def ask_question():
    data = request.json or {}
    query = data.get("query", "").strip()
    if not query:
        return jsonify({"error": "Query cannot be empty"}), 400
        
    vault_scope_type = data.get("vault_scope", "Current Vault")
    selected_vaults = data.get("selected_vaults", [])
    
    active_name = Path(state.active_vault_path).name
    v_scope = None
    evaluated_vault_names = []
    summary_text = ""

    if vault_scope_type == "Current Vault":
        v_scope = [active_name]
        evaluated_vault_names = [active_name]
        summary_text = f"Current Vault ({active_name})"
    elif vault_scope_type == "Selected Vaults" and selected_vaults:
        v_scope = selected_vaults
        evaluated_vault_names = selected_vaults
        summary_text = f"{len(selected_vaults)} Vaults ({' · '.join(selected_vaults)})"
    else:
        v_scope = None
        all_v_names = [Path(p).name for p in state.discovered_vaults.keys()]
        evaluated_vault_names = all_v_names if all_v_names else [active_name]
        summary_text = f"All Vaults ({' · '.join(evaluated_vault_names)})"
        
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
        vault_scope=v_scope,
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
            "vault_name": getattr(c, "vault_name", active_name)
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
            "vault_name": getattr(c, "vault_name", active_name)
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
            "vault_scope_type": vault_scope_type,
            "evaluated_vault_names": evaluated_vault_names,
            "summary_text": summary_text
        }
    })


@app.route("/api/settings", methods=["GET", "POST"])
def settings_handler():
    if request.method == "GET":
        return jsonify({
            "top_k_final": state.top_k_final,
            "top_k_pool": state.top_k_pool,
            "w_semantic": state.w_semantic,
            "w_lexical": state.w_lexical,
            "raw_cosine_threshold": state.raw_cosine_threshold,
            "enable_query_expansion": state.enable_query_expansion,
            "persist_dir": state.persist_dir,
            "model_name": os.getenv("GEMINI_MODEL", "gemini-3.6-flash")
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
    app.run(host="127.0.0.1", port=5000, debug=False)
