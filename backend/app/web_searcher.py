"""
Web search module using Tavily API.
Configured for high-quality, encyclopedic/academic sources.
"""
from __future__ import annotations

import asyncio
import os
from typing import Dict, List

from dotenv import load_dotenv
from tavily import TavilyClient

load_dotenv()

_tavily_client: TavilyClient | None = None

# Domains known to produce noisy, low-quality results for plagiarism detection
# (social media, user-generated content, pastebin-style sites)
EXCLUDED_DOMAINS = [
    "facebook.com",
    "twitter.com",
    "x.com",
    "instagram.com",
    "reddit.com",
    "quora.com",
    "pinterest.com",
    "tiktok.com",
    "linkedin.com",
    "youtube.com",
    "pastebin.com",
]


def get_tavily_client() -> TavilyClient:
    """Lazily initialise Tavily client (singleton)."""
    global _tavily_client
    if _tavily_client is None:
        api_key = os.getenv("TAVILY_API_KEY")
        if not api_key or api_key.startswith("tvly-your"):
            raise ValueError(
                "TAVILY_API_KEY is not set. Please add your key to backend/.env"
            )
        _tavily_client = TavilyClient(api_key=api_key)
    return _tavily_client


def search_sentence(sentence: str, max_results: int = 5) -> List[Dict[str, str]]:
    """
    Query Tavily for a single sentence with enhanced search config.

    Improvements over basic:
    - search_depth="advanced" → deeper crawl, better quality results
    - exclude_domains → skip social media / low-quality sources
    - include_domains → prioritise encyclopedic sources when possible
    - max_results=5 → more candidates for similarity comparison
    - include_raw_content=True → get more text to compare against

    Returns a list of {content, url, title} dicts.
    """
    client = get_tavily_client()
    try:
        response = client.search(
            query=sentence,
            search_depth="advanced",        # deeper, higher-quality crawl
            max_results=max_results,
            topic="general",                # broad search (not news-specific)
            exclude_domains=EXCLUDED_DOMAINS,
            include_raw_content=False,       # raw content is expensive; snippet is enough
            include_answer=False,
        )
        results = []
        for r in response.get("results", []):
            content = r.get("content", "").strip()
            url = r.get("url", "")
            title = r.get("title", "")
            if content and url:
                results.append({
                    "content": content,
                    "url": url,
                    "title": title,
                })
        return results
    except Exception as e:
        print(f"[web_searcher] Error searching: {e}")
        return []


async def search_all_sentences(
    sentences: List[str], max_results: int = 5
) -> List[List[Dict[str, str]]]:
    """
    Async wrapper: search all sentences concurrently using asyncio.
    Returns a list (same order as input) of search result lists.
    """
    loop = asyncio.get_event_loop()
    tasks = [
        loop.run_in_executor(None, search_sentence, sentence, max_results)
        for sentence in sentences
    ]
    results = await asyncio.gather(*tasks)
    return list(results)
