# LocaL-iQ — Your Knowledge, Understood.

LocaL-iQ is a production-oriented, local Obsidian RAG application built with a modern **React + Vite** frontend and a **Python REST API** backend powered by ChromaDB and Google Gemini.

---

## 🚀 System Architecture

```text
 ┌─────────────────────────────────────────────────────────────────────────┐
 │                       React + Vite Frontend (Port 5173)                 │
 │  Anthropic Serif Display Typography · Perplexity Sans UI · Dark Mode   │
 └────────────────────────────────────┬────────────────────────────────────┘
                                      │ REST API (CORS)
                                      ▼
 ┌─────────────────────────────────────────────────────────────────────────┐
 │                       Python Flask REST Server (Port 5000)              │
 ├─────────────────────────────────────────────────────────────────────────┤
 │  Obsidian Vault Parser  ──►  Structure-Aware Chunker  ──►  Local Embeds │
 │                                                                         │
 │  Two-Stage Hybrid Retrieval: Dense Vector Search + Lexical BM25 Rerank  │
 │  Raw Cosine Evidence Gate (>= 0.28)  ──►  Google Gemini (gemini-3.6)    │
 └─────────────────────────────────────────────────────────────────────────┘
```

---

## 🛠️ How to Run

### 1. Start Python REST Backend Server
```bash
python server.py
```
*(Runs on http://127.0.0.1:5000)*

### 2. Start React + Vite Frontend
```bash
cd frontend
npm run dev
```
*(Runs on http://localhost:5173)*

---

## 🧪 Automated Testing
```bash
python -m pytest tests/ -v
```
*(Runs full test suite covering chunker, parser, vector store, hybrid retriever, and evidence gates)*
