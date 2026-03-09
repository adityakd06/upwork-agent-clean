import numpy as np
from sentence_transformers import SentenceTransformer
import faiss

# Load a lightweight embedding model (runs on CPU fine)
_embedder = SentenceTransformer("all-MiniLM-L6-v2")


def _chunk_text(text: str, chunk_size: int = 200) -> list[str]:
    """Split text into overlapping chunks by word count."""
    words = text.split()
    chunks = []
    for i in range(0, len(words), chunk_size - 20):  # 20 word overlap
        chunk = " ".join(words[i:i + chunk_size])
        if chunk.strip():
            chunks.append(chunk)
    return chunks


def build_index(text: str):
    """
    Takes raw knowledge text, chunks it, embeds it, and returns
    a FAISS index + the original chunks list.
    """
    chunks = _chunk_text(text)
    embeddings = _embedder.encode(chunks, convert_to_numpy=True)
    
    # Normalize for cosine similarity
    faiss.normalize_L2(embeddings)
    
    index = faiss.IndexFlatIP(embeddings.shape[1])
    index.add(embeddings)
    
    return index, chunks


def retrieve(query: str, index, chunks: list[str], top_k: int = 3) -> str:
    """
    Given a job description query, find the top_k most relevant
    chunks from the knowledge base and return them as a single string.
    """
    query_vec = _embedder.encode([query], convert_to_numpy=True)
    faiss.normalize_L2(query_vec)
    
    _, indices = index.search(query_vec, top_k)
    
    relevant = [chunks[i] for i in indices[0] if i < len(chunks)]
    return "\n\n".join(relevant)