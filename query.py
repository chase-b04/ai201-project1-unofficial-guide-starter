"""
Milestone 5 — Generation
Wires retrieval (embed.py) to the Groq LLM (llama-3.3-70b-versatile).
Answers are grounded: the model may only use the retrieved chunks as context.
Sources are cited both inside the prompt and appended programmatically.
"""

import os
from dotenv import load_dotenv
from groq import Groq
from embed import build_vector_store, retrieve
from ingest import ingest

load_dotenv()

GROQ_MODEL = "llama-3.3-70b-versatile"
TOP_K = 8

# ---------------------------------------------------------------------------
# Build the vector store once at import time so the UI doesn't re-embed on
# every query.  All state lives in this module-level dict.
# ---------------------------------------------------------------------------
_store: dict = {}


def _init_store() -> None:
    """Ingest documents, embed chunks, and cache the collection + model."""
    if _store:
        return  # already initialized

    chunks = ingest()
    if not chunks:
        raise RuntimeError(
            "No chunks found. Add .txt files to documents/ and restart."
        )

    collection, model = build_vector_store(chunks)
    _store["collection"] = collection
    _store["model"] = model
    all_meta = _store["collection"].get(include=["metadatas"])["metadatas"]
    sources_loaded = sorted(set(m["source"] for m in all_meta))
    print(f"[READY] {len(all_meta)} chunks from {len(sources_loaded)} sources:")
    for s in sources_loaded:
        count = sum(1 for m in all_meta if m["source"] == s)
        print(f"         {s} ({count} chunks)")


def _build_prompt(question: str, hits: list[dict]) -> str:
    """
    Construct the grounded prompt.
    Each retrieved chunk is labelled with its source file so the model can
    attribute its answer and we can parse sources afterwards.
    """
    context_blocks = []
    for i, hit in enumerate(hits, 1):
        context_blocks.append(
            f"[Document {i} — source: {hit['source']}]\n{hit['text']}"
        )
    context = "\n\n".join(context_blocks)

    return f"""You are a helpful assistant for ASU students looking for off-campus housing information.

Use the documents below to answer the question. Follow these rules:
- Base your answer on what the documents say. Quote or paraphrase specific details when they are present.
- Cite which document(s) you drew from (e.g. "According to Document 2 — reddit-grad.txt, ...").
- If the documents contain only partial information, share what they do say and note what is missing.
- Only say "I don't have enough information on that." if the documents contain NO relevant information whatsoever.
- Do NOT invent facts or use outside knowledge beyond what is written below.

---
{context}
---

Question: {question}

Answer (cite sources by their document number and file name):"""


def ask(question: str) -> dict:
    """
    End-to-end RAG query.

    Returns a dict with:
        answer  : str   — grounded answer from the LLM
        sources : list  — deduplicated source file names from retrieved chunks
        chunks  : list  — full hit dicts for inspection / display
    """
    _init_store()

    # 1. Retrieve relevant chunks
    hits = retrieve(question, _store["collection"], _store["model"], top_k=TOP_K)

    # 2. Build grounded prompt
    prompt = _build_prompt(question, hits)

    # 3. Call Groq
    client = Groq(api_key=os.environ["GROQ_API_KEY"])
    response = client.chat.completions.create(
        model=GROQ_MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2,   # low temp = more faithful to source text
        max_tokens=512,
    )
    answer = response.choices[0].message.content.strip()

    # 4. Collect unique sources from retrieved chunks (preserves rank order)
    seen = set()
    sources = []
    for hit in hits:
        if hit["source"] not in seen:
            seen.add(hit["source"])
            sources.append(hit["source"])

    return {
        "answer": answer,
        "sources": sources,
        "chunks": hits,
    }


# ---------------------------------------------------------------------------
# Quick CLI test — python query.py
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    test_questions = [
        "Which apartment complexes do students most frequently recommend near ASU?",
        "What concerns do students raise about off-campus housing near ASU Tempe?",
        "What alternatives to Greek housing are available for ASU students?",
    ]

    # result = ask("Which apartment complexes do students most frequently recommend in the Reddit thread 'Best Off-Campus Apartments'?")
    # print(result["answer"])
    # print("\nChunks retrieved:")
    # for hit in result["chunks"]:
    #     print(f"  [{hit['distance']:.3f}] {hit['source']} chunk#{hit['chunk_index']}: {hit['text'][:120]}")

    for q in test_questions:
        print(f"\n{'='*70}")
        print(f"Q: {q}")
        print("="*70)
        result = ask(q)
        print(f"\nA: {result['answer']}")
        print(f"\nSources used:")
        for s in result["sources"]:
            print(f"  - {s}")
