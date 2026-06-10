"""
Milestone 4 — Embedding and Retrieval
Embeds all chunks from ingest.py using all-MiniLM-L6-v2 and stores them
in a ChromaDB collection. Includes a retrieval function that returns the
top-k most relevant chunks with source metadata and distance scores.
"""

import chromadb
from sentence_transformers import SentenceTransformer
from ingest import ingest


COLLECTION_NAME = "asu_housing"
TOP_K = 8


def build_vector_store(chunks: list[dict], collection_name: str = COLLECTION_NAME) -> chromadb.Collection:
    print("\n[EMBED] Loading embedding model: all-MiniLM-L6-v2 ...")
    model = SentenceTransformer("all-MiniLM-L6-v2")
    texts = [chunk["text"] for chunk in chunks]

    print(f"[EMBED] Embedding {len(texts)} chunks ...")
    embeddings = model.encode(texts, show_progress_bar=True)
    print(f"[EMBED] Done. Each vector has {len(embeddings[0])} dimensions.")

    client = chromadb.Client()
    try:
        client.delete_collection(collection_name)
    except Exception:
        pass

    collection = client.create_collection(
        name=collection_name,
        metadata={"hnsw:space": "cosine"},
    )
    # Load chunks into ChromaDB with metadata
    collection.add(
        ids=[f"{chunk['source']}__chunk{chunk['chunk_index']}" for chunk in chunks],
        documents=texts,
        embeddings=[emb.tolist() for emb in embeddings],
        metadatas=[
            {
                "source": chunk["source"],
                "chunk_index": chunk["chunk_index"],
                "chunk_size": len(chunk["text"]),
            }
            for chunk in chunks
        ],
    )

    print(f"[STORE] {collection.count()} chunks loaded into ChromaDB collection '{collection_name}'.")
    return collection, model


def retrieve(query: str, collection: chromadb.Collection, model: SentenceTransformer, top_k: int = TOP_K, max_per_source: int = 2) -> list[dict]:
    query_embedding = model.encode([query])[0].tolist()
    candidate_k = top_k * 4

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=candidate_k,
        include=["documents", "metadatas", "distances"],
    )
    source_counts: dict[str, int] = {}
    hits = []
    for i in range(len(results["documents"][0])):
        source = results["metadatas"][0][i]["source"]
        if source_counts.get(source, 0) >= max_per_source:
            continue
        source_counts[source] = source_counts.get(source, 0) + 1
        hits.append({
            "rank":        len(hits) + 1,
            "text":        results["documents"][0][i],
            "source":      source,
            "chunk_index": results["metadatas"][0][i]["chunk_index"],
            "chunk_size":  results["metadatas"][0][i]["chunk_size"],
            "distance":    results["distances"][0][i],
        })
        if len(hits) == top_k:
            break

    return hits


def safe_print(text: str) -> None:
    """Print text safely on Windows terminals that don't support full Unicode."""
    print(text.encode("ascii", errors="replace").decode("ascii"))


def print_results(query: str, hits: list[dict]) -> None:
    safe_print(f"\n{'='*70}")
    safe_print(f"QUERY: {query}")
    safe_print(f"{'='*70}")
    for hit in hits:
        safe_print(f"\n--- Rank {hit['rank']} | Source: {hit['source']} | Chunk #{hit['chunk_index']} ---")
        safe_print(f"    Distance score : {hit['distance']:.4f}  (lower = more similar)")
        safe_print(f"    Chunk size     : {hit['chunk_size']} characters")
        safe_print(f"    Text:\n")
        safe_print(f"        {hit['text']}")
        safe_print("")


if __name__ == "__main__":
    # Step 1: Ingest and chunk documents
    chunks = ingest()

    if not chunks:
        print("\n[ERROR] No chunks to embed. Add .txt files to documents/ and re-run.")
        exit(1)

    # Step 2: Embed and store
    collection, model = build_vector_store(chunks)

    # Step 3: Test retrieval with sample queriesy
    test_queries = [
        "What should students know before signing a lease for off-campus housing near ASU?",
        "What concerns do students raise about choosing off-campus housing near ASU Tempe?",
        "What are the pros and cons of living in off-campus student apartments versus traditional apartments near ASU?",
        "What neighborhoods near ASU Tempe are most popular for student housing?",
        "What alternatives to Greek housing are available for ASU students?",
    ]

    for query in test_queries:
        hits = retrieve(query, collection, model, top_k=TOP_K)
        print_results(query, hits)
