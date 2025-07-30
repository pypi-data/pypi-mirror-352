from pathlib import Path
from typing import List

import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer
from langchain.text_splitter import RecursiveCharacterTextSplitter


def embed_transcripts(
    folder_path: str,
    collection_name: str = "transcripts",
    model_name: str = "all-MiniLM-L6-v2",
    persist_directory: str = "chroma_db",
    distance: str = "cosine",
    chunk_size: int = 500,
    chunk_overlap: int = 75,
) -> None:
    """Embed all .txt files in folder and store them in ChromaDB."""

    client = chromadb.PersistentClient(
        path=persist_directory, settings=Settings(allow_reset=True)
    )
    collection = client.get_or_create_collection(
        name=collection_name, metadata={"hnsw:space": distance}
    )
    model = SentenceTransformer(model_name)
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
    )

    for file in Path(folder_path).glob("*.txt"):
        text = file.read_text(encoding="utf-8")
        chunks = splitter.split_text(text)
        if not chunks:
            continue
        embeddings = model.encode(chunks).tolist()
        ids = [f"{file.stem}_{i}" for i in range(len(chunks))]
        metadatas = [
            {"source": file.name, "chunk": i} for i in range(len(chunks))
        ]
        collection.add(
            ids=ids,
            embeddings=embeddings,
            documents=chunks,
            metadatas=metadatas,
        )

    client.persist()
    print(
        f"Stored {collection.count()} embeddings in collection '{collection_name}' at '{persist_directory}'."
    )
