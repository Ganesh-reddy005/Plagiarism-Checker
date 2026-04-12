"""
Database module for Qdrant vector database.
Handles storing documents and searching for semantic matches.
"""
from __future__ import annotations

import os
from typing import Dict, List, Any

from qdrant_client import QdrantClient
from qdrant_client.http import models

from app.embedder import encode

# We will store sentences from uploaded documents
COLLECTION_NAME = "documents_corpus"

_qdrant_client: QdrantClient | None = None

def get_qdrant_client() -> QdrantClient:
    """Initialize Qdrant client (singleton)."""
    global _qdrant_client
    if _qdrant_client is None:
        qdrant_url = os.getenv("QDRANT_URL")
        qdrant_api_key = os.getenv("QDRANT_API_KEY")
        
        if qdrant_url and qdrant_api_key:
            _qdrant_client = QdrantClient(url=qdrant_url, api_key=qdrant_api_key)
        else:
            # Fallback to local disk-based Qdrant if no remote credentials provided
            _qdrant_client = QdrantClient(path="./qdrant_data")
            
        # Ensure collection exists, assume dimension of all-MiniLM-L6-v2 which is 384
        # Note: If OpenRouter model is configured, dimensions might be different.
        # But for now, we'll try to fetch dimensions or default to 384. 
        # (OpenRouter nomic usually expects 768 or 1536 depending on the model, we'll parameterize it if needed, but 384 is default)
        try:
            _qdrant_client.get_collection(COLLECTION_NAME)
        except Exception:
            _qdrant_client.create_collection(
                collection_name=COLLECTION_NAME,
                vectors_config=models.VectorParams(
                    size=384,  # Adjust if a different base model is used
                    distance=models.Distance.COSINE
                )
            )
            
    return _qdrant_client

def index_document(document_id: str, title: str, sentences: List[str]):
    """Embed and index sentences of a document."""
    if not sentences:
        return
        
    client = get_qdrant_client()
    embeddings = encode(sentences)
    
    points = []
    for i, (sentence, embedding) in enumerate(zip(sentences, embeddings)):
        points.append(
            models.PointStruct(
                id=f"{document_id}_{i}",
                vector=embedding.tolist(),
                payload={
                    "document_id": document_id,
                    "title": title,
                    "content": sentence,
                    "source_type": "internal_db"
                }
            )
        )
        
    client.upsert(
        collection_name=COLLECTION_NAME,
        points=points
    )

def search_internal_database(sentence: str, max_results: int = 3) -> List[Dict[str, Any]]:
    """Search Qdrant for similar sentences."""
    client = get_qdrant_client()
    from app.embedder import encode_single
    vector = encode_single(sentence)
    
    # If vector is empty (e.g. embedder failed), return empty
    if vector.size == 0:
        return []
        
    results = client.search(
        collection_name=COLLECTION_NAME,
        query_vector=vector.tolist(),
        limit=max_results,
        score_threshold=0.5 # Basic filtering to not return complete noise
    )
    
    formatted_results = []
    for hit in results:
        payload = hit.payload or {}
        formatted_results.append({
            "content": payload.get("content", ""),
            "url": f"internal://{payload.get('document_id', 'unknown')}",
            "title": f"Internal DB: {payload.get('title', 'Unknown Document')}",
            "score": hit.score
        })
        
    return formatted_results
