# LocaL-iQ

### Your knowledge, understood.

**LocaL-iQ** is a production-oriented, local-first **Retrieval-Augmented Generation (RAG) knowledge assistant for Obsidian Markdown vaults**.

It lets users connect their local Obsidian vaults and ask questions grounded in their own notes. The system combines **structure-aware Markdown processing, hybrid semantic + lexical retrieval, evidence gating, contextual expansion, and citation-aware Gemini generation**.

### 🌐 Demo / Deployment

### 🚀 Live Demo

**[Launch LocaL-iQ](https://local-iq.vercel.app/)**

The public demo runs the complete LocaL-iQ RAG pipeline against a bundled
sample Obsidian vault, allowing evaluators to test the application without
local installation.

> **Demo note:** The hosted version uses `sample_vault/` because a cloud
> deployment cannot access a visitor's local filesystem.

### 🏠 Local Installation

For full Obsidian integration, run LocaL-iQ locally. The local version
automatically discovers Obsidian vaults on your machine and supports
multi-vault retrieval, custom directory selection, and incremental
synchronization.

### 🔗 Links

- **Live Demo:** https://local-iq.vercel.app/
- **GitHub:** https://github.com/thinbearr/LocaL-iQ

---

## ⚡ What it does

LocaL-iQ turns unstructured Obsidian notes into a grounded, interactive knowledge engine.

* **Automated Vault Discovery**: Scans user-accessible directories for folders containing an `.obsidian/` directory and valid Markdown notes.
* **Multi-Vault Support**: Detects, manages, and retrieves across multiple Obsidian vaults simultaneously.
* **Granular Search Scope**: Choose between **Current Vault**, **Selected Vaults**, or **All Vaults**.
* **Incremental Synchronization**: Tracks new, modified, deleted, and unchanged Markdown files without unnecessarily rebuilding the entire index.
* **Markdown Parsing & Structure-Aware Chunking**: Preserves heading hierarchies, bullet lists, tags, code blocks, and sibling context while creating semantically cohesive chunks.
* **Two-Stage Hybrid Retrieval**: Combines dense vector retrieval using `all-MiniLM-L6-v2` with lexical BM25 reranking.
* **Raw Cosine Semantic Evidence Gate**: Applies an absolute cosine similarity threshold before lexical reranking to filter low-relevance candidates.
* **Bounded Sibling & Heading Context**: Adds adjacent sibling chunks and parent heading context to improve semantic completeness.
* **Conversation-Aware RAG**: Resolves follow-up questions and conversational references across multi-turn sessions.
* **Citation-Aware Answers**: Generates grounded answers with source file and section citations.
* **Retrieval Inspector**: Exposes candidate ranking, cosine scores, BM25 scores, hybrid scores, selection status, and evaluated search scope.
* **Grounding Guardrail**: Suppresses generation when sufficiently relevant vault evidence cannot be retrieved.
* **Gemini-Powered Generation**: Uses Google Gemini for final grounded synthesis.

---

## 🏗️ RAG Architecture

### Local Execution (Desktop)

```text
                   Obsidian Vault (.md files)
                              ↓
                       Vault Discovery
                              ↓
                       Markdown Parsing
                              ↓
                  Structure-Aware Chunking
                              ↓
                 Sentence-Transformers / MiniLM
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
                    Gemini 3.5 Flash Lite
                              ↓
                       Answer + Citations
```

### Public Cloud Demo (Render)

```text
                        sample_vault
                              ↓
                       Markdown Parsing
                              ↓
                  Structure-Aware Chunking
                              ↓
                     Gemini Embedding 2
                              ↓
                    ChromaDB Vector Store
                              ↓
           Same retrieval/reranking/grounding pipeline
                              ↓
                    Gemini 3.5 Flash Lite
                              ↓
                       Answer + Citations
```

### Raw Cosine Evidence Gate

Before lexical reranking, every candidate retrieved through dense vector search must pass an absolute **raw cosine similarity threshold**.

The threshold is configurable in Settings and defaults to `0.28`.

Candidates that do not meet the threshold are discarded before BM25 fusion. This prevents low-relevance passages from being forwarded to the LLM context.

---

## 🗂️ Multi-Vault Retrieval

LocaL-iQ distinguishes between managing a vault and querying across vaults.

### Active Vault

The currently active and managed vault used for management operations such as manual force re-indexing.

### Search Scope

Controls which vaults participate in retrieval:

* **Current Vault**: Search only the active vault.
* **Selected Vaults**: Search a user-selected combination of vaults.
* **All Vaults**: Search across all discovered vaults.

---

## 🔄 Incremental Synchronization

LocaL-iQ performs additive, diff-based indexing when vault contents change.

* **New Markdown Files**: Detected, parsed, embedded, and added to the index.
* **Modified Markdown Files**: Existing chunk embeddings are removed and regenerated.
* **Deleted Markdown Files**: Associated vector embeddings and metadata are removed.
* **Unchanged Files**: Skipped during synchronization.

Internal Obsidian metadata directories such as `.obsidian/` are excluded from indexing.

---

## 🛡️ Grounding & Anti-Hallucination

LocaL-iQ is designed to keep generated answers grounded in retrieved vault evidence.

Before generation, retrieved candidates must pass the semantic evidence gate and satisfy the retrieval criteria.

If no sufficiently relevant evidence is available, generation is suppressed and the application returns:

> **“No relevant information found in the vault.”**

When evidence is available, the Gemini generator is instructed to answer strictly from the retrieved context and provide source file and section citations.

This retrieval-first design reduces unsupported generation by preventing low-relevance or unrelated passages from being forwarded to the LLM.

---

## 🔍 Retrieval Inspector

The **Retrieval Inspector** provides transparency into the retrieval and ranking pipeline.

### Trajectory Flow

Visualizes the stages from dense retrieval through evidence filtering, reranking, context construction, and generation.

### Candidate Pool Scoring Matrix

Displays candidate chunks alongside:

* Source vault
* Filename
* Section heading
* Raw cosine similarity
* BM25 lexical score
* Hybrid fusion score
* Selection status

### Evaluated Search Scope

Shows the exact vault scope evaluated for the active query.

This makes the RAG pipeline inspectable rather than treating retrieval as a black box.

---

## 💻 Technology Stack

### Frontend

* **React 19** — Component-based single-page application.
* **Vite 8** — Frontend development server and bundler.
* **Vanilla CSS** — Custom design system with CSS variables and dark-mode UI.
* **Google Fonts**

  * `Newsreader` — Serif display typography.
  * `Roboto` — UI typography.
  * `JetBrains Mono` — Technical metadata and retrieval information.

### Backend

* **Python 3.12** — Core runtime.
* **Flask 3.1** — REST API server.
* **Flask-CORS** — Cross-origin API support.

### RAG & Vector Storage

* **ChromaDB** — Embedded vector database using HNSW indexing and cosine similarity.
* **Sentence-Transformers** — `sentence-transformers/all-MiniLM-L6-v2` for local 384-dimensional embeddings.
* **Rank-BM25** — `BM25Okapi` for lexical reranking.

### LLM Generation

* **Google Gemini**
* **`google-genai` SDK**
* **`gemini-3.5-flash-lite`**

### Knowledge Source

* **Obsidian**
* Local Markdown `.md` vaults.

---

## ⚙️ Local Setup

Follow these steps to run LocaL-iQ locally with your own Obsidian vaults.

### 1. Clone the repository

```bash
git clone https://github.com/thinbearr/LocaL-iQ.git
cd LocaL-iQ
```

### 2. Configure environment variables

Copy `.env.example` to `.env`:

```bash
cp .env.example .env
```

Add your Gemini API key:

```env
GEMINI_API_KEY=your_actual_gemini_api_key_here
GEMINI_MODEL=gemini-3.5-flash-lite
CHROMA_DB_DIR=./chroma_db
```

### 3. Install backend dependencies

```bash
pip install -r requirements.txt
```

### 4. Install frontend dependencies

```bash
cd frontend
npm install
cd ..
```

### 5. Start the backend

In one terminal:

```bash
python server.py
```

The Flask backend runs locally and provides access to local Obsidian vault discovery and synchronization.

### 6. Start the React frontend

In a second terminal:

```bash
cd frontend
npm run dev
```

The Vite development server runs on:

```text
http://localhost:5173
```

### 7. Open the application

Open:

**http://localhost:5173**

LocaL-iQ will discover available local Obsidian vaults and initialize the knowledge base.

---

## 🔐 Environment Variables & Security

| Variable         | Required | Default                 | Description                                         |
| ---------------- | :------: | ----------------------- | --------------------------------------------------- |
| `GEMINI_API_KEY` |  **Yes** | —                       | Gemini API key used for grounded answer generation. |
| `GEMINI_MODEL`   |    No    | `gemini-3.5-flash-lite` | Gemini model variant.                               |
| `CHROMA_DB_DIR`  |    No    | `./chroma_db`           | Local ChromaDB storage path.                        |

> **Important:** The `GEMINI_API_KEY` must remain server-side inside `.env`. Never commit it to GitHub or expose it through frontend code.

`.env` is included in `.gitignore`.

---

## 🌐 Demo / Deployment

### 🚀 Live Demo

**https://local-iq.vercel.app/**

The public application provides an interactive demonstration of the LocaL-iQ RAG pipeline using the bundled `sample_vault/`.

### Backend

**Render API:**
https://local-iq.onrender.com

### Public Demo Knowledge Base

The hosted demo uses:

```text
sample_vault/
```

This is intentional. A cloud deployment cannot access an evaluator's local filesystem or private Obsidian directories.

For the public demo:

```text
Browser
   ↓
Vercel Frontend
   ↓
Render Backend
   ↓
sample_vault
   ↓
Same RAG Pipeline
   ↓
Gemini
   ↓
Grounded Answer + Citations
```

No mock retrieval is used. The public deployment uses the same core RAG components:

```text
HybridRerankedRetriever
        +
GeminiLLMGenerator
        +
ChromaVectorStore
```

---

## 🏠 Local vs Public Demo Architecture

LocaL-iQ maintains a separation between local desktop execution and public cloud deployment.

### Local Installation — `server.py`

* Automatically discovers Obsidian vaults on the local machine.
* Supports multi-vault retrieval.
* Supports custom directory selection.
* Supports real-time incremental synchronization.
* Uses the user's own Markdown notes as the knowledge base.
* Keeps local vault contents on the user's machine during local execution.

### Public Cloud Demo — `demo_server.py`

* Runs as the hosted deployment backend.
* Uses only the repository's bundled `sample_vault/`.
* Does not attempt local filesystem discovery.
* Uses the same genuine retrieval and generation pipeline.
* Provides grounded answers based on the bundled knowledge base.

> **Important:** Local users should run `server.py`, not `demo_server.py`, when they want full local Obsidian vault discovery and multi-vault functionality.

---

## 📁 Project Structure

```text
LocaL-iQ/
├── frontend/                         # React + Vite frontend
│   ├── public/                       # Static assets
│   ├── src/
│   │   ├── components/
│   │   │   ├── AskPage.jsx           # Question composer & answer view
│   │   │   ├── KnowledgeBasePage.jsx # Vault management & document list
│   │   │   ├── RetrievalInspectorPage.jsx
│   │   │   ├── SettingsPage.jsx      # RAG configuration
│   │   │   ├── Sidebar.jsx            # Search scope & vault selector
│   │   │   └── TopHeader.jsx          # Application status
│   │   ├── App.jsx                    # Main application shell
│   │   ├── index.css                  # Global design system
│   │   └── main.jsx                   # React entrypoint
│   ├── index.html
│   ├── package.json
│   └── vite.config.js
│
├── src/                              # Core Python RAG pipeline
│   ├── chunker.py                    # Structure-aware Markdown chunker
│   ├── embedder.py                   # Local Sentence-Transformers embeddings
│   ├── generator.py                  # Gemini generation
│   ├── prompt_builder.py             # Grounded prompt construction
│   ├── retriever.py                  # Hybrid retrieval & evidence gate
│   ├── vault_discovery.py            # Obsidian vault discovery
│   ├── vault_parser.py               # Markdown parsing
│   └── vector_store.py               # ChromaDB & incremental sync
│
├── sample_vault/                     # Sample Obsidian vault
│
├── tests/                            # Automated test suite (12 tests)
│   ├── test_chunker.py
│   ├── test_evaluation_set.py
│   ├── test_multi_file_kb.py
│   ├── test_retriever.py
│   ├── test_vault_discovery.py
│   └── test_vault_parser.py
│
├── server.py                         # Local Flask server
├── demo_server.py                    # Public demo server
├── Procfile                          # Render deployment configuration
├── requirements.txt                  # Backend dependencies
├── requirements-demo.txt             # Demo dependencies
├── render.yaml                       # Render configuration
├── .env.example                      # Environment template
├── .gitignore
└── README.md
```

---

## 🧪 Testing

Run the automated test suite (12 tests):

```bash
python -m pytest tests/ -v
```

The test suite validates:

* Markdown structure-aware chunking and sibling linkage.
* Automatic Obsidian vault discovery and refresh (`test_vault_discovery.py`).
* Vault validity checks and new vault discovery after cache expiration.
* Multi-file additive indexing.
* File modification and deletion handling.
* Hybrid vector + BM25 retrieval.
* Semantic evidence gating.
* Grounded evaluation questions.
* Out-of-domain guardrail behavior.

---

## 🎨 Product Design

LocaL-iQ uses a deliberately technical, knowledge-work-oriented interface.

* **Dark Mode** — Deep charcoal surfaces with high-contrast borders.
* **Teal Accent System** — Used for important actions and system states.
* **Newsreader** — Serif display typography for major headings.
* **Roboto** — UI and body typography.
* **JetBrains Mono** — Technical metadata, file paths, scores, and retrieval information.

The Retrieval Inspector intentionally exposes technical retrieval information to make the underlying RAG system understandable rather than hiding it behind a simple chat interface.

---

## 🔒 Security & Privacy

* Gemini API credentials remain server-side.
* `.env` is excluded from Git.
* Local ChromaDB files are excluded from Git.
* Local Obsidian vault contents remain on the user's machine during local execution.
* The public deployment uses only the bundled sample vault.
* The hosted application does not scan or access a visitor's local filesystem.

---

## 🎯 Why this approach?

Traditional RAG pipelines often follow:

```text
Query
 ↓
Vector Search
 ↓
Top-K Chunks
 ↓
LLM
```

LocaL-iQ adds multiple safeguards and retrieval stages:

```text
Query
 ↓
Dense Retrieval
 ↓
Evidence Gate
 ↓
BM25 Reranking
 ↓
Context Expansion
 ↓
Grounded Prompt
 ↓
Gemini
 ↓
Cited Answer
```

This design makes retrieval quality and grounding explicit parts of the system rather than relying solely on the LLM to determine whether retrieved content is relevant.

---

## 🔗 Links

### Live Demo

**https://local-iq.vercel.app/**

### GitHub

**https://github.com/thinbearr/LocaL-iQ**

### Backend

**https://local-iq.onrender.com**

---

**Built with React, Flask, ChromaDB, Sentence-Transformers, BM25, and Google Gemini.**

### LocaL-iQ — Your knowledge, understood.
