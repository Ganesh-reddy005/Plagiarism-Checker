"""
Detector module — orchestrates the full plagiarism detection pipeline.
"""
from __future__ import annotations

import time
from typing import List, Dict

from app.embedder import encode_single
from app.models import CheckRequest, MatchResult, PlagiarismReport, SentenceSearchResult, SearchedSource
from app.preprocessor import preprocess
from app.similarity import compute_similarity_for_results
from app.web_searcher import search_all_sentences
from app.database import search_internal_database

async def run_detection(request: CheckRequest) -> PlagiarismReport:
    """
    Full pipeline:
    1. Preprocess → sentences
    2. Web search (async, concurrent)
    3. Embed each sentence
    4. Internal DB search (Qdrant)
    5. Compare embeddings vs retrieved content (Web & Internal)
    6. Aggregate score
    """
    start_time = time.time()

    sentences = preprocess(request.text, max_sentences=request.max_sentences)
    total_sentences = len(sentences)

    if total_sentences == 0:
        return PlagiarismReport(
            score=0.0,
            total_sentences=0,
            matched_sentences=0,
            matches=[],
            processing_time=round(time.time() - start_time, 2),
        )

    all_web_results = await search_all_sentences(sentences, max_results=5)
    
    global_max_score = 0.0
    global_max_url = None
    global_max_title = None

    matches: List[MatchResult] = []
    sentence_search_results: List[SentenceSearchResult] = []
    matched_count = 0

    for sentence, web_results in zip(sentences, all_web_results):
        sentence_embedding = encode_single(sentence)
        if sentence_embedding.size == 0:
            continue
            
        # 1. Get internal results
        internal_results = search_internal_database(sentence, max_results=3)
        
        # 2. Combine results
        combined_sources = []
        for r in internal_results:
             combined_sources.append({
                 "content": r["content"],
                 "url": r["url"],
                 "title": r["title"]
             })
             
        for r in web_results:
             combined_sources.append({
                 "content": r["content"],
                 "url": r["url"],
                 "title": r["title"]
             })
             
        # 3. Calculate similarities for ALL combined sources
        # We need individual scores to populate SearchedSource
        searched_sources = []
        best_overall_score = 0.0
        best_match_info = None
        
        if combined_sources:
            from app.embedder import encode
            from sklearn.metrics.pairwise import cosine_similarity
            import numpy as np
            
            content_list = [c["content"] for c in combined_sources]
            content_embeddings = encode(content_list)
            
            if len(content_embeddings) > 0:
                scores = cosine_similarity(sentence_embedding.reshape(1, -1), content_embeddings)[0]
                
                for idx, score in enumerate(scores):
                    score = float(score)
                    searched_sources.append(
                        SearchedSource(
                            url=combined_sources[idx]["url"],
                            title=combined_sources[idx]["title"],
                            snippet=combined_sources[idx]["content"][:4000] + ("..." if len(combined_sources[idx]["content"]) > 4000 else ""),
                            similarity=round(score, 4)
                        )
                    )
                    
                    if score > best_overall_score:
                        best_overall_score = score
                        best_match_info = {
                            "url": combined_sources[idx]["url"],
                            "title": combined_sources[idx]["title"],
                            "snippet": combined_sources[idx]["content"][:300] + "...",
                        }
                    
                    # Track global highest match
                    if score > global_max_score:
                        global_max_score = score
                        global_max_url = combined_sources[idx]["url"]
                        global_max_title = combined_sources[idx]["title"]

        # Sort sources by similarity descending
        searched_sources.sort(key=lambda x: x.similarity or 0.0, reverse=True)
        
        # Round the score to avoid floating point precision issues against threshold
        is_plagiarised = round(best_overall_score, 4) >= request.threshold

        
        if is_plagiarised and best_match_info:
            matched_count += 1
            matches.append(
                MatchResult(
                    sentence=sentence,
                    source_url=best_match_info["url"],
                    source_title=best_match_info["title"],
                    similarity=round(best_overall_score, 4),
                    matched_snippet=best_match_info["snippet"],
                    all_sources=searched_sources
                )
            )
            
        sentence_search_results.append(
            SentenceSearchResult(
                sentence=sentence,
                sources=searched_sources,
                best_similarity=round(best_overall_score, 4),
                is_plagiarised=is_plagiarised
            )
        )

    if total_sentences > 0:
        avg_percentage = sum(r.best_similarity for r in sentence_search_results) / total_sentences * 100
        score = round(avg_percentage, 2)
    else:
        score = 0.0

    return PlagiarismReport(
        score=score,
        total_sentences=total_sentences,
        matched_sentences=matched_count,
        matches=sorted(matches, key=lambda m: m.similarity, reverse=True),
        sentence_search_results=sentence_search_results,
        highest_match_score=round(global_max_score * 100, 2),
        highest_match_url=global_max_url,
        highest_match_title=global_max_title,
        processing_time=round(time.time() - start_time, 2),
    )
