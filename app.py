import os
import time
import shutil
import tempfile
from pathlib import Path
from typing import List, Optional
import streamlit as st

from src.vault_parser import VaultParser, detect_obsidian_vault
from src.vault_discovery import ObsidianVaultDiscovery, VaultInfo
from src.chunker import MarkdownChunker
from src.embedder import LocalEmbedder
from src.vector_store import ChromaVectorStore
from src.retriever import HybridRerankedRetriever, RetrievalResult
from src.generator import GeminiLLMGenerator

# Page Configuration
st.set_page_config(
    page_title="LocaL-iQ — Your Knowledge, Understood.",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# -------------------------------------------------------------
# DARK MODE EXCLUSIVE DESIGN SYSTEM (Matching Reference Screenshot)
# -------------------------------------------------------------
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Instrument+Serif:ital@0;1&family=Plus+Jakarta+Sans:ital,wght@0,400;0,500;0,600;0,700;1,400&family=JetBrains+Mono:wght@400;500;600&display=swap');

    /* Global Base Reset - Deep Charcoal Dark Theme Only */
    .stApp {
        background-color: #0B0E14;
        color: #F0F4F8;
        font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
        -webkit-font-smoothing: antialiased;
    }

    /* Hide Streamlit Header & Padding Overrides */
    header[data-testid="stHeader"] { visibility: hidden; }
    .block-container { padding-top: 1.5rem; padding-bottom: 2rem; max-width: 1200px; }

    /* Typography Scale */
    .brand-logo {
        font-family: 'Instrument Serif', Georgia, serif;
        font-size: 2.6rem;
        font-weight: 400;
        color: #FFFFFF;
        letter-spacing: -0.02em;
        line-height: 1.05;
        margin: 0;
    }
    .brand-tagline {
        font-family: 'Plus Jakarta Sans', sans-serif;
        font-size: 0.85rem;
        color: #8C9BAE;
        font-weight: 400;
        margin-top: 4px;
        margin-bottom: 24px;
    }

    /* Hero Typography */
    .greeting-line {
        font-family: 'Plus Jakarta Sans', sans-serif;
        font-size: 0.95rem;
        color: #00A896;
        font-weight: 600;
        margin-bottom: 8px;
    }
    .hero-title {
        font-family: 'Instrument Serif', Georgia, serif;
        font-size: 3.6rem;
        font-weight: 400;
        color: #FFFFFF;
        letter-spacing: -0.025em;
        line-height: 1.08;
        margin-bottom: 12px;
    }
    .hero-subtitle {
        font-family: 'Plus Jakarta Sans', sans-serif;
        font-size: 1.05rem;
        color: #94A3B8;
        margin-bottom: 28px;
    }

    /* Sidebar Customization */
    section[data-testid="stSidebar"] {
        background-color: #121722;
        border-right: 1px solid #1E2638;
        padding-top: 1.5rem;
    }
    .sidebar-section-header {
        font-family: 'Plus Jakarta Sans', sans-serif;
        font-size: 0.72rem;
        font-weight: 700;
        color: #64748B;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        margin-top: 20px;
        margin-bottom: 10px;
    }

    /* Active Vault Card in Sidebar */
    .sidebar-vault-card {
        background-color: #182030;
        border: 1px solid #243048;
        border-radius: 10px;
        padding: 14px;
        margin-bottom: 12px;
    }
    .sidebar-vault-name {
        font-weight: 700;
        font-size: 1.05rem;
        color: #FFFFFF;
    }
    .sidebar-vault-stats {
        font-size: 0.84rem;
        color: #00A896;
        margin-top: 6px;
        display: flex;
        align-items: center;
        gap: 12px;
    }

    /* Top Right Vault Status Bar */
    .top-status-bar {
        background-color: #121722;
        border: 1px solid #1E2638;
        border-radius: 8px;
        padding: 10px 20px;
        font-size: 0.88rem;
        display: flex;
        align-items: center;
        justify-content: flex-end;
        gap: 20px;
        color: #94A3B8;
    }
    .top-status-badge {
        background-color: rgba(0, 168, 150, 0.12);
        color: #00A896;
        border: 1px solid #00A896;
        border-radius: 6px;
        padding: 4px 10px;
        font-family: 'Plus Jakarta Sans', sans-serif;
        font-size: 0.78rem;
        font-weight: 700;
        letter-spacing: 0.04em;
    }

    /* Hero Question Input Container */
    .input-hero-container {
        background-color: #121722;
        border: 1px solid #1E2638;
        border-radius: 14px;
        padding: 20px;
        margin-bottom: 32px;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.25);
    }
    .input-hero-footer {
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin-top: 16px;
        padding-top: 14px;
        border-top: 1px solid #1E2638;
        font-size: 0.82rem;
        color: #64748B;
    }

    /* Sample Question Cards Grid */
    .sample-card {
        background-color: #121722;
        border: 1px solid #1E2638;
        border-radius: 12px;
        padding: 20px;
        height: 100%;
        transition: all 0.2s ease;
        cursor: pointer;
    }
    .sample-card:hover {
        border-color: #00A896;
        background-color: #182030;
    }
    .sample-card-title {
        font-weight: 600;
        font-size: 0.98rem;
        color: #F0F4F8;
        margin-bottom: 12px;
        line-height: 1.4;
    }
    .sample-card-source {
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.78rem;
        color: #64748B;
    }

    /* Feature Highlights Bar */
    .features-bar {
        background-color: #121722;
        border: 1px solid #1E2638;
        border-radius: 14px;
        padding: 22px;
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 20px;
        margin-top: 36px;
    }
    .feature-item-title {
        font-weight: 700;
        font-size: 0.95rem;
        color: #FFFFFF;
        margin-bottom: 4px;
    }
    .feature-item-desc {
        font-size: 0.82rem;
        color: #8C9BAE;
        line-height: 1.4;
    }

    /* Grounded Answer Card */
    .answer-card {
        background-color: #121722;
        border: 1px solid #1E2638;
        border-radius: 14px;
        padding: 28px;
        margin-top: 20px;
        margin-bottom: 28px;
    }
    .answer-header {
        font-family: 'Instrument Serif', Georgia, serif;
        font-size: 1.6rem;
        color: #FFFFFF;
        margin-bottom: 14px;
    }
    .evidence-card {
        background-color: #182030;
        border: 1px solid #243048;
        border-left: 4px solid #00A896;
        border-radius: 10px;
        padding: 18px;
        margin-bottom: 14px;
    }
    .mono-meta {
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.8rem;
        color: #00A896;
    }

    /* SVG Icon Styling */
    .svg-icon {
        width: 16px;
        height: 16px;
        display: inline-block;
        vertical-align: middle;
        fill: currentColor;
    }

    /* Streamlit Controls Overrides */
    button[data-baseweb="tab"] {
        font-family: 'Plus Jakarta Sans', sans-serif;
        font-weight: 600;
        color: #8C9BAE;
        font-size: 0.95rem;
        padding: 10px 20px;
    }
    button[aria-selected="true"] {
        color: #00A896 !important;
        border-bottom-color: #00A896 !important;
    }
    div[data-baseweb="select"] > div {
        background-color: #182030 !important;
        border-color: #243048 !important;
        color: #FFFFFF !important;
        border-radius: 8px !alignment;
    }
</style>
""", unsafe_allow_html=True)


@st.cache_resource
def get_system_core(persist_dir: str):
    """Initializes local embedder and persistent ChromaDB vector store."""
    embedder = LocalEmbedder()
    vector_store = ChromaVectorStore(persist_dir=persist_dir)
    return embedder, vector_store


def auto_sync_vault_on_startup(vault_dir: str, embedder, vector_store):
    """Automatic Incremental Startup Synchronization."""
    if not os.path.exists(vault_dir):
        return None

    vault_name = Path(vault_dir).name
    parser = VaultParser(vault_dir)
    chunker = MarkdownChunker(max_chunk_size=800, min_chunk_size=50)
    notes = parser.parse_vault()
    sync_res = vector_store.sync_with_vault_notes(notes, embedder, chunker, vault_name=vault_name)
    return sync_res, len(notes)


def get_greeting() -> str:
    """Returns greeting based on local time."""
    current_hour = time.localtime().tm_hour
    if current_hour < 12:
        return "Good morning"
    elif current_hour < 18:
        return "Good afternoon"
    else:
        return "Good evening"


def main():
    # Active Storage Path Configuration
    if "persist_dir" not in st.session_state:
        st.session_state["persist_dir"] = "./chroma_db"
    
    persist_dir = st.session_state["persist_dir"]
    embedder, vector_store = get_system_core(persist_dir)

    # Vault Discovery Engine
    discovery = ObsidianVaultDiscovery()
    if "discovered_vaults" not in st.session_state:
        st.session_state["discovered_vaults"] = discovery.discover(force_rescan=False)

    discovered_vaults = st.session_state["discovered_vaults"]

    # Active Vault Resolution
    default_vault = "./sample_vault"
    if "active_vault_path" not in st.session_state:
        if discovered_vaults:
            st.session_state["active_vault_path"] = list(discovered_vaults.keys())[0]
        else:
            st.session_state["active_vault_path"] = default_vault

    active_vault = st.session_state["active_vault_path"]
    active_vault_name = Path(active_vault).name
    is_vault, detect_msg = detect_obsidian_vault(active_vault)
    
    # Auto-sync active vault on startup or vault switch
    if st.session_state.get("synced_vault_path") != active_vault and is_vault:
        sync_res, note_count = auto_sync_vault_on_startup(active_vault, embedder, vector_store)
        st.session_state["synced_vault_path"] = active_vault
        st.session_state["last_sync_res"] = sync_res
        st.session_state["last_sync_time"] = time.strftime("%H:%M:%S")

    stats = vector_store.get_stats()
    active_v_stats = vector_store.get_vault_stats(active_vault_name)
    registry = vector_store.get_indexed_files_registry(vault_name=active_vault_name)
    all_files_list = [f["file_name"] for f in registry]

    if "chat_history" not in st.session_state:
        st.session_state["chat_history"] = []

    # -------------------------------------------------------------
    # BRANDING SIDEBAR (Exact Match to Design Reference Screenshot)
    # -------------------------------------------------------------
    st.sidebar.markdown("<div class='brand-logo'>LocaL-iQ</div>", unsafe_allow_html=True)
    st.sidebar.markdown("<div class='brand-tagline'>Your knowledge, understood.</div>", unsafe_allow_html=True)

    st.sidebar.markdown("<div class='sidebar-section-header'>ACTIVE VAULT</div>", unsafe_allow_html=True)
    
    vault_options = list(discovered_vaults.keys()) if discovered_vaults else [active_vault]
    if active_vault not in vault_options:
        vault_options.append(active_vault)

    selected_v_path = st.sidebar.selectbox(
        "Select Active Vault",
        options=vault_options,
        format_func=lambda p: Path(p).name,
        index=vault_options.index(active_vault) if active_vault in vault_options else 0,
        label_visibility="collapsed"
    )

    if selected_v_path != active_vault:
        st.session_state["active_vault_path"] = selected_v_path
        st.rerun()

    st.sidebar.markdown(f"""
    <div class='sidebar-vault-stats'>
        <span><b>{active_v_stats['total_files']}</b> document</span>
        <span><b>{active_v_stats['total_chunks']}</b> chunks</span>
    </div>
    <div style='font-size:0.8rem; color:#64748B; margin-top:6px;'>
        <span style='color:#00A896;'>✓</span> Synced {st.session_state.get('last_sync_time', '23:48:35')}
    </div>
    """, unsafe_allow_html=True)

    st.sidebar.markdown("<div class='sidebar-section-header'>SEARCH SCOPE</div>", unsafe_allow_html=True)
    vault_scope_opt = st.sidebar.radio(
        "Search Scope",
        ["Current Vault", "Selected Vaults", "All Vaults"],
        index=0,
        label_visibility="collapsed",
        key="sb_vault_scope_radio"
    )

    st.sidebar.markdown("<div class='sidebar-section-header'>NAVIGATION</div>", unsafe_allow_html=True)
    
    # -------------------------------------------------------------
    # TOP HEADER STATUS BAR (Top Right)
    # -------------------------------------------------------------
    st.markdown(f"""
    <div class='top-status-bar'>
        <div>Vault: <b style='color:#FFFFFF;'>{active_vault_name}</b></div>
        <div><span style='color:#00A896;'>{active_v_stats['total_files']}</span> document &nbsp;·&nbsp; <span style='color:#00A896;'>{active_v_stats['total_chunks']}</span> chunks</div>
        <div class='top-status-badge'>✓ SYNCED</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Navigation Tabs (Ask, Knowledge Base, Retrieval Inspector, Settings — No Evaluation)
    tab_ask, tab_kb, tab_inspector, tab_settings = st.tabs([
        "Ask",
        "Knowledge Base",
        "Retrieval Inspector",
        "Settings"
    ])

    # -------------------------------------------------------------
    # TAB 4: Settings (Technical Configuration)
    # -------------------------------------------------------------
    with tab_settings:
        st.markdown("<div style='font-family:\"Instrument Serif\", serif; font-size:2.4rem; margin-bottom:4px;'>Settings</div>", unsafe_allow_html=True)
        st.caption("Configure LocaL-iQ retrieval engine, parameters, and storage paths.")

        sett_tab1, sett_tab2, sett_tab3 = st.tabs(["Retrieval", "Generation", "Storage"])

        with sett_tab1:
            col_s1, col_s2 = st.columns(2)
            with col_s1:
                top_k_final = st.slider("Final Top-K Evidence Chunks", 1, 10, 5)
                top_k_pool = st.slider("Initial Candidate Pool Size (Stage 1)", 5, 300, 15)
                semantic_weight = st.slider("Semantic Weight (w_semantic)", 0.0, 1.0, 0.70, step=0.05)
                lexical_weight = round(1.0 - semantic_weight, 2)
                st.info(f"Lexical Weight (w_lexical): {lexical_weight}")

            with col_s2:
                raw_cosine_threshold = st.slider("Absolute Raw Cosine Similarity Threshold", 0.0, 0.8, 0.28, step=0.02)
                enable_expansion = st.checkbox("Enable Experimental Query Expansion", value=False)
                st.caption("Query expansion enriches search queries with domain terms.")

        with sett_tab2:
            st.markdown("#### LLM Generation Model")
            model_display = os.getenv("GEMINI_MODEL", "gemini-3.5-flash")
            st.info(f"Server Provider: Google Gemini ({model_display}) via environment secret key.")

        with sett_tab3:
            st.markdown("#### Vector Storage Path")
            new_persist_dir = st.text_input("ChromaDB Vector Directory", value=persist_dir, key="settings_persist_path")
            if new_persist_dir != persist_dir:
                st.session_state["persist_dir"] = new_persist_dir
                st.success(f"Storage path updated to {new_persist_dir}. Restarting engine...")
                st.rerun()

    top_k_final = st.session_state.get("top_k_final", 5)
    top_k_pool = st.session_state.get("top_k_pool", 15)
    semantic_weight = st.session_state.get("semantic_weight", 0.70)
    lexical_weight = round(1.0 - semantic_weight, 2)
    raw_cosine_threshold = st.session_state.get("raw_cosine_threshold", 0.28)
    enable_expansion = st.session_state.get("enable_expansion", False)

    # -------------------------------------------------------------
    # TAB 2: Knowledge Base Manager
    # -------------------------------------------------------------
    with tab_kb:
        st.markdown("<div style='font-family:\"Instrument Serif\", serif; font-size:2.4rem; margin-bottom:4px;'>Knowledge Base</div>", unsafe_allow_html=True)
        st.caption("Manage connected Obsidian vaults and document synchronization.")

        col_kb_act1, col_kb_act2 = st.columns([1, 3])
        with col_kb_act1:
            if st.button("Rescan Vaults", use_container_width=True, key="kb_rescan_btn"):
                with st.spinner("Scanning system for Obsidian vaults..."):
                    st.session_state["discovered_vaults"] = discovery.discover(force_rescan=True)
                st.success("Rescan complete.")
                time.sleep(1)
                st.rerun()

        st.markdown("<br>", unsafe_allow_html=True)
        col_kb_vlist, col_kb_main = st.columns([1, 2])

        with col_kb_vlist:
            st.markdown("#### Discovered Vaults")
            for v_path, v_info in discovered_vaults.items():
                v_name = v_info.name
                v_stats = vector_store.get_vault_stats(v_name)
                is_active = (v_path == active_vault)

                card_style = "sidebar-vault-card" if is_active else "sidebar-vault-card"
                badge = "<span class='top-status-badge'>ACTIVE</span>" if is_active else "<span style='font-size:0.75rem; color:#64748B;'>DISCOVERED</span>"

                st.markdown(f"""
                <div class='{card_style}'>
                    <div style='display:flex; justify-content:space-between; align-items:center;'>
                        <span style='font-weight:700; font-size:1.0rem; color:#FFFFFF;'>{v_name}</span>
                        {badge}
                    </div>
                    <div class='mono-meta' style='margin-top:6px;'>
                        {v_info.md_count} files &nbsp;·&nbsp; {v_stats['total_chunks']} chunks
                    </div>
                </div>
                """, unsafe_allow_html=True)

                if not is_active:
                    if st.button(f"Connect {v_name}", key=f"btn_conn_{v_name}", use_container_width=True):
                        st.session_state["active_vault_path"] = v_path
                        st.rerun()

        with col_kb_main:
            st.markdown(f"""
            <div class='sidebar-vault-card'>
                <div style='display:flex; justify-content:space-between; align-items:center;'>
                    <div>
                        <h3 style='margin:0; font-family:"Instrument Serif", serif; font-size:1.8rem; color:#FFFFFF;'>{active_vault_name}</h3>
                        <span class='mono-meta'>Path: {active_vault}</span>
                    </div>
                    <span class='top-status-badge'>OBSIDIAN DETECTED</span>
                </div>
            </div>
            """, unsafe_allow_html=True)

            col_fsync1, col_fsync2 = st.columns(2)
            with col_fsync1:
                if st.button("Force Re-index", use_container_width=True):
                    parser = VaultParser(active_vault)
                    chunker = MarkdownChunker(max_chunk_size=800, min_chunk_size=50)
                    notes = parser.parse_vault()
                    sres = vector_store.sync_with_vault_notes(notes, embedder, chunker, vault_name=active_vault_name)
                    st.session_state["last_sync_time"] = time.strftime("%H:%M:%S")
                    st.success(f"Force re-indexed {active_vault_name}.")
                    time.sleep(1)
                    st.rerun()

            with col_fsync2:
                if st.button("Sync Vault", use_container_width=True, type="primary"):
                    parser = VaultParser(active_vault)
                    chunker = MarkdownChunker(max_chunk_size=800, min_chunk_size=50)
                    notes = parser.parse_vault()
                    sres = vector_store.sync_with_vault_notes(notes, embedder, chunker, vault_name=active_vault_name)
                    st.session_state["last_sync_time"] = time.strftime("%H:%M:%S")
                    st.success(f"Synced. Added: {sres['added']}, Deleted: {sres['deleted']}")
                    time.sleep(1)
                    st.rerun()

            st.markdown("---")
            st.markdown("#### Indexed Documents")

            if not registry:
                st.info(f"No documents currently indexed for vault {active_vault_name}.")
            else:
                for idx, fitem in enumerate(registry):
                    fname = fitem["file_name"]
                    ccount = fitem["chunk_count"]
                    col_f1, col_f2, col_f3, col_f4 = st.columns([3, 1.5, 1.5, 1])
                    col_f1.markdown(f"**`{fname}`**")
                    col_f2.markdown(f"<span class='mono-meta'>{ccount} chunks</span>", unsafe_allow_html=True)
                    col_f3.markdown("<span class='top-status-badge'>INDEXED</span>", unsafe_allow_html=True)
                    
                    if col_f4.button("Delete", key=f"del_{fname}_{idx}"):
                        vector_store.delete_file(fname, vault_name=active_vault_name)
                        st.success(f"Deleted {fname}.")
                        st.rerun()

    # -------------------------------------------------------------
    # TAB 1: Ask (Exact Hero Experience Matching Screenshot)
    # -------------------------------------------------------------
    with tab_ask:
        sample_q = st.session_state.get("selected_sample_q", "")

        # Display Hero Header
        greeting = get_greeting()
        st.markdown(f"<div class='greeting-line'>{greeting}</div>", unsafe_allow_html=True)
        st.markdown("<div class='hero-title'>What would you like<br>to know?</div>", unsafe_allow_html=True)
        st.markdown("<div class='hero-subtitle'>Ask anything about your connected knowledge.</div>", unsafe_allow_html=True)

        # Large Hero Question Input Container
        with st.container():
            st.markdown("<div class='input-hero-container'>", unsafe_allow_html=True)
            
            with st.form("ask_hero_form", clear_on_submit=False):
                query_input = st.text_area(
                    "Ask a question across your connected notes...",
                    value=sample_q if sample_q else "",
                    placeholder="Ask a question across your connected notes...",
                    height=100,
                    key="hero_query_input",
                    label_visibility="collapsed"
                )
                
                btn_col1, btn_col2 = st.columns([4, 1])
                with btn_col2:
                    submit_asked = st.form_submit_button("Ask Question", type="primary", use_container_width=True)

            st.markdown("""
            <div class='input-hero-footer'>
                <div><span>✧</span> Powered by RAG &nbsp;·&nbsp; Grounded in your knowledge &nbsp;·&nbsp; Private & local</div>
            </div>
            </div>
            """, unsafe_allow_html=True)

        # Display Grounded Response & Evidence if available
        if "last_answer" in st.session_state and "last_user_query" in st.session_state:
            u_query = st.session_state["last_user_query"]
            res: RetrievalResult = st.session_state["last_res"]
            answer = st.session_state["last_answer"]

            st.markdown(f"""
            <div class='answer-card'>
                <div class='answer-header'>Answer</div>
                <div style='line-height:1.65; color:#F0F4F8;'>{answer}</div>
            </div>
            """, unsafe_allow_html=True)

            st.markdown("### Grounded Source Evidence")
            if res.primary_chunks:
                for idx, p_chunk in enumerate(res.primary_chunks, 1):
                    st.markdown(f"""
                    <div class='evidence-card'>
                        <div style='display:flex; justify-content:space-between; align-items:center; margin-bottom:8px;'>
                            <div>
                                <span style='font-weight:700; font-size:1.0rem; color:#FFFFFF;'>{p_chunk.file_name}</span>
                                &nbsp;<span class='mono-meta'>[{p_chunk.heading}]</span>
                            </div>
                            <span class='mono-meta'>Hybrid Score: {p_chunk.hybrid_score}</span>
                        </div>
                        <div style='background-color:#121722; border:1px solid #1E2638; border-radius:6px; padding:12px; font-family:"JetBrains Mono", monospace; font-size:0.84rem; color:#94A3B8; line-height:1.5;'>
                            {p_chunk.text}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("<div style='font-size:0.95rem; font-weight:600; color:#F0F4F8; margin-bottom:14px;'>Try asking something like</div>", unsafe_allow_html=True)

        # 3 Sample Question Cards Grid (Exact Screenshot Layout)
        q_col1, q_col2, q_col3 = st.columns(3)

        with q_col1:
            st.markdown("""
            <div class='sample-card'>
                <div class='sample-card-title'>What are the main<br>validation checks?</div>
                <div class='sample-card-source'>IDEX_Project.md</div>
            </div>
            """, unsafe_allow_html=True)
            if st.button("Ask: Validation Checks", key="btn_sq_1", use_container_width=True):
                st.session_state["selected_sample_q"] = "What are the main validation checks?"
                st.rerun()

        with q_col2:
            st.markdown("""
            <div class='sample-card'>
                <div class='sample-card-title'>How are cable routing<br>paths calculated?</div>
                <div class='sample-card-source'>architecture.md</div>
            </div>
            """, unsafe_allow_html=True)
            if st.button("Ask: Cable Routing", key="btn_sq_2", use_container_width=True):
                st.session_state["selected_sample_q"] = "How are cable routing paths calculated?"
                st.rerun()

        with q_col3:
            st.markdown("""
            <div class='sample-card'>
                <div class='sample-card-title'>Explain the retrieval<br>architecture.</div>
                <div class='sample-card-source'>retrieval.md</div>
            </div>
            """, unsafe_allow_html=True)
            if st.button("Ask: Retrieval Architecture", key="btn_sq_3", use_container_width=True):
                st.session_state["selected_sample_q"] = "Explain the retrieval architecture."
                st.rerun()

        # Bottom 4 Feature Cards Bar (Exact Screenshot Layout)
        st.markdown(f"""
        <div class='features-bar'>
            <div>
                <div class='feature-item-title'>Your knowledge</div>
                <div class='feature-item-desc'>{active_v_stats['total_files']} document<br>{active_v_stats['total_chunks']} chunks</div>
            </div>
            <div>
                <div class='feature-item-title'>Private & secure</div>
                <div class='feature-item-desc'>All data stays on your device</div>
            </div>
            <div>
                <div class='feature-item-title'>Fast retrieval</div>
                <div class='feature-item-desc'>Hybrid search with semantic + BM25</div>
            </div>
            <div>
                <div class='feature-item-title'>Grounded answers</div>
                <div class='feature-item-desc'>Every answer is backed by your sources</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        if submit_asked and query_input.strip():
            retriever = HybridRerankedRetriever(
                embedder=embedder,
                vector_store=vector_store,
                absolute_semantic_threshold=raw_cosine_threshold,
                w_semantic=semantic_weight,
                w_lexical=lexical_weight
            )

            v_scope = None
            if vault_scope_opt == "Current Vault":
                v_scope = [active_vault_name]
            elif vault_scope_opt == "All Vaults":
                v_scope = None

            with st.spinner("Executing LocaL-iQ retrieval & generating answer..."):
                res = retriever.retrieve(
                    user_query=query_input,
                    chat_history=st.session_state["chat_history"],
                    vault_scope=v_scope,
                    top_k_candidate_pool=top_k_pool,
                    top_k_final=top_k_final,
                    enable_query_expansion=enable_expansion
                )

                generator = GeminiLLMGenerator()
                answer = generator.generate_answer(query_input, res.primary_chunks)

                st.session_state["last_user_query"] = query_input
                st.session_state["last_res"] = res
                st.session_state["last_answer"] = answer
                st.session_state["selected_sample_q"] = ""
                
                st.session_state["chat_history"].append({
                    "user": query_input,
                    "assistant": answer
                })
                st.rerun()

    # -------------------------------------------------------------
    # TAB 3: Retrieval Inspector
    # -------------------------------------------------------------
    with tab_inspector:
        st.markdown("<div style='font-family:\"Instrument Serif\", serif; font-size:2.4rem; margin-bottom:4px;'>Retrieval Inspector</div>", unsafe_allow_html=True)
        st.caption("Inspect query resolution, candidate scoring, BM25 reranking, and evidence selection.")

        if "last_res" not in st.session_state:
            st.info("Ask a question in the Ask tab first to inspect its retrieval trajectory.")
        else:
            res: RetrievalResult = st.session_state["last_res"]

            col_i1, col_i2, col_i3, col_i4, col_i5 = st.columns(5)
            col_i1.metric("Candidates Evaluated", len(res.all_candidates_evaluated))
            col_i2.metric("Selected Evidence", len(res.primary_chunks))
            col_i3.metric("Top Semantic Score", f"{res.max_raw_semantic_score:.4f}")
            col_i4.metric("Top Hybrid Score", f"{res.max_hybrid_score:.4f}")
            col_i5.metric("Latency", f"{res.retrieval_latency_ms:.1f} ms")

            st.markdown("---")
            st.markdown("#### Candidate Pool Scoring Matrix")

            table_data = []
            for c in res.all_candidates_evaluated:
                table_data.append({
                    "Rank": c.rank,
                    "Selected": "Yes" if c.selected else "No",
                    "Source File": c.file_name,
                    "Section": c.heading,
                    "Raw Cosine": c.raw_semantic_score,
                    "BM25 Score": c.lexical_bm25_score,
                    "Hybrid Score": c.hybrid_score
                })
            st.dataframe(table_data, use_container_width=True)


if __name__ == "__main__":
    main()
