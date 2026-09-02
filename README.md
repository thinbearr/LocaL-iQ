# LocaL-iQ

**Your knowledge, understood.**

LocaL-iQ is a production-oriented, local-first **Retrieval-Augmented Generation (RAG) knowledge assistant for Obsidian Markdown vaults**. It enables users to connect their local Obsidian vaults and ask questions grounded strictly in their own personal notes, featuring two-stage hybrid retrieval, an anti-hallucination evidence gate, and an interactive retrieval trajectory inspector.

---

## ⚡ What it does

LocaL-iQ turns unstructured Obsidian notes into a grounded, interactive knowledge engine:

* **Automated Vault Discovery**: Automatically scans user-accessible directories for folders containing an `.obsidian/` directory and valid Markdown notes.
* **Multi-Vault Support**: Supports detecting, managing, and retrieving across multiple Obsidian vaults simultaneously.
* **Granular Search Scope**: Choose between **Current Vault** (active managed vault), **Selected Vaults** (checkbox multi-selection), or **All Vaults** (entire discovered knowledge base).
* **Incremental Synchronization**: Automatically tracks new, modified, and deleted Markdown files, updating the ChromaDB vector store additively without re-indexing unchanged files.
* **Markdown Parsing & Structure-Aware Chunking**: Preserves Markdown heading hierarchies, bullet lists, tags, and code blocks while chunking text into semantically cohesive passages with sibling context linkage.
* **Two-Stage Hybrid Retrieval**: Combines dense vector search (`all-MiniLM-L6-v2` with HNSW cosine similarity) and lexical BM25 reranking (`rank_bm25`).
* **Raw Cosine Semantic Evidence Gate**: Filters candidate passages using an absolute raw cosine similarity threshold (default `0.28`) prior to lexical reranking to prevent low-relevance noise from entering the context.
* **Bounded Sibling & Heading Context**: Automatically incorporates immediate sibling chunks (previous/next adjacent paragraphs) and parent heading context to maintain complete semantic clarity.
* **Conversation-Aware RAG**: Resolves follow-up questions and conversational pronouns in multi-turn chat sessions.
* **Citation-Aware Answers**: Generates grounded answers using Google Gemini with explicit source file and section citations.
* **Retrieval Inspector**: Developer and user transparency view showing candidate pool ranking, raw cosine scores, BM25 scores, hybrid fusion scores, and evidence selection.
* **Anti-Hallucination Guardrail**: Returns a strict fallback message when no retrieved evidence satisfies the relevance threshold.
* **Gemini-Powered Generation**: Leverages Google Gemini (`gemini-3.5-flash-lite`) for precise, grounded synthesis.

---

## 🏗️ RAG Architecture

```text
               Obsidian Vault (.md files)
                           ↓
                   Vault Discovery
                           ↓
                   Markdown Parsing
                           ↓
              Structure-Aware Chunking
                           ↓
                Local Embeddings (MiniLM)
                           ↓
               ChromaDB Vector Store
                           ↓
             Semantic Candidate Retrieval
                           ↓
               Raw Cosine Evidence Gate
                           ↓
                BM25 / Lexical Reranking
                           ↓
                     Final Top-K
                           ↓
          Bounded Sibling & Heading Context
                           ↓
                    Grounded Prompt
                           ↓
                     Google Gemini
                           ↓
                  Answer + Citations
```

### Raw Cosine Evidence Gate
Before lexical reranking occurs, every candidate chunk retrieved via dense vector search must pass an absolute **raw cosine similarity threshold** (configurable in Settings, default `0.28`). If candidate chunks do not meet this threshold, they are discarded prior to BM25 fusion, ensuring ungrounded or low-relevance passages never reach the LLM context window.

---

## 🗂️ Multi-Vault Retrieval

LocaL-iQ cleanly distinguishes between managing a vault and querying across vaults:

* **Active Vault**: The currently active and managed vault used for single-vault management actions (such as manual force re-indexing).
* **Search Scope**: Controls which vaults participate in retrieval queries:
  * **Current Vault**: Restricts search exclusively to the active vault.
  * **Selected Vaults**: Allows selecting multiple vaults simultaneously using sidebar checkboxes (e.g. `IDEX` + `sample_vault`).
  * **All Vaults**: Queries across all discovered Obsidian vaults on the local machine.

---

## 🔄 Incremental Synchronization

LocaL-iQ performs additive, diff-based indexing on vault updates:

* **New Markdown Files**: Automatically detected, parsed, embedded, and added to the index.
* **Modified Markdown Files**: Stale chunk embeddings are deleted and re-indexed.
* **Deleted Markdown Files**: Associated vector embeddings and metadata are removed from ChromaDB.
* **Unchanged Files**: Skipped during sync for near-instant updates.

*Note: Internal Obsidian metadata directories (`.obsidian/`) are strictly excluded from indexing.*

---

## 🛡️ Anti-Hallucination / Grounding

LocaL-iQ is engineered for strict factuality and zero speculation. When no retrieved evidence passes the raw cosine evidence gate or satisfies the query intent, the application suppresses generation and returns exactly:

> **“No relevant information found in the vault.”**

The model is constrained strictly to the provided retrieved context and will not hallucinate answers from pre-trained parametric memory when vault evidence is absent.

---

## 🔍 Retrieval Inspector

The **Retrieval Inspector** tab provides full transparency into the retrieval and ranking pipeline:

* **Trajectory Flow**: Visualizes pipeline stages from dense retrieval to LLM generation.
* **Candidate Pool Scoring Matrix**: Displays all candidate chunks alongside their source vault, filename, section heading, raw cosine similarity score, BM25 lexical score, hybrid score, and selection status.
* **Evaluated Search Scope**: Displays the exact vault scope evaluated for the active query.

---

## 💻 Technology Stack

### Frontend
* **React 19**: Modern component-based single-page application.
* **Vite 8**: High-performance frontend dev server and bundler.
* **Vanilla CSS**: Custom design system with CSS variables, exclusive dark theme (`#0B0E14`), and luminous teal accents (`#00A896`).
* **Google Fonts**: `Newsreader` (Anthropic/Claude-inspired serif headings), `Roboto` (UI typography), `JetBrains Mono` (technical metadata).

### Backend
* **Python 3.12**: Core runtime environment.
* **Flask 3.1 & Flask-CORS**: Lightweight REST API server exposing vault management and retrieval endpoints.

### RAG & Vector Storage
* **ChromaDB**: Embedded vector database utilizing HNSW index with cosine similarity.
* **Sentence-Transformers**: `sentence-transformers/all-MiniLM-L6-v2` for local 384-dimensional dense vector embeddings.
* **Rank-BM25**: `BM25Okapi` implementation for lexical keyword reranking.

### LLM Generation
* **Google Gemini**: `google-genai` SDK using `gemini-3.5-flash-lite` as the sole generation model.

### Knowledge Source
* **Obsidian**: Local Markdown `.md` vaults.

---

## ⚙️ Local Setup

Follow these steps to run LocaL-iQ locally:

### 1. Clone Repository
```bash
git clone https://github.com/thinbearr/LocaL-iQ.git
cd LocaL-iQ
```

### 2. Configure Environment Variables
Copy `.env.example` to `.env` and add your Google Gemini API key:
```bash
cp .env.example .env
```
Edit `.env`:
```env
GEMINI_API_KEY=your_actual_gemini_api_key_here
GEMINI_MODEL=gemini-3.5-flash-lite
CHROMA_DB_DIR=./chroma_db
```

### 3. Install Backend Dependencies
```bash
pip install -r requirements.txt
```

### 4. Install Frontend Dependencies
```bash
cd frontend
npm install
cd ..
```

### 5. Start Backend REST API Server
In one terminal window, run:
```bash
gunicorn --bind 0.0.0.0:$PORT server:app
```
*(Runs on `http://127.0.0.1:5000`)*

### 6. Start React Frontend
In a second terminal window, run:
```bash
cd frontend
npm run dev
```
*(Runs on `http://localhost:5173`)*

### 7. Open Application
Open **[http://localhost:5173](http://localhost:5173)** in your browser. LocaL-iQ will automatically discover local Obsidian vaults and initialize the knowledge base.

---

## 🔐 Environment Variables & Security

| Variable | Required | Default | Description |
| :--- | :---: | :---: | :--- |
| `GEMINI_API_KEY` | **Yes** | — | Google Gemini API key for grounded answer generation. |
| `GEMINI_MODEL` | No | `gemini-3.5-flash-lite` | Gemini model variant. |
| `CHROMA_DB_DIR` | No | `./chroma_db` | Storage path for local ChromaDB database. |

> [!IMPORTANT]
> The `GEMINI_API_KEY` must remain strictly server-side inside `.env` and must **never** be committed to GitHub or exposed to client-side frontend code. `.env` is included in `.gitignore`.

---

## 🌐 Demo / Deployment

* **Live Production Backend**: [https://local-iq.onrender.com](https://local-iq.onrender.com)
* **Local Installation**: Direct connection to your personal local Obsidian vaults on your local machine.

*Note: A hosted web demo uses a pre-loaded sample knowledge base (`sample_vault/`) because web browsers cannot directly access an evaluator's local filesystem. Full local vault discovery and privacy require running the application locally.*

---

## 📁 Project Structure

```text
LocaL-iQ/
├── frontend/                     # React + Vite Frontend SPA
│   ├── public/                   # Static assets & icons
│   ├── src/
│   │   ├── components/
│   │   │   ├── AskPage.jsx                 # Question composer & answer view
│   │   │   ├── KnowledgeBasePage.jsx       # Vault management & document list
│   │   │   ├── RetrievalInspectorPage.jsx  # Trajectory & candidate scoring matrix
│   │   │   ├── SettingsPage.jsx            # RAG hyperparameter configuration
│   │   │   ├── Sidebar.jsx                 # Search scope & multi-vault selector
│   │   │   └── TopHeader.jsx               # Active status bar & search scope stats
│   │   ├── App.jsx                         # Main app shell & global state manager
│   │   ├── index.css                       # Dark theme CSS tokens & typography
│   │   └── main.jsx                        # React entrypoint
│   ├── index.html                      # HTML template with Google Fonts
│   ├── package.json                    # Frontend dependencies
│   └── vite.config.js                  # Vite configuration
├── src/                          # Core Python RAG Pipeline
│   ├── chunker.py                # Structure-aware Markdown chunker
│   ├── embedder.py               # Local Sentence-Transformers embedder
│   ├── generator.py              # Gemini LLM answer generator
│   ├── prompt_builder.py         # Grounded RAG prompt builder
│   ├── retriever.py              # Two-stage hybrid retriever & evidence gate
│   ├── vault_discovery.py        # Automated local Obsidian vault scanner
│   ├── vault_parser.py           # Markdown AST & frontmatter parser
│   └── vector_store.py           # ChromaDB vector store & incremental sync
├── sample_vault/                 # Included sample Obsidian vault for testing
├── tests/                        # Automated Pytest test suite
│   ├── test_chunker.py
│   ├── test_evaluation_set.py
│   ├── test_multi_file_kb.py
│   ├── test_retriever.py
│   └── test_vault_parser.py
├── server.py                     # Local desktop Flask REST API server (Obsidian discovery)
├── demo_server.py                # Public Render deployment server (sample_vault RAG)
├── Procfile                      # Render production deployment configuration
├── requirements.txt              # Python backend dependencies
├── .env.example                  # Environment configuration template
├── .gitignore                    # Git exclude rules
└── README.md                     # Project documentation
```

---

## 🌐 Local vs Public Demo Architecture

LocaL-iQ maintains a strict separation between local desktop execution and public cloud deployment:

### 🏠 Local Installation (`server.py`)
* **Run Normal Backend**: Execute `python server.py`.
* **Automatic Vault Discovery**: LocaL-iQ automatically discovers Obsidian vaults on your machine by scanning standard user directories for `.obsidian/` configurations.
* **Full Multi-Vault Control**: Supports multi-vault scope filtering, custom directory selection, and real-time incremental synchronization.
* **Privacy First**: Your actual local Obsidian notes remain 100% private and serve as your knowledge base.

### ☁️ Public Cloud Demo (`demo_server.py`)
* **Render Web Deployment**: The hosted live web application executes `demo_server.py` (configured via `Procfile`).
* **Bundled Knowledge Base**: Operates exclusively over the repository's bundled `sample_vault/`.
* **Isolated from Local Discovery**: Intentionally skips local filesystem scanning because a cloud server cannot access a visitor's local desktop filesystem.
* **Real RAG Pipeline**: Uses the **exact same genuine RAG system** (`HybridRerankedRetriever` + `GeminiLLMGenerator` + `ChromaVectorStore`) to retrieve evidence and generate answers grounded in `sample_vault/` without mock data.

> [!IMPORTANT]
> **Local Desktop Users**: Do not install or run `demo_server.py` for local development. Always launch `server.py` to enable full local Obsidian vault discovery and multi-vault functionality.

---

## 🧪 Testing

Run the full automated test suite using `pytest`:

```bash
python -m pytest tests/ -v
```

The test suite validates:
* Markdown structure-aware chunking and sibling linkage (`test_chunker.py`)
* Vault discovery and Markdown parsing (`test_vault_parser.py`)
* Multi-file additive indexing and deletion (`test_multi_file_kb.py`)
* Hybrid vector + BM25 retrieval and evidence gating (`test_retriever.py`)
* Grounded evaluation questions and out-of-domain guardrail handling (`test_evaluation_set.py`)

---

## 🎨 Product Design

* **Exclusive Dark Mode**: Deep charcoal surfaces (`#0B0E14` / `#121722`), crisp borders (`#1E2638`), and luminous teal accents (`#00A896`).
* **Anthropic/Claude-inspired Serif Typography**: `Newsreader` serif font for major brand headings and titles.
* **Roboto UI Typography**: `Roboto` for body text, navigation controls, labels, cards, and buttons.
* **JetBrains Mono**: `JetBrains Mono` for technical metadata, scores, file paths, and chunk text.

---

## 🔒 Security

* Gemini API key is isolated server-side within environment variables.
* `.env` and local database files are excluded from Git via `.gitignore`.
* Local vault files remain 100% private and never leave your machine during local execution.

---

**Built with React, Flask, ChromaDB, and Google Gemini.**

**LocaL-iQ — Your knowledge, understood.**
