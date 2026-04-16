"""
Detector module — orchestrates the full plagiarism detection pipeline.
"""
from __future__ import annotations

import time
import asyncio
from typing import List, Dict

from app.embedder import encode_single, encode
from app.models import CheckRequest, MatchResult, PlagiarismReport, SentenceSearchResult, SearchedSource
from app.preprocessor import preprocess
from app.similarity import compute_similarity_for_results, compute_standard_similarity
from app.web_searcher import search_all_sentences
from app.database import search_internal_database
from app.llm_helper import generate_search_queries
from app.openalex_searcher import search_openalex
from sklearn.metrics.pairwise import cosine_similarity

async def run_detection(request: CheckRequest) -> PlagiarismReport:
    """
    Full pipeline:
    1. Preprocess → sentences
    2. Phase 1: LLM Query Generation (Web + Academic)
    3. Phase 2: Concurrent Evidence Gathering (Tavily, OpenAlex, Internal DB)
    4. Phase 3: Compare each sentence against gathered Evidence Pool
    5. Aggregate score & build report
    """
    start_time = time.time()
    is_semantic = request.check_mode == "semantic"

    sentences = preprocess(request.text, max_sentences=request.max_sentences)
    total_sentences = len(sentences)

    if total_sentences == 0:
        return PlagiarismReport(
            score=0.0,
            total_sentences=0,
            matched_sentences=0,
            matches=[],
            processing_time=round(time.time() - start_time, 2),
            check_mode=request.check_mode,
            risk_level="Low",
        )

    # Phase 1: Generate Queries Contextually using max_sentences as the requested query limit
    llm_queries = generate_search_queries(request.text, max_queries=request.max_sentences)
    web_queries = [q["query"] for q in llm_queries if q.get("type", "web") == "web"]
    academic_queries = [q["query"] for q in llm_queries if q.get("type") == "academic"]
    
    if not web_queries and not academic_queries:
        # Fallback to literal sentences if LLM failed completely
        web_queries = sentences[:5]

    # Phase 2: Evidence Gathering
    # 2a. Web Search (Tavily)
    all_web_results = await search_all_sentences(web_queries, max_results=3)
    
    # 2b. Academic Search (OpenAlex)
    if academic_queries:
        openalex_tasks = [search_openalex(q, max_results=3) for q in academic_queries]
        all_academic_results = await asyncio.gather(*openalex_tasks)
    else:
        all_academic_results = []
        
    # 2c. Internal Search (Qdrant)
    all_internal_results = []
    all_queries = web_queries + academic_queries
    for q in all_queries:
        # DB search is fast locally
        internal_res = search_internal_database(q, max_results=3)
        if internal_res:
            all_internal_results.append(internal_res)

    # 2d. Pool aggregation
    global_sources_pool = []
    seen_urls = set()
    
    def add_to_pool(results_list_of_lists):
        for res_group in results_list_of_lists:
            for r in res_group:
                url = r.get("url", "")
                if url and url not in seen_urls:
                    seen_urls.add(url)
                    global_sources_pool.append({
                        "content": r["content"], 
                        "url": url, 
                        "title": r.get("title", "")
                    })

    add_to_pool(all_web_results)
    add_to_pool([res for res in all_academic_results]) # already list of lists
    add_to_pool([res for res in all_internal_results])
    
    # Phase 3: Setup Embeddings for Semantic Match
    pool_embeddings = None
    if is_semantic and global_sources_pool:
        content_list = [c["content"] for c in global_sources_pool]
        pool_embeddings = encode(content_list)

    global_max_score = 0.0
    global_max_url = None
    global_max_title = None

    matches: List[MatchResult] = []
    sentence_search_results: List[SentenceSearchResult] = []
    matched_count = 0

    # Phase 4: Sentence Evaluation
    for sentence in sentences:
        searched_sources = []
        best_overall_score = 0.0
        best_match_info = None

        if is_semantic:
            sentence_embedding = encode_single(sentence)
            if sentence_embedding.size > 0 and pool_embeddings is not None and len(pool_embeddings) > 0:
                scores = cosine_similarity(sentence_embedding.reshape(1, -1), pool_embeddings)[0]
                for idx, score in enumerate(scores):
                    score = float(score)
                    searched_sources.append(
                        SearchedSource(
                            url=global_sources_pool[idx]["url"],
                            title=global_sources_pool[idx]["title"],
                            snippet=global_sources_pool[idx]["content"][:4000] + ("..." if len(global_sources_pool[idx]["content"]) > 4000 else ""),
                            similarity=round(score, 4),
                        )
                    )
                    if score > best_overall_score:
                        best_overall_score = score
                        best_match_info = {
                            "url": global_sources_pool[idx]["url"],
                            "title": global_sources_pool[idx]["title"],
                            "snippet": global_sources_pool[idx]["content"][:300] + "...",
                        }
                    if score > global_max_score:
                        global_max_score = score
                        global_max_url = global_sources_pool[idx]["url"]
                        global_max_title = global_sources_pool[idx]["title"]
        else:
            # Standard Text Overlap
            for src in global_sources_pool:
                score = compute_standard_similarity(sentence, src["content"])
                searched_sources.append(
                    SearchedSource(
                        url=src["url"],
                        title=src["title"],
                        snippet=src["content"][:4000] + ("..." if len(src["content"]) > 4000 else ""),
                        similarity=round(score, 4),
                    )
                )
                if score > best_overall_score:
                    best_overall_score = score
                    best_match_info = {
                        "url": src["url"],
                        "title": src["title"],
                        "snippet": src["content"][:300] + "...",
                    }
                if score > global_max_score:
                    global_max_score = score
                    global_max_url = src["url"]
                    global_max_title = src["title"]

        searched_sources.sort(key=lambda x: x.similarity or 0.0, reverse=True)
        # To avoid massive payloads, keep only top 3 candidate sources per sentence response
        top_searched_sources = searched_sources[:3]

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
                    all_sources=top_searched_sources,
                )
            )

        sentence_search_results.append(
            SentenceSearchResult(
                sentence=sentence,
                sources=top_searched_sources,
                best_similarity=round(best_overall_score, 4),
                is_plagiarised=is_plagiarised,
            )
        )

    if total_sentences > 0:
        avg_percentage = (sum(r.best_similarity for r in sentence_search_results) / total_sentences * 100)
        score = round(avg_percentage, 2)
    else:
        score = 0.0

    if score >= 75:
        risk_level = "Very High"
    elif score >= 50:
        risk_level = "High"
    elif score >= 25:
        risk_level = "Moderate"
    else:
        risk_level = "Low"

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
        check_mode=request.check_mode,
        risk_level=risk_level,
    )
