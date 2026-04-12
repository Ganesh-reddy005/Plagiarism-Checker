"""
Pydantic models for request/response schemas.
"""
from __future__ import annotations

from typing import List, Optional
from pydantic import BaseModel, ConfigDict, Field


class CheckRequest(BaseModel):
    text: str = Field(..., description="Text to check for plagiarism", min_length=10)
    threshold: float = Field(default=0.75, ge=0.0, le=1.0, description="Similarity threshold (0-1)")
    max_sentences: int = Field(default=10, ge=1, le=30, description="Max sentences to analyse")


class SearchedSource(BaseModel):
    """A single URL that was found during web search for a sentence."""
    url: str
    title: str = ""
    snippet: str = ""
    similarity: Optional[float] = None   # filled if compared; None if skipped


class SentenceSearchResult(BaseModel):
    """All sources retrieved for one input sentence."""
    sentence: str
    sources: List[SearchedSource] = Field(default_factory=list)
    best_similarity: float = 0.0
    is_plagiarised: bool = False


class MatchResult(BaseModel):
    sentence: str = Field(..., description="Original sentence from input")
    source_url: str = Field(..., description="URL of potential source")
    source_title: str = Field(default="", description="Page title of source")
    similarity: float = Field(..., description="Cosine similarity score (0-1)")
    matched_snippet: str = Field(..., description="Most similar snippet from source")
    all_sources: List[SearchedSource] = Field(
        default_factory=list,
        description="All sources found for this sentence"
    )


class PlagiarismReport(BaseModel):
    score: float = Field(..., description="Overall plagiarism score (0-100)")
    total_sentences: int = Field(..., description="Total sentences analysed")
    matched_sentences: int = Field(..., description="Sentences flagged as plagiarised")
    matches: List[MatchResult] = Field(default_factory=list)
    sentence_search_results: List[SentenceSearchResult] = Field(
        default_factory=list,
        description="All searched sources per sentence"
    )
    highest_match_score: float = Field(default=0.0, description="Highest similarity score found in any source")
    highest_match_url: Optional[str] = Field(default=None, description="URL of the highest match source")
    highest_match_title: Optional[str] = Field(default=None, description="Title of the highest match source")
    processing_time: float = Field(..., description="Processing time in seconds")


class HealthResponse(BaseModel):
    model_config = ConfigDict(protected_namespaces=())
    status: str
    model_loaded: bool
