"""
Reporter module — formats and enriches the plagiarism report.
"""
from __future__ import annotations

from app.models import PlagiarismReport
from app.llm_helper import generate_report_summary

def get_risk_level(score: float) -> str:
    """Return a human-readable risk level."""
    if score < 20:
        return "Low"
    elif score < 50:
        return "Moderate"
    elif score < 75:
        return "High"
    else:
        return "Very High"


def format_report_summary(report: PlagiarismReport) -> dict:
    """
    Add human-readable metadata to the raw report.
    Returns an enriched dict for the API response.
    """
    summary_text = generate_report_summary(report)
    
    return {
        **report.model_dump(),
        "risk_level": get_risk_level(report.score),
        "summary": summary_text,
    }
