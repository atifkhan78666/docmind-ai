import re
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
from pdf_utils import chunk_text
from llm import generate_response

_model = None


def get_model() -> SentenceTransformer:
    global _model
    if _model is None:
        _model = SentenceTransformer("all-MiniLM-L6-v2")
    return _model


def create_vector_store(pages: list[dict]) -> tuple:
    texts = []
    metadata = []

    for page in pages:
        chunks = chunk_text(page["text"])
        for chunk in chunks:
            texts.append(chunk)
            metadata.append({"page": page["page"]})

    model = get_model()
    embeddings = model.encode(texts, show_progress_bar=False)

    dimension = embeddings.shape[1]
    index = faiss.IndexFlatL2(dimension)
    index.add(np.array(embeddings, dtype=np.float32))

    return index, texts, metadata


def retrieve(query: str, index, texts: list, metadata: list, k: int = 5) -> list[dict]:
    """Semantic search — finds chunks most similar to the query."""
    model = get_model()
    query_embedding = model.encode([query])
    distances, indices = index.search(np.array(query_embedding, dtype=np.float32), k)

    seen = set()
    results = []

    for idx in indices[0]:
        chunk = texts[idx]
        if chunk not in seen:
            seen.add(chunk)
            results.append({
                "text": chunk,
                "page": metadata[idx]["page"]
            })

    return results


def retrieve_by_page(page_nums: list[int], texts: list, metadata: list) -> list[dict]:
    """
    Direct page lookup — bypasses FAISS entirely.
    Returns all chunks belonging to the requested page numbers.
    """
    results = []
    for i, meta in enumerate(metadata):
        if meta["page"] in page_nums:
            results.append({
                "text": texts[i],
                "page": meta["page"]
            })
    return results


def extract_page_numbers(query: str) -> list[int]:
    """
    Detect page number mentions in a query.
    Handles patterns like:
      - "summarize page 5"
      - "what is on page 3 and page 7"
      - "page5" or "pg 5" or "p.5"
    Returns a list of page numbers found, or empty list if none.
    """
    # Matches: page 5, page5, pg 5, pg5, p.5, p 5
    pattern = r'\b(?:page|pg|p\.?)\s*(\d+)\b'
    matches = re.findall(pattern, query.lower())
    return [int(m) for m in matches]


def chat_with_pdf(query: str, index, texts: list, metadata: list) -> str:
    """
    Answer a question using PDF context.
    - If query mentions specific page numbers → direct page lookup
    - Otherwise → semantic FAISS search
    """
    page_nums = extract_page_numbers(query)

    if page_nums:
        # ── Direct page fetch ──────────────────────────────────────────
        results = retrieve_by_page(page_nums, texts, metadata)

        if not results:
            available = sorted(set(m["page"] for m in metadata))
            return (
                f"❌ Page {page_nums} not found in the document.\n\n"
                f"📄 Available pages: {available[0]} to {available[-1]}"
            )

        context_parts = [f"[Page {r['page']}]: {r['text']}" for r in results]
        context = "\n\n".join(context_parts)
        source_pages = sorted(set(r["page"] for r in results))
        sources = ", ".join(f"Page {p}" for p in source_pages)

        # Detect if user wants a summary or just content
        wants_summary = any(
            word in query.lower()
            for word in ["summarize", "summary", "summarise", "overview", "briefly"]
        )

        if wants_summary:
            prompt = f"""Summarize the following page content into clear bullet points.
Cover the main idea and key details.

Content:
{context}"""
        else:
            prompt = f"""Answer the question based on the specific page content below.

Content:
{context}

Question:
{query}"""

    else:
        # ── Semantic search ────────────────────────────────────────────
        results = retrieve(query, index, texts, metadata)

        context_parts = [f"[Page {r['page']}]: {r['text']}" for r in results]
        context = "\n\n".join(context_parts)
        source_pages = sorted(set(r["page"] for r in results))
        sources = ", ".join(f"Page {p}" for p in source_pages)

        prompt = f"""Answer the question based ONLY on the context below.
If the answer is not in the context, say "I could not find this in the document."

Context:
{context}

Question:
{query}

Mention which pages the information came from at the end."""

    answer = generate_response(
        prompt,
        system="You are a precise document analyst. Only use the provided context to answer."
    )
    return f"{answer}\n\n📄 **Sources:** {sources}"