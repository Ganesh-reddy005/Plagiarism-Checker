"""
Similarity computation module.
Computes cosine similarity between sentence embeddings and web content embeddings (semantic),
or text overlap similarity using difflib + bigrams (standard).
"""
from __future__ import annotations

import difflib
from typing import Dict, List, Optional, Tuple

import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

from app.embedder import encode


def _word_bigram_jaccard(a: str, b: str) -> float:
    """Compute Jaccard similarity of word bigrams between two strings."""
    def bigrams(text: str):
        words = text.lower().split()
        return set(zip(words, words[1:])) if len(words) >= 2 else set()

    bg_a = bigrams(a)
    bg_b = bigrams(b)
    if not bg_a and not bg_b:
        return 1.0
    if not bg_a or not bg_b:
        return 0.0
    intersection = len(bg_a & bg_b)
    union = len(bg_a | bg_b)
    return intersection / union if union > 0 else 0.0


def compute_standard_similarity(sentence: str, content: str) -> float:
    """
    Standard (non-semantic) text similarity score (0-1).
    Blends:
      - 60% character-level SequenceMatcher ratio (catches exact wording)
      - 40% word bigram Jaccard overlap (catches phrase-level copying)
    """
    # Chunk the content into ~sentence-length windows and take the best match
    words = content.split()
    sentence_len = max(len(sentence.split()), 1)
    window = sentence_len + 10  # slight overshoot for context
    
    best = 0.0
    step = max(sentence_len // 2, 1)
    for start in range(0, max(len(words) - sentence_len + 1, 1), step):
        chunk = " ".join(words[start : start + window])
        char_ratio = difflib.SequenceMatcher(None, sentence.lower(), chunk.lower()).ratio()
        bigram_score = _word_bigram_jaccard(sentence, chunk)
        score = 0.6 * char_ratio + 0.4 * bigram_score
        if score > best:
            best = score
        if best >= 0.99:   # early exit
            break

    return round(min(best, 1.0), 4)


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
