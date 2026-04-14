"use client";

import React from "react";
import ScoreGauge from "@/components/ScoreGauge/ScoreGauge";
import MatchCard from "@/components/MatchCard/MatchCard";
import TextHighlighter from "@/components/TextHighlighter/TextHighlighter";
import SourcesPanel from "@/components/SourcesPanel/SourcesPanel";

interface SearchedSource {
  url: string;
  title: string;
  snippet: string;
  similarity: number | null;
}

interface SentenceSearchResult {
  sentence: string;
  sources: SearchedSource[];
  best_similarity: number;
  is_plagiarised: boolean;
}

interface MatchResult {
  sentence: string;
  source_url: string;
  source_title: string;
  similarity: number;
  matched_snippet: string;
  all_sources: SearchedSource[];
}

interface ReportData {
  score: number;
  total_sentences: number;
  matched_sentences: number;
  matches: MatchResult[];
  sentence_search_results: SentenceSearchResult[];
  processing_time: number;
  risk_level: string;
  summary: string;
  check_mode: string;
  highest_match_score: number;
  highest_match_url: string | null;
  highest_match_title: string | null;
}

interface ResultsSectionProps {
  report: ReportData;
  originalText: string;
  onReset: () => void;
}

export default function ResultsSection({ report, originalText, onReset }: ResultsSectionProps) {
  const [activeSentence, setActiveSentence] = React.useState<string | null>(null);

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: "24px" }}>
      {/* Top Banner: Score & Summary */}
      <div className="glass-card" style={{ display: "flex", flexDirection: "column", gap: "24px", padding: "24px" }}>
        <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", gap: "24px", flexWrap: "wrap" }}>
          
          {/* Left Side: Score & Title */}
          <div style={{ display: "flex", alignItems: "center", gap: "24px" }}>
            <ScoreGauge score={report.score} riskLevel={report.risk_level} />
            <div>
              <h2 style={{ fontFamily: "Space Grotesk", fontSize: "1.8rem", margin: "0 0 8px 0" }}>
                Analysis Report
              </h2>
              {/* Check mode badge */}
              <div style={{ display: "inline-flex", alignItems: "center", gap: "6px", padding: "4px 12px", borderRadius: "20px",
                background: report.check_mode === "semantic"
                  ? "rgba(124, 58, 237, 0.15)" : "rgba(6, 182, 212, 0.12)",
                border: `1px solid ${report.check_mode === "semantic" ? "rgba(124,58,237,0.4)" : "rgba(6,182,212,0.35)"}`,
              }}>
                <span style={{ fontSize: "0.85rem" }}>
                  {report.check_mode === "semantic" ? "🧠" : "🔍"}
                </span>
                <span style={{ fontSize: "0.72rem", fontWeight: 600, letterSpacing: "0.04em", textTransform: "uppercase",
                  color: report.check_mode === "semantic" ? "var(--accent-purple-light)" : "var(--accent-cyan-light)"
                }}>
                  {report.check_mode === "semantic" ? "Deep Semantic Check" : "Standard Text Check"}
                </span>
              </div>
            </div>
          </div>
          
          {/* Right Side: Stats */}
          <div className="score-stats" style={{ display: "flex", gap: "24px", minWidth: "200px", padding: "12px 24px", background: "rgba(255,255,255,0.03)", borderRadius: "12px", border: "1px solid var(--border)" }}>
            <div className="stat-item" style={{ display: "flex", flexDirection: "column", alignItems: "center" }}>
              <span className="stat-value" style={{ fontSize: "1.5rem", fontWeight: "bold" }}>{report.total_sentences}</span>
              <span className="stat-label" style={{ fontSize: "0.8rem", color: "var(--text-muted)", textTransform: "uppercase", letterSpacing: "1px" }}>Total</span>
            </div>
            <div className="stat-item" style={{ display: "flex", flexDirection: "column", alignItems: "center" }}>
              <span className="stat-value" style={{ fontSize: "1.5rem", fontWeight: "bold", color: report.matched_sentences > 0 ? "var(--danger)" : "var(--success)" }}>
                {report.matched_sentences}
              </span>
              <span className="stat-label" style={{ fontSize: "0.8rem", color: "var(--text-muted)", textTransform: "uppercase", letterSpacing: "1px" }}>Matched</span>
            </div>
            <div className="stat-item" style={{ display: "flex", flexDirection: "column", alignItems: "center" }}>
              <span className="stat-value" style={{ fontSize: "1.5rem", fontWeight: "bold", color: "var(--accent-cyan)" }}>
                {report.total_sentences - report.matched_sentences}
              </span>
              <span className="stat-label" style={{ fontSize: "0.8rem", color: "var(--text-muted)", textTransform: "uppercase", letterSpacing: "1px" }}>Original</span>
            </div>
            
            <div className="stat-item" style={{ display: "flex", flexDirection: "column", alignItems: "center", borderLeft: "1px solid var(--border)", paddingLeft: "24px" }}>
              <span className="stat-value" style={{ fontSize: "1.5rem", fontWeight: "bold", color: report.highest_match_score > 70 ? "var(--danger)" : "var(--accent-purple)" }}>
                {report.highest_match_score}%
              </span>
              <span className="stat-label" style={{ fontSize: "0.8rem", color: "var(--text-muted)", textTransform: "uppercase", letterSpacing: "1px" }}>Highest Match</span>
              {report.highest_match_url && (
                <a 
                  href={report.highest_match_url} 
                  target="_blank" 
                  rel="noopener noreferrer" 
                  style={{ fontSize: "0.65rem", color: "var(--accent-cyan)", textDecoration: "none", marginTop: "4px", maxWidth: "120px", overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}
                  title={report.highest_match_title || report.highest_match_url}
                >
                  {report.highest_match_url.replace("https://", "").replace("http://", "").split('/')[0]}
                </a>
              )}
            </div>
          </div>
          
        </div>

        {/* AI Executive Summary Full-Width Row */}
        {report.summary && (
          <div style={{ padding: "20px", background: "rgba(255,255,255,0.03)", borderRadius: "12px", borderLeft: "4px solid var(--accent-purple)", fontSize: "0.95rem", lineHeight: "1.6", whiteSpace: "pre-wrap", borderTop: "1px solid var(--border)", borderRight: "1px solid var(--border)", borderBottom: "1px solid var(--border)" }}>
            <div style={{ display: "flex", alignItems: "center", gap: "8px", marginBottom: "12px" }}>
              <span style={{ fontSize: "1.2rem", color: "var(--accent-purple)" }}>✨</span>
              <strong style={{ fontFamily: "Space Grotesk", fontSize: "1.1rem", color: "white" }}>AI Executive Summary & Fixing Advice</strong>
            </div>
            <div style={{ color: "var(--text-secondary)" }}>
              {report.summary}
            </div>
          </div>
        )}
      </div>

      {/* Split Dashboard */}
      <div style={{ 
        display: "grid", 
        gridTemplateColumns: "1fr 1fr", 
        gap: "24px",
        alignItems: "start"
      }}>
        {/* Left: Original Text Highlighter */}
        <div style={{ height: "650px" }}>
          <TextHighlighter 
            originalText={originalText} 
            matches={report.matches} 
            onSentenceClick={(s) => setActiveSentence(s)}
          />
        </div>

        {/* Right: Sources Breakdown */}
        <div style={{ height: "650px" }}>
          <SourcesPanel 
            sentenceResults={report.sentence_search_results} 
            activeSentence={activeSentence}
          />
        </div>
      </div>

      <div className="btn-row" style={{ marginTop: "12px" }}>
        <button
          id="reset-button"
          className="btn-submit"
          onClick={onReset}
          style={{ width: "100%", background: "rgba(255,255,255,0.05)", border: "1px solid var(--border)" }}
        >
          <span className="btn-submit-inner">
            <span className="btn-icon">🔄</span>
            Scan Another Document
          </span>
        </button>
      </div>
    </div>
  );
}
