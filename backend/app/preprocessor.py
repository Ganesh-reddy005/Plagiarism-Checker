"""
Text preprocessing module.
Handles cleaning, normalisation, and sentence splitting.
Uses a robust regex fallback if NLTK punkt is unavailable.
"""
from __future__ import annotations

import re
import ssl
import string
from typing import List

# macOS SSL certificate fix for NLTK downloads
try:
    _create_unverified_https_context = ssl._create_unverified_context
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context

# Try to load NLTK tokenizer; fall back gracefully
_NLTK_AVAILABLE = False
try:
    import nltk
    # Ensure tokenizer data is available
    try:
        nltk.data.find("tokenizers/punkt_tab")
        _NLTK_AVAILABLE = True
    except (LookupError, OSError):
        try:
            nltk.download("punkt_tab", quiet=True)
            _NLTK_AVAILABLE = True
        except Exception:
            pass

    if not _NLTK_AVAILABLE:
        try:
            nltk.data.find("tokenizers/punkt")
            _NLTK_AVAILABLE = True
        except (LookupError, OSError):
            try:
                nltk.download("punkt", quiet=True)
                _NLTK_AVAILABLE = True
            except Exception:
                pass
except ImportError:
    pass


def _regex_sent_tokenize(text: str) -> List[str]:
    """Simple regex sentence splitter as fallback."""
    # Split on . ! ? followed by whitespace and capital letter or end of string
    sentences = re.split(r"(?<=[.!?])\s+(?=[A-Z])", text)
    return [s.strip() for s in sentences if s.strip()]


def split_into_sentences(text: str) -> List[str]:
    """Split text into individual sentences."""
    cleaned = re.sub(r"\s+", " ", text.strip())

    if _NLTK_AVAILABLE:
        try:
            import nltk
            sentences = nltk.sent_tokenize(cleaned)
        except Exception:
            sentences = _regex_sent_tokenize(cleaned)
    else:
        sentences = _regex_sent_tokenize(cleaned)

    # Filter out very short sentences (< 5 words)
    return [s.strip() for s in sentences if len(s.split()) >= 5]


def select_top_sentences(sentences: List[str], max_count: int) -> List[str]:
    """
    Select the most important sentences to limit API calls.
    Strategy: prefer longer, more content-rich sentences.
    """
    if len(sentences) <= max_count:
        return sentences
    scored = sorted(sentences, key=lambda s: len(s.split()), reverse=True)
    return scored[:max_count]


def preprocess(text: str, max_sentences: int = 10) -> List[str]:
    """
    Full preprocessing pipeline.
    Returns a list of selected sentences ready for web search.
    """
    sentences = split_into_sentences(text)
    selected = select_top_sentences(sentences, max_sentences)
    return selected
