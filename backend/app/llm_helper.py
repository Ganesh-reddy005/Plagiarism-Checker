"""
LLM Helper module for generating intelligent summaries using Groq.
"""
import os
from typing import Optional
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
