"""
Milestone 3 — Ingestion and Chunking
Loads documents from the documents/ folder, cleans the text, and produces
chunks of ~500 characters with 100-character overlap.
"""

import os
import re
import glob


DOCUMENTS_DIR = "documents"
CHUNK_SIZE = 500
CHUNK_OVERLAP = 100


def load_documents(directory: str) -> list[dict]:
    docs = []
    pattern = os.path.join(directory, "*.txt")
    paths = glob.glob(pattern)

    if not paths:
        print(f"[WARNING] No .txt files found in '{directory}/'. Add your scraped documents there.")
        return docs

    for path in paths:
        with open(path, "r", encoding="utf-8") as f:
            raw = f.read()
        docs.append({"source": os.path.basename(path), "raw": raw})
        print(f"[LOAD] {os.path.basename(path)} — {len(raw):,} characters")

    return docs


def clean_text(text: str) -> str:
    # Strip HTML tags
    text = re.sub(r"<[^>]+>", " ", text)

    # Decode common HTML entities
    entities = {
        "&amp;": "&", "&lt;": "<", "&gt;": ">",
        "&quot;": '"', "&#39;": "'", "&nbsp;": " ",
        "&mdash;": "—", "&ndash;": "–", "&hellip;": "…",
    }
    for entity, char in entities.items():
        text = text.replace(entity, char)

    # Remove leftover HTML entity patterns (e.g. &#123;)
    text = re.sub(r"&#?\w+;", " ", text)

    # Remove URLs
    text = re.sub(r"https?://\S+", "", text)

    # --- Reddit-specific noise ---
    # Remove "Go to <subreddit>" navigation lines
    text = re.sub(r"Go to \S+\s*", "", text)
    # Remove subreddit labels like "r/ASU"
    text = re.sub(r"r/\w+", "", text)
    # Remove Reddit username patterns: "u/username" or "u/username avatar"
    text = re.sub(r"u/\w[\w_-]*(?: avatar)?", "", text)
    # Remove vote counts on their own (a bare number followed by a newline, e.g. "4\n" or "12\n")
    text = re.sub(r"^\d+\s*$", "", text, flags=re.MULTILINE)
    # Remove relative timestamps like "4y ago", "2mo ago", "3d ago", "1h ago"
    text = re.sub(r"\b\d+\s*(?:y|mo|d|h|min)?\s*ago\b", "", text)
    # Remove standalone Reddit labels: OP, [deleted], Share, Reply, Report, Save
    text = re.sub(r"\b(OP|Share|Reply|Report|Save|Award|Crosspost|Embed)\b", "", text)
    text = re.sub(r"\[deleted\]", "", text)

    # Collapse multiple blank lines into one
    text = re.sub(r"\n{3,}", "\n\n", text)
    # Collapse horizontal whitespace runs (preserve newlines)
    text = re.sub(r"[ \t]+", " ", text)

    # Remove Unicode replacement characters (U+FFFD) — leftover from bad encoding
    text = text.replace("�", "")
    # Remove any remaining non-printable / non-ASCII control characters
    # Keep: standard ASCII (32–126), newline (10), tab (9)
    text = re.sub(r"[^\x09\x0a\x20-\x7e]", "", text)

    # Final whitespace cleanup after character removal
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)

    return text.strip()


def chunk_text(text: str, source: str, chunk_size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP) -> list[dict]:
    chunks = []
    step = chunk_size - overlap
    start = 0

    while start < len(text):
        end = start + chunk_size
        chunk_text_slice = text[start:end].strip()

        if len(chunk_text_slice) >= 50:
            chunks.append({
                "source": source,
                "chunk_index": len(chunks),
                "text": chunk_text_slice,
            })

        start += step

    return chunks


def ingest(directory: str = DOCUMENTS_DIR) -> list[dict]:
    docs = load_documents(directory)

    if not docs:
        return []

    all_chunks = []
    for doc in docs:
        cleaned = clean_text(doc["raw"])
        print(f"[CLEAN] {doc['source']} — {len(cleaned):,} characters after cleaning")

        chunks = chunk_text(cleaned, source=doc["source"])
        print(f"[CHUNK] {doc['source']} — {len(chunks)} chunks")
        all_chunks.extend(chunks)

    print(f"\n[TOTAL] {len(all_chunks)} chunks across {len(docs)} document(s)")
    return all_chunks


if __name__ == "__main__":
    chunks = ingest()

    if chunks:
        print("\n--- Sample chunk (first) ---")
        print(chunks[0]["text"])
        print("\n--- Sample chunk (last) ---")
        print(chunks[-1]["text"])
