from typing import Optional

import chromadb
from sentence_transformers import SentenceTransformer

try:
    import google.generativeai as genai
except Exception:  # pragma: no cover
    genai = None


def ask_question(
    collection_name: str,
    query_text: str,
    embed_model: str = "all-MiniLM-L6-v2",
    gen_model: str = "gemini-pro",
    persist_directory: str = "chroma_db",
    n_results: int = 5,
    distance: str = "cosine",
) -> Optional[str]:
    """Retrieve context from ChromaDB and generate an answer using Gemini."""
    client = chromadb.PersistentClient(path=persist_directory)
    collection = client.get_collection(collection_name)

    embedder = SentenceTransformer(embed_model)
    query_emb = embedder.encode([query_text]).tolist()

    results = collection.query(
        query_embeddings=query_emb,
        n_results=n_results,
        include=["documents"],
    )
    context = "\n".join(results["documents"][0])

    if genai is None:
        raise RuntimeError("google-generativeai package not installed")

    response = genai.generate_content(
        model=gen_model,
        prompt=f"Answer the question:\n{query_text}\n\nContext:\n{context}",
    )
    return response.text if hasattr(response, "text") else str(response)
