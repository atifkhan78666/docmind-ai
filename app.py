# import streamlit as st
# from pdf_utils import load_pdf
# from llm import summarize_text
# from rag import create_vector_store, chat_with_pdf

# st.set_page_config(page_title="PDF Chat App", layout="wide")
# st.title("📄 PDF Reader + Summarizer + Chat")


# # =========================
# # ⚡ FULL SUMMARY
# # =========================
# @st.cache_data(show_spinner=False)
# def summarize_pages(pages: list[dict]) -> str:
#     full_text = " ".join(p["text"] for p in pages if p.get("text"))

#     if not full_text.strip():
#         return "No text content found in the document."

#     chunk_size = 3000
#     words = full_text.split()
#     chunks = [
#         " ".join(words[i:i + chunk_size])
#         for i in range(0, len(words), chunk_size)
#     ]

#     summaries = []
#     progress = st.progress(0, text="Summarizing document...")

#     for idx, chunk in enumerate(chunks):
#         prompt = f"""Summarize this document chunk into key points:
# - Purpose
# - Key requirements
# - Financial details
# - Important conditions

# Text:
# {chunk}"""
#         try:
#             summaries.append(summarize_text(prompt))
#         except Exception as e:
#             summaries.append(f"[Chunk {idx + 1} failed: {e}]")

#         progress.progress((idx + 1) / len(chunks), text=f"Processing chunk {idx + 1}/{len(chunks)}...")

#     progress.empty()

#     if not summaries:
#         return "Failed to generate summary."

#     combined = "\n\n".join(f"Section {i + 1}:\n{s}" for i, s in enumerate(summaries))

#     final_prompt = f"""Combine these section summaries into one clean structured summary.
# Be specific — avoid generic filler statements.

# {combined}

# Output format:
# ## Purpose
# ## Scope
# ## Eligibility
# ## Financials
# ## Timeline
# ## Key Conditions"""

#     return summarize_text(final_prompt)


# # =========================
# # 📂 FILE UPLOAD
# # =========================
# uploaded_file = st.file_uploader("Upload a PDF", type=["pdf"])

# if uploaded_file:
#     # ── Reset session state when a new file is uploaded ──────────────────
#     # Without this, uploading a second PDF reuses the old vector store
#     file_id = uploaded_file.name + str(uploaded_file.size)
#     if st.session_state.get("file_id") != file_id:
#         for key in ["file_id", "index", "texts", "metadata", "chat_history", "page_summaries"]:
#             st.session_state.pop(key, None)
#         st.session_state.file_id = file_id

#     # ── Load pages ────────────────────────────────────────────────────────
#     pages = load_pdf(uploaded_file)

#     if not pages:
#         st.error("Could not extract text from this PDF. It may be a scanned/image PDF.")
#         st.stop()

#     st.success(f"✅ {len(pages)} pages loaded from **{uploaded_file.name}**")

#     # ── Build vector store once per file ─────────────────────────────────
#     if "index" not in st.session_state:
#         with st.spinner("Building vector store..."):
#             index, texts, metadata = create_vector_store(pages)
#             st.session_state.index = index
#             st.session_state.texts = texts
#             st.session_state.metadata = metadata

#     # =========================
#     # 🔘 SUMMARY BUTTONS
#     # =========================
#     col1, col2 = st.columns(2)

#     # 📑 Page-wise Summary
#     with col1:
#         if st.button("📑 Page-wise Summary"):
#             st.session_state.page_summaries = {}  # Reset old results
#             for page in pages:
#                 with st.spinner(f"Summarizing page {page['page']}..."):
#                     prompt = f"""Summarize this page into short bullet points:
# - Main idea
# - Key details

# Text:
# {page["text"][:1200]}"""
#                     st.session_state.page_summaries[page["page"]] = summarize_text(prompt)

#     # Show stored page summaries (persists after button click)
#     if st.session_state.get("page_summaries"):
#         for page_num, summary in st.session_state.page_summaries.items():
#             st.markdown(f"### Page {page_num}")
#             st.write(summary)

#     # 📚 Full Summary
#     with col2:
#         if st.button("📚 Full Summary"):
#             with st.spinner("Generating full summary..."):
#                 summary = summarize_pages(pages)
#                 st.session_state.full_summary = summary

#     # Show stored full summary (persists after button click)
#     if st.session_state.get("full_summary"):
#         st.markdown("### 📚 Full Summary")
#         st.write(st.session_state.full_summary)

#     # =========================
#     # 💬 CHAT SECTION
#     # =========================
#     st.markdown("---")
#     st.subheader("💬 Chat with PDF")

#     # Initialize chat history
#     if "chat_history" not in st.session_state:
#         st.session_state.chat_history = []

#     # Display previous messages
#     for msg in st.session_state.chat_history:
#         with st.chat_message(msg["role"]):
#             st.write(msg["content"])

#     # Chat input
#     query = st.chat_input("Ask something about the PDF...")

#     if query:
#         # Show user message
#         st.session_state.chat_history.append({"role": "user", "content": query})
#         with st.chat_message("user"):
#             st.write(query)

#         # Generate and show answer
#         with st.chat_message("assistant"):
#             with st.spinner("Thinking..."):
#                 answer = chat_with_pdf(
#                     query,
#                     st.session_state.index,
#                     st.session_state.texts,
#                     st.session_state.metadata
#                 )
#                 st.write(answer)
#                 st.session_state.chat_history.append({"role": "assistant", "content": answer})






import streamlit as st
from pdf_utils import load_pdf
from llm import summarize_text
from rag import create_vector_store, chat_with_pdf

st.set_page_config(
    page_title="Yunite · DocMind AI",
    page_icon="◈",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ─── GLOBAL STYLES ────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;500;600;700;800&family=DM+Sans:ital,opsz,wght@0,9..40,300;0,9..40,400;0,9..40,500;1,9..40,300&display=swap');

/* ════════════════════
   BASE RESET
════════════════════ */
*, *::before, *::after { box-sizing: border-box; }

html, body {
    background: #07090F !important;
    color: #E2E5EF !important;
    font-family: 'DM Sans', sans-serif !important;
}
[data-testid="stAppViewContainer"] {
    background:
        radial-gradient(ellipse 70% 45% at 15% 0%,  rgba(96,165,250,0.08) 0%, transparent 65%),
        radial-gradient(ellipse 55% 40% at 85% 95%, rgba(139,92,246,0.06) 0%, transparent 60%),
        #07090F !important;
}
[data-testid="stHeader"]  { background: transparent !important; }
[data-testid="stSidebar"] { display: none !important; }
#MainMenu, footer, header { visibility: hidden !important; }
[data-testid="stToolbar"] { display: none !important; }
section.main > div, .block-container {
    padding: 0 !important;
    max-width: 100% !important;
}
::-webkit-scrollbar { width: 3px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: rgba(96,165,250,0.25); border-radius: 2px; }
h1,h2,h3,h4,h5 { font-family: 'Syne', sans-serif !important; }

/* ════════════════════
   NAV
════════════════════ */
.nav {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 20px 64px;
    border-bottom: 1px solid rgba(255,255,255,0.055);
    background: rgba(7,9,15,0.85);
    backdrop-filter: blur(24px);
    position: sticky;
    top: 0;
    z-index: 200;
}
.nav-left { display: flex; align-items: center; gap: 16px; }
.nav-logo {
    font-family: 'Syne', sans-serif;
    font-size: 21px;
    font-weight: 800;
    letter-spacing: -0.6px;
    color: #fff;
}
.nav-logo span { color: #60A5FA; }
.nav-sep { width: 1px; height: 16px; background: rgba(255,255,255,0.1); }
.nav-by {
    font-size: 13px;
    font-weight: 300;
    color: rgba(226,229,239,0.35);
}
.nav-by b { font-weight: 500; color: rgba(226,229,239,0.65); }
.nav-pill {
    font-size: 10px;
    font-weight: 700;
    letter-spacing: 2.2px;
    text-transform: uppercase;
    color: rgba(96,165,250,0.75);
    border: 1px solid rgba(96,165,250,0.22);
    padding: 4px 11px;
    border-radius: 20px;
}

/* ════════════════════
   HERO
════════════════════ */
.hero {
    padding: 72px 64px 56px;
    max-width: 860px;
}
.eyebrow {
    display: flex;
    align-items: center;
    gap: 10px;
    font-size: 10.5px;
    font-weight: 700;
    letter-spacing: 3px;
    text-transform: uppercase;
    color: #60A5FA;
    margin-bottom: 22px;
}
.eyebrow::before {
    content: '';
    display: block;
    width: 22px;
    height: 1px;
    background: #60A5FA;
    flex-shrink: 0;
}
.hero-title {
    font-family: 'Syne', sans-serif;
    font-size: clamp(34px, 4.8vw, 62px);
    font-weight: 800;
    line-height: 1.06;
    letter-spacing: -2px;
    color: #fff;
    margin-bottom: 22px;
}
.hero-title em {
    font-style: normal;
    color: transparent;
    -webkit-text-stroke: 1.5px rgba(96,165,250,0.55);
}
.hero-sub {
    font-size: 16px;
    font-weight: 300;
    color: rgba(226,229,239,0.45);
    line-height: 1.75;
    max-width: 500px;
    margin-bottom: 30px;
}
.pills { display: flex; gap: 8px; flex-wrap: wrap; }
.pill {
    font-size: 12px;
    font-weight: 500;
    color: rgba(226,229,239,0.4);
    border: 1px solid rgba(255,255,255,0.07);
    padding: 5px 13px;
    border-radius: 20px;
}
.pill b { color: #60A5FA; margin-right: 4px; font-weight: 400; }

/* ════════════════════
   SECTION LABEL
════════════════════ */
.section-label {
    font-family: 'Syne', sans-serif;
    font-size: 10px;
    font-weight: 700;
    letter-spacing: 2.8px;
    text-transform: uppercase;
    color: rgba(226,229,239,0.28);
    margin-bottom: 14px;
}

/* ════════════════════
   UPLOAD ZONE
════════════════════ */
.upload-wrap {
    padding: 0 64px 52px 64px;
    max-width: 100%;
}
            
[data-testid="stFileUploader"] {
    background: rgba(96,165,250,0.035) !important;
    border: 1.5px dashed rgba(96,165,250,0.32) !important;
    border-radius: 16px !important;
    transition: all 0.25s ease !important;
    margin-left: 65px !important;
    width: 70% !important;
}
[data-testid="stFileUploader"]:hover {
    border-color: rgba(96,165,250,0.58) !important;
    background: rgba(96,165,250,0.06) !important;
    box-shadow: 0 0 32px rgba(96,165,250,0.07) !important;
}
[data-testid="stFileUploaderDropzone"] {
    padding: 32px 36px !important;
    background: transparent !important;
    border: none !important;
}
[data-testid="stFileUploaderDropzoneInstructions"] span {
    color: rgba(226,229,239,0.5) !important;
    font-size: 14.5px !important;
}
[data-testid="stFileUploaderDropzoneInstructions"] small {
    color: rgba(226,229,239,0.28) !important;
    font-size: 12px !important;
}
[data-testid="stFileUploaderDropzone"] button {
    background: rgba(96,165,250,0.14) !important;
    border: 1.5px solid rgba(96,165,250,0.38) !important;
    border-radius: 10px !important;
    color: #93C5FD !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 13px !important;
    font-weight: 600 !important;
    padding: 8px 22px !important;
    transition: all 0.2s !important;
}
[data-testid="stFileUploaderDropzone"] button:hover {
    background: rgba(96,165,250,0.26) !important;
    border-color: rgba(96,165,250,0.65) !important;
    color: #fff !important;
}

/* ════════════════════
   STATUS BAR
════════════════════ */
.status-bar {
    display: flex;
    align-items: center;
    gap: 10px;
    margin: 0 64px 36px 64px;
    padding: 13px 20px;
    background: rgba(96,165,250,0.055);
    border: 1px solid rgba(96,165,250,0.14);
    border-radius: 12px;
    font-size: 13.5px;
    color: rgba(226,229,239,0.65);
    max-width: calc(100% - 128px);
}
.status-dot {
    width: 7px; height: 7px;
    background: #4ADE80;
    border-radius: 50%;
    box-shadow: 0 0 7px #4ADE80;
    flex-shrink: 0;
    animation: blink 2.2s ease-in-out infinite;
}
@keyframes blink {
    0%,100% { opacity:1; } 50% { opacity:0.3; }
}
.status-bar strong { color: #fff; font-weight: 500; }

/* ════════════════════
   ACTION BUTTONS
════════════════════ */
.actions-wrap { padding: 0 64px 44px 64px; }

[data-testid="stHorizontalBlock"] {
    max-width: 500px !important;
    gap: 12px !important;
    padding-left: 0 !important;
    margin-left: 65px !important;

}

[data-testid="stHorizontalBlock"] {
    max-width: 500px !important;
    gap: 12px !important;

}
[data-testid="stButton"] > button {
    width: 100% !important;
    padding: 15px 20px !important;
    background: rgba(255,255,255,0.035) !important;
    border: 1px solid rgba(255,255,255,0.09) !important;
    border-radius: 13px !important;
    color: rgba(226,229,239,0.8) !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 13.5px !important;
    font-weight: 500 !important;
    text-align: center !important;
    transition: all 0.18s ease !important;
    cursor: pointer !important;
    white-space: nowrap !important;
}
[data-testid="stButton"] > button:hover {
    background: rgba(96,165,250,0.09) !important;
    border-color: rgba(96,165,250,0.38) !important;
    color: #fff !important;
    transform: translateY(-1px) !important;
    box-shadow: 0 6px 20px rgba(0,0,0,0.3) !important;
}
[data-testid="stButton"] > button:active { transform: translateY(0) !important; }

/* ════════════════════
   RESULT CARDS
════════════════════ */
.result-card {
    margin: 0 64px 32px 64px;
    padding: 28px 32px;
    background: rgba(255,255,255,0.018);
    border: 1px solid rgba(255,255,255,0.065);
    border-radius: 18px;
    position: relative;
    overflow: hidden;
    max-width: calc(100% - 128px);
}
.result-card::before {
    content: '';
    position: absolute;
    top:0; left:0; right:0;
    height: 1px;
    background: linear-gradient(90deg, transparent, rgba(96,165,250,0.38), transparent);
}
.result-card-label {
    font-family: 'Syne', sans-serif;
    font-size: 10px;
    font-weight: 700;
    letter-spacing: 3px;
    text-transform: uppercase;
    color: #60A5FA;
    margin-bottom: 18px;
    display: flex;
    align-items: center;
    gap: 10px;
}
.result-card-label::after {
    content: '';
    flex: 1;
    height: 1px;
    background: rgba(96,165,250,0.13);
}

/* ════════════════════
   DIVIDER
════════════════════ */
.divider {
    height: 1px;
    background: linear-gradient(90deg, transparent, rgba(96,165,250,0.13), transparent);
    margin: 0 64px 44px;
    max-width: 900px;
}

/* ════════════════════
   CHAT HEADER
════════════════════ */
.chat-header { padding: 0 64px 24px; }
.chat-title {
    font-family: 'Syne', sans-serif;
    font-size: 19px;
    font-weight: 700;
    color: #fff;
    letter-spacing: -0.4px;
    margin-bottom: 5px;
}
.chat-hint {
    font-size: 13px;
    font-weight: 300;
    color: rgba(226,229,239,0.3);
}

/* Chat message rows — add left/right gutter */
[data-testid="stChatMessage"] {
    padding: 5px 64px !important;
    background: transparent !important;
    border: none !important;
    width: 70% !important;
}
[data-testid="stChatMessage"] .stMarkdown p,
[data-testid="stChatMessage"] .stMarkdown li {
    font-size: 14px !important;
    line-height: 1.75 !important;
    color: rgba(226,229,239,0.82) !important;
}
[data-testid="stChatMessageAvatarUser"],
[data-testid="stChatMessageAvatarAssistant"] {
    background: rgba(96,165,250,0.12) !important;
    border: 1px solid rgba(96,165,250,0.18) !important;
    border-radius: 50% !important;
    flex-shrink: 0 !important;
}

/* ════════════════════
   CHAT INPUT
   CSS handles what it can.
   JS (below) overrides
   the inline style on
   stBottom directly.
════════════════════ */

/* stBottom — CSS layer (JS will finish the job) */
[data-testid="stBottom"],
[data-testid="stBottom"] > *,
[data-testid="stBottom"] > * > * {
    background-color: #07090F !important;
    background: #07090F !important;
}
[data-testid="stBottom"] {
    border-top: 1px solid rgba(255,255,255,0.055) !important;
    padding: 14px 64px 18px !important;
    
}

/* The chat input widget */
[data-testid="stChatInput"] {
    background: #12161F !important;
    background-color: #12161F !important;
    border: 1.5px solid rgba(96,165,250,0.3) !important;
    border-radius: 14px !important;
    box-shadow: none !important;
    outline: none !important;
    max-width: 1700px !important;        /* ← ADD THIS */
    margin-left: 0 !important;          /* ← ADD THIS */
    margin-right: auto !important;      /* ← ADD THIS */
}
}
[data-testid="stChatInput"]:focus-within {
    border-color: rgba(96,165,250,0.58) !important;
    box-shadow: 0 0 0 3px rgba(96,165,250,0.07) !important;
    background: #141821 !important;
    background-color: #141821 !important;
}

/* Inner textarea */
[data-testid="stChatInput"] textarea {
    background: transparent !important;
    background-color: transparent !important;
    color: #E2E5EF !important;
                -webkit-text-fill-color: white !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 14px !important;
    caret-color: #60A5FA !important;
    border: none !important;
    outline: none !important;
    box-shadow: none !important;
    -webkit-box-shadow: none !important;
    -webkit-appearance: none !important;
    resize: none !important;
}
[data-testid="stChatInput"] textarea::placeholder {
    color: rgba(226,229,239,0.25) !important;
}
[data-testid="stChatInput"] textarea:focus,
[data-testid="stChatInput"] textarea:focus-visible {
    outline: none !important;
    box-shadow: none !important;
    border: none !important;
}

/* Send button */
[data-testid="stChatInputSubmitButton"] button {
    background: rgba(96,165,250,0.18) !important;
    border: 1px solid rgba(96,165,250,0.28) !important;
    border-radius: 10px !important;
    color: #93C5FD !important;
    transition: all 0.18s !important;
}
[data-testid="stChatInputSubmitButton"] button:hover {
    background: rgba(96,165,250,0.32) !important;
    border-color: rgba(96,165,250,0.55) !important;
    color: #fff !important;
}

textarea:focus, textarea:focus-visible {
    outline: none !important;
    box-shadow: none !important;
}

/* ════════════════════
   MISC
════════════════════ */
[data-testid="stAlert"] {
    margin: 0 64px 20px !important;
    border-radius: 12px !important;
    font-size: 13.5px !important;
    max-width: 760px !important;
}
[data-testid="stProgressBar"] > div {
    background: rgba(255,255,255,0.05) !important;
    border-radius: 4px !important;
}
[data-testid="stProgressBar"] > div > div {
    background: linear-gradient(90deg, #60A5FA, #A78BFA) !important;
    border-radius: 4px !important;
}
</style>
""", unsafe_allow_html=True)


# ── JS: force stBottom background — beats Streamlit's inline style ──────────
# Streamlit sets background:white as an inline style on stBottom.
# CSS !important cannot override inline styles; JS can.
st.markdown("""
<script>
(function fixChatBar() {
    const BG = '#07090F';
    function paint() {
        // stBottom and every direct child
        document.querySelectorAll(
            '[data-testid="stBottom"], [data-testid="stBottom"] > *, [data-testid="stBottom"] > * > *'
        ).forEach(el => {
            el.style.setProperty('background',      BG, 'important');
            el.style.setProperty('background-color', BG, 'important');
        });
    }
    // Run immediately, then watch for Streamlit re-renders
    paint();
    new MutationObserver(paint).observe(document.body, { childList: true, subtree: true });
})();
</script>
""", unsafe_allow_html=True)


# ════════════════════════════════════════
# NAV
# ════════════════════════════════════════
st.markdown("""
<div class="nav">
    <div class="nav-left">
        <div class="nav-logo">Doc<span>Mind</span></div>
        <div class="nav-sep"></div>
        <div class="nav-by">by <b>Yunite</b></div>
    </div>
    <div class="nav-pill">AI · BETA</div>
</div>
""", unsafe_allow_html=True)


# ════════════════════════════════════════
# HERO
# ════════════════════════════════════════
st.markdown("""
<div class="hero">
    <div class="eyebrow">Yunite · Intelligent Document Analysis</div>
    <h1 class="hero-title">Read less.<br><em>Understand</em> more.</h1>
    <p class="hero-sub">
        Upload any PDF and instantly summarize, extract insights,
        and have a conversation with your document — powered by LLaMA&nbsp;3.3.
    </p>
    <div class="pills">
        <div class="pill"><b>◈</b>Semantic Search</div>
        <div class="pill"><b>◈</b>Page-level Summaries</div>
        <div class="pill"><b>◈</b>Full Document Analysis</div>
        <div class="pill"><b>◈</b>Source Citations</div>
    </div>
</div>
""", unsafe_allow_html=True)


# ════════════════════════════════════════
# UPLOAD
# ════════════════════════════════════════
st.markdown('<div class="upload-wrap"><div class="section-label">Upload Document</div>', unsafe_allow_html=True)
uploaded_file = st.file_uploader(" ", type=["pdf"], label_visibility="collapsed")
st.markdown('</div>', unsafe_allow_html=True)


# ════════════════════════════════════════
# CACHED FULL SUMMARY
# ════════════════════════════════════════
@st.cache_data(show_spinner=False)
def summarize_pages(pages: list[dict]) -> str:
    full_text = " ".join(p["text"] for p in pages if p.get("text"))
    if not full_text.strip():
        return "No text content found in the document."
    words = full_text.split()
    chunks = [" ".join(words[i:i+3000]) for i in range(0, len(words), 3000)]
    summaries = []
    bar = st.progress(0, text="Analyzing document...")
    for i, chunk in enumerate(chunks):
        prompt = f"""Summarize this document chunk into key points:
- Purpose
- Key requirements
- Financial details
- Important conditions

Text:
{chunk}"""
        try:
            summaries.append(summarize_text(prompt))
        except Exception as e:
            summaries.append(f"[Chunk {i+1} failed: {e}]")
        bar.progress((i+1)/len(chunks), text=f"Processing chunk {i+1} of {len(chunks)}...")
    bar.empty()
    if not summaries:
        return "Failed to generate summary."
    combined = "\n\n".join(f"Section {i+1}:\n{s}" for i, s in enumerate(summaries))
    return summarize_text(f"""Combine these section summaries into one clean structured summary.
Be specific — avoid generic filler statements.

{combined}

Output format:
## Purpose
## Scope
## Eligibility
## Financials
## Timeline
## Key Conditions""")


# ════════════════════════════════════════
# MAIN APP
# ════════════════════════════════════════
if uploaded_file:
    # Reset on new file
    file_id = uploaded_file.name + str(uploaded_file.size)
    if st.session_state.get("file_id") != file_id:
        for k in ["file_id","index","texts","metadata","chat_history","page_summaries","full_summary"]:
            st.session_state.pop(k, None)
        st.session_state.file_id = file_id

    pages = load_pdf(uploaded_file)
    if not pages:
        st.error("Could not extract text. This may be a scanned or image-only PDF.")
        st.stop()

    # Status bar
    st.markdown(f"""
    <div class="status-bar">
        <div class="status-dot"></div>
        <div><strong>{uploaded_file.name}</strong> &mdash; {len(pages)} pages loaded and ready</div>
    </div>
    """, unsafe_allow_html=True)

    # Vector store
    if "index" not in st.session_state:
        with st.spinner("Building knowledge index..."):
            vidx, vtexts, vmeta = create_vector_store(pages)
            st.session_state.index    = vidx
            st.session_state.texts    = vtexts
            st.session_state.metadata = vmeta

    # Action buttons
    st.markdown('<div class="actions-wrap"><div class="section-label">Actions</div>', unsafe_allow_html=True)
    col1, col2 = st.columns([1, 1])

    with col1:
        if st.button("📑  Page-wise Summary"):
            st.session_state.page_summaries = {}
            st.session_state.full_summary   = None
            bar = st.progress(0, text="Starting...")
            for i, page in enumerate(pages):
                bar.progress((i+1)/len(pages), text=f"Summarizing page {page['page']} of {len(pages)}...")
                st.session_state.page_summaries[page["page"]] = summarize_text(
                    f"Summarize this page into short bullet points:\n- Main idea\n- Key details\n\nText:\n{page['text'][:1200]}"
                )
            bar.empty()

    with col2:
        if st.button("📚  Full Document Summary"):
            st.session_state.page_summaries = None
            with st.spinner("Generating full summary..."):
                st.session_state.full_summary = summarize_pages(pages)

    st.markdown('</div>', unsafe_allow_html=True)

    # Results
    if st.session_state.get("page_summaries"):
        for page_num, summary in st.session_state.page_summaries.items():
            st.markdown(f"""
            <div class="result-card">
                <div class="result-card-label">Page {page_num}</div>
                <div style="color:rgba(226,229,239,0.75); font-size:14px; line-height:1.8; padding-top:4px;">
                    {summary.replace(chr(10), '<br>')}
                </div>
            </div>
            """, unsafe_allow_html=True)

    if st.session_state.get("full_summary"):
        st.markdown(f"""
        <div class="result-card">
            <div class="result-card-label">Full Document Summary</div>
            <div style="color:rgba(226,229,239,0.75); font-size:14px; line-height:1.8; padding-top:4px;">
                {st.session_state.full_summary.replace(chr(10), '<br>')}
            </div>
        </div>
        """, unsafe_allow_html=True)

    # Divider
    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

    # Chat header
    st.markdown("""
    <div class="chat-header">
        <div class="chat-title">Ask your document</div>
        <div class="chat-hint">Try &nbsp;·&nbsp; "Summarize page 5" &nbsp;·&nbsp; "What are the key requirements?" &nbsp;·&nbsp; "List all financial terms"</div>
    </div>
    """, unsafe_allow_html=True)

    # Chat history
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    for msg in st.session_state.chat_history:
        if msg["role"] == "user":
            st.markdown(f"""
            <div style="display:flex; justify-content:flex-end; padding: 4px 64px;">
                <div style="
                    max-width: 70%;
                    background: rgba(96,165,250,0.12);
                    border: 1px solid rgba(96,165,250,0.2);
                    border-radius: 18px 18px 4px 18px;
                    padding: 12px 18px;
                    color: #000000;
                    font-size: 14px;
                    line-height: 1.7;
                ">{msg["content"]}</div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div style="display:flex; justify-content:flex-start; padding: 4px 64px;">
                <div style="
                    max-width: 80%;
                    background: rgba(255,255,255,0.03);
                    border: 1px solid rgba(255,255,255,0.07);
                    border-radius: 18px 18px 18px 4px;
                    padding: 12px 18px;
                    color: rgba(226,229,239,0.82);
                    font-size: 14px;
                    line-height: 1.75;
                ">{msg["content"]}</div>
            </div>
            """, unsafe_allow_html=True)

    # Chat input
    st.markdown("""
    <form id="chatform" onsubmit="submitChat(event)" style="
        display:flex; align-items:center; gap:10px;
        padding: 0 64px 40px; max-width: 960px;
        margin: 0;
    ">
        <input
            id="chatinput"
            type="text"
            autocomplete="off"
            placeholder="Ask anything about your document..."
            style="
                flex: 1;
                background: #12161F;
                color: #1a1a2e;
                font-family: 'DM Sans', sans-serif;
                font-size: 14px;
                border: 1.5px solid rgba(96,165,250,0.28);
                border-radius: 14px;
                padding: 14px 18px;
                outline: none;
                text-align: left;
                caret-color: #60A5FA;
                transition: border-color 0.2s, box-shadow 0.2s;
            "
            onfocus="this.style.borderColor='rgba(96,165,250,0.58)'; this.style.boxShadow='0 0 0 3px rgba(96,165,250,0.07)';"
            onblur="this.style.borderColor='rgba(96,165,250,0.28)'; this.style.boxShadow='none';"
        />
        <button type="submit" style="
            background: rgba(96,165,250,0.18);
            border: 1.5px solid rgba(96,165,250,0.32);
            border-radius: 14px;
            color: #93C5FD;
            font-family: 'DM Sans', sans-serif;
            font-size: 14px;
            font-weight: 600;
            padding: 13px 26px;
            cursor: pointer;
            white-space: nowrap;
        ">Send &#8594;</button>
    </form>
    <script>
    function submitChat(e) {
        e.preventDefault();
        const val = document.getElementById('chatinput').value.trim();
        if (!val) return;
        const url = new URL(window.location.href);
        url.searchParams.set('chat_q', val);
        url.searchParams.set('chat_ts', Date.now());
        window.location.href = url.toString();
    }
    </script>
    """, unsafe_allow_html=True)

    params = st.query_params
    query  = params.get("chat_q", "").strip()

    if query:
        st.session_state.chat_history.append({"role": "user", "content": query})
        with st.chat_message("user"):
            st.write(query)
        with st.chat_message("assistant"):
            with st.spinner(""):
                answer = chat_with_pdf(
                    query,
                    st.session_state.index,
                    st.session_state.texts,
                    st.session_state.metadata
                )
                st.write(answer)
                st.session_state.chat_history.append({"role": "assistant", "content": answer})

else:
    # Empty state
    st.markdown("""
    <div style="padding: 0 64px 80px;">
        <div style="
            max-width: 420px;
            padding: 44px;
            background: rgba(255,255,255,0.012);
            border: 1.5px dashed rgba(255,255,255,0.07);
            border-radius: 20px;
            text-align: center;
        ">
            <div style="font-size:34px; margin-bottom:16px; opacity:0.2;">◈</div>
            <div style="font-family:'Syne',sans-serif; font-size:15px; font-weight:600;
                        color:rgba(226,229,239,0.32); margin-bottom:8px;">
                No document uploaded
            </div>
            <div style="font-size:13px; color:rgba(226,229,239,0.17);
                        line-height:1.65; font-weight:300;">
                Drop a PDF above to begin.<br>Supports any text-based PDF.
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

