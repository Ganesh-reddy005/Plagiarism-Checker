"""
Embedding module.
Supports OpenRouter if configured, falls back to local Sentence Transformers.
"""
from __future__ import annotations

import os
from typing import List

import numpy as np

# Try to use local model as fallback
try:
    from sentence_transformers import SentenceTransformer
except ImportError:
    pass

_OPENROUTER_MODEL = os.getenv("OPENROUTER_EMBEDDING_MODEL")

# Local fallback
_MODEL_NAME = "all-MiniLM-L6-v2"
_model = None

_openai_client = None

def get_openai_client():
    from openai import OpenAI
    global _openai_client
    if _openai_client is None:
        # OpenRouter usually accepts an api key. We'll look for OPENROUTER_API_KEY.
        key = os.getenv("OPENROUTER_API_KEY")
        if key:
            _openai_client = OpenAI(
                base_url="https://openrouter.ai/api/v1",
                api_key=key,
            )
    return _openai_client

def get_local_model():
    """Lazily load and cache the local fallback model."""
    global _model
    if _model is None:
        print(f"[embedder] Loading local fallback model '{_MODEL_NAME}'...")
        _model = SentenceTransformer(_MODEL_NAME)
        print("[embedder] Local model loaded successfully.")
    return _model

def encode(texts: List[str]) -> np.ndarray:
    """
    Encode a list of strings into embedding vectors.
    """
    if not texts:
        return np.array([])
        
    client = get_openai_client()
    if client and _OPENROUTER_MODEL:
        try:
            response = client.embeddings.create(
                input=texts,
                model=_OPENROUTER_MODEL
            )
            # OpenRouter/OpenAI API returns data[i].embedding
            embeddings = [item.embedding for item in response.data]
            return np.array(embeddings)
        except Exception as e:
            print(f"[embedder] OpenRouter failed, falling back to local: {e}")
            # Fall through to local model

    model = get_local_model()
    embeddings = model.encode(texts, convert_to_numpy=True, normalize_embeddings=True)
    return embeddings

def encode_single(text: str) -> np.ndarray:
    """Encode a single string into an embedding vector."""
    result = encode([text])
    return result[0] if len(result) > 0 else np.array([])
