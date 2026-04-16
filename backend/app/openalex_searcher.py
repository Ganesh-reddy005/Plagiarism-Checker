import httpx
import os
from typing import Dict, List
from dotenv import load_dotenv

load_dotenv()

async def search_openalex(query: str, max_results: int = 3) -> List[Dict[str, str]]:
    """
    Search OpenAlex API for academic papers matching the query.
    Extracts the title, abstract (by reconstructing the inverted index), and doi/url.
    """
    email = os.getenv("OPENALEX_EMAIL", "")
    api_key = os.getenv("OPENALEX_API_KEY", "")
    
    headers = {}
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"
        
    params = {
        "search": query,
        "per-page": max_results,
        "filter": "has_abstract:true"
    }
    
    if email:
        params["mailto"] = email

    url = "https://api.openalex.org/works"
    
    results = []
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url, params=params, headers=headers)
            if response.status_code != 200:
                print(f"[openalex_searcher] Non-200 response: {response.status_code}")
                return results
                
            data = response.json()
                
            for item in data.get("results", []):
                    title = item.get("title") or "Unknown Title"
                    doi = item.get("doi") or item.get("id") or ""
                    
                    # OpenAlex returns abstracts as an inverted index
                    abstract_index = item.get("abstract_inverted_index")
                    abstract = ""
                    
                    if abstract_index:
                        # Reconstruct abstract
                        # abstract_index is like {"Word": [0, 5], "Another": [1]}
                        word_positions = []
                        for word, positions in abstract_index.items():
                            for pos in positions:
                                word_positions.append((pos, word))
                                
                        # Sort by position
                        word_positions.sort(key=lambda x: x[0])
                        abstract = " ".join([word for pos, word in word_positions])
                    
                    if abstract and doi:
                        results.append({
                            "content": abstract,
                            "url": doi,
                            "title": f"[Academic Paper] {title}"
                        })
                        
    except Exception as e:
        print(f"[openalex_searcher] Error: {e}")
        
    return results
