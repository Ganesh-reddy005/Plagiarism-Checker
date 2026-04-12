"""
Similarity computation module.
Computes cosine similarity between sentence embeddings and web content embeddings.
"""
from __future__ import annotations

from typing import Dict, List, Optional, Tuple

import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

from app.embedder import encode


def compute_best_match(
    sentence_embedding: np.ndarray,
    content_list: List[str],
) -> Tuple[float, str]:
    """
    Given a sentence embedding and a list of content strings,
    find the most similar content and return (score, snippet).
    """
    if not content_list:
        return 0.0, ""

    content_embeddings = encode(content_list)
    if len(content_embeddings) == 0:
        return 0.0, ""

    # cosine_similarity expects 2D arrays
    scores = cosine_similarity(
        sentence_embedding.reshape(1, -1), content_embeddings
    )[0]

    best_idx = int(np.argmax(scores))
    best_score = float(scores[best_idx])
    best_content = content_list[best_idx]

    # Truncate snippet to 300 chars for readability
    snippet = best_content[:300].strip()
    if len(best_content) > 300:
        snippet += "..."

    return best_score, snippet


def compute_similarity_for_results(
    sentence_embedding: np.ndarray,
    search_results: List[Dict[str, str]],
) -> Tuple[float, str, str]:
    """
    Find the highest-similarity source from search results.
    Returns (best_score, best_snippet, best_url).
    """
    if not search_results:
        return 0.0, "", ""

    content_list = [r["content"] for r in search_results]
    urls = [r["url"] for r in search_results]

    best_score, best_snippet = compute_best_match(sentence_embedding, content_list)

    # Find corresponding URL
    if not content_list:
        return 0.0, "", ""

    content_embeddings = encode(content_list)
    scores = cosine_similarity(
        sentence_embedding.reshape(1, -1), content_embeddings
    )[0]
    best_idx = int(np.argmax(scores))
    best_url = urls[best_idx]

    return best_score, best_snippet, best_url
