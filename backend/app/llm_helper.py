"""
LLM Helper module for generating intelligent summaries using Groq.
"""
import os
from typing import Optional, List, Dict
import json
from groq import Groq
from app.models import PlagiarismReport

_groq_client: Optional[Groq] = None

def get_groq_client() -> Optional[Groq]:
    global _groq_client
    if _groq_client is None:
        api_key = os.getenv("GROQ_LLM_API")
        if api_key and not api_key.startswith("groq-your"):
            _groq_client = Groq(api_key=api_key)
    return _groq_client

def generate_search_queries(text: str, max_queries: int = 15) -> List[Dict[str, str]]:
    """
    Analyses the input text and generates a list of search queries to find potential plagiarism.
    Returns a list of dicts like: [{"query": "theory of relativity einstein mass energy", "type": "academic"}]
    """
    client = get_groq_client()
    if not client:
        # Fallback if no LLM: just return some basic chunked queries of the text and assign half to web, half to academic
        print("[llm_helper] No Groq client. Using fallback query generation.")
        words = text.split()
        chunks = [" ".join(words[i:i+10]) for i in range(0, len(words), max(10, len(words)//10))]
        queries = []
        for i, chunk in enumerate(chunks[:max_queries]):
            queries.append({
                "query": chunk,
                "type": "academic" if i % 2 == 0 else "web"
            })
        return queries

    prompt = f"""
You are an expert plagiarism detection system. Your task is to analyze the provided text and conceptualize targeted search queries to locate its original source if it was plagiarized or heavily paraphrased.

Instructions:
1. Identify unique claims, specific arguments, highly specific technical phrases, and core concepts.
2. Generate up to {max_queries} distinct search queries.
3. Categorize each query as either 'web' (for general internet search) or 'academic' (for research paper databases).
4. Do NOT use quotes in your queries unless it's a highly distinctive 3-4 word phrase. Use combinations of 4-8 keywords.

Format exactly as a valid JSON object with a "queries" key containing an array of objects:
{{
  "queries": [
    {{"query": "the exact search string", "type": "web"}},
    {{"query": "another search string", "type": "academic"}}
  ]
}}

Text to analyze:
{text[:4000]}
"""
    try:
        chat_completion = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="llama-3.3-70b-versatile",
            temperature=0.2,
            response_format={"type": "json_object"},
            max_tokens=1024,
        )
        content = chat_completion.choices[0].message.content.strip()
        data = json.loads(content)
        return data.get("queries", [])
    except Exception as e:
        print(f"[llm_helper] Error generating queries: {e}")
        return []


def generate_report_summary(report: PlagiarismReport) -> str:
    """
    Generate an intelligent summary of the plagiarism report using Groq.
    If Groq is not configured or fails, returns a default summary.
    """
    client = get_groq_client()
    
    default_summary = (
        f"Analysed {report.total_sentences} sentences in {report.processing_time}s. "
        f"{report.matched_sentences} matched with an overall score of {report.score:.1f}%."
    )
    
    if not client:
        return default_summary

    # Extract top 5 sources from across ALL sentences to give the LLM deep context
    all_sources = []
    for sentence_result in report.sentence_search_results:
        for src in sentence_result.sources:
            if src.similarity:
                all_sources.append(src)
                
    # Sort descending by similarity
    all_sources.sort(key=lambda s: s.similarity, reverse=True)
    
    unique_sources = []
    seen_urls = set()
    for src in all_sources:
        if src.url not in seen_urls:
            unique_sources.append(src)
            seen_urls.add(src.url)
        if len(unique_sources) >= 5:
            break
            
    source_details = []
    for i, src in enumerate(unique_sources):
        source_details.append(f"Source {i+1}: {src.url} (Similarity: {src.similarity*100:.1f}%)\nSnippet Context: {src.snippet}")
        
    sources_text = "\n\n".join(source_details) if source_details else "No external sources retrieved."
    
    prompt = f"""
You are an expert AI Plagiarism Analyst and Writing Tutor. Review the results of a plagiarism detection scan.

Scan Results:
- Total Sentences: {report.total_sentences}
- Plagiarised Threshold Hits: {report.matched_sentences}
- Overall Plagiarism Score (Average Similarity): {report.score:.1f}%

Top Sources Found (with context snippets):
{sources_text}

Provide a short summary in 2 parts:
1. Summary of Matches: Briefly state what was found to be the same and from which primary sources. Use the Top Sources Found above to explain where the similarities came from. Explain that the overall score reflects the average similarity of the text to these sources.
2. How to Fix It: Provide 1-2 actionable suggestions on how the author can rewrite or paraphrase the original text to be completely plagiarism-free, considering the actual source context provided above. Be specific about what concepts need to be reworded.

Do not use markdown formatting like bolding or headers, just use plain text with line breaks between the two sections.
"""
    try:
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
            model="llama-3.3-70b-versatile", # Fast and capable standard model on Groq
            temperature=0.3,
            max_tokens=1000,
        )
        return chat_completion.choices[0].message.content.strip()
    except Exception as e:
        print(f"[llm_helper] Error generating summary with Groq: {e}")
        return default_summary
