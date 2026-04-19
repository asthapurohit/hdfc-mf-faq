import json
import os
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

STORE_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "vector_store.json")

def get_embedding(text: str) -> list:
    from sklearn.feature_extraction.text import TfidfVectorizer
    return None

def save_store(chunks: list[dict]):
    with open(STORE_PATH, 'w', encoding='utf-8') as f:
        json.dump(chunks, f, ensure_ascii=False, indent=2)
    print(f"Saved {len(chunks)} chunks to vector store")

def load_store() -> list[dict]:
    if not os.path.exists(STORE_PATH):
        raise RuntimeError("Vector store not found. Please run ingest first.")
    with open(STORE_PATH, 'r', encoding='utf-8') as f:
        return json.load(f)

def search(query: str, top_k: int = 4) -> list[dict]:
    chunks = load_store()
    from sklearn.feature_extraction.text import TfidfVectorizer
    
    texts = [c["text"] for c in chunks]
    all_texts = texts + [query]
    
    vectorizer = TfidfVectorizer(stop_words='english')
    tfidf_matrix = vectorizer.fit_transform(all_texts)
    
    query_vec = tfidf_matrix[-1]
    doc_vecs = tfidf_matrix[:-1]
    
    scores = cosine_similarity(query_vec, doc_vecs)[0]
    top_indices = np.argsort(scores)[::-1][:top_k]
    
    return [chunks[i] for i in top_indices if scores[i] > 0]
