"use client";

import React from "react";

interface MatchCardProps {
  sentence: string;
  sourceUrl: string;
  similarity: number;
  matchedSnippet: string;
  index: number;
}

function getScoreClass(similarity: number): string {
  if (similarity >= 0.85) return "score-high";
  if (similarity >= 0.7) return "score-medium";
  return "score-low";
}

function getBarColor(similarity: number): string {
  if (similarity >= 0.85) return "var(--danger)";
  if (similarity >= 0.7) return "var(--warning)";
  return "var(--success)";
}

function truncateUrl(url: string, max = 60): string {
  try {
    const parsed = new URL(url);
    const display = parsed.hostname + parsed.pathname;
    return display.length > max ? display.slice(0, max) + "…" : display;
  } catch {
    return url.length > max ? url.slice(0, max) + "…" : url;
  }
}

export default function MatchCard({
  sentence,
  sourceUrl,
  similarity,
  matchedSnippet,
  index,
}: MatchCardProps) {
  const scoreClass = getScoreClass(similarity);
  const barColor = getBarColor(similarity);
  const barWidth = `${(similarity * 100).toFixed(1)}%`;

  return (
    <div
      className="match-card"
      style={{ animationDelay: `${index * 0.08}s` }}
    >
      {/* Header: sentence + score pill */}
      <div className="match-card-header">
        <p className="match-sentence">"{sentence}"</p>
        <span className={`match-score-pill ${scoreClass}`}>
          {(similarity * 100).toFixed(1)}%
        </span>
      </div>

      {/* Similarity bar */}
      <div className="similarity-bar-wrapper">
        <div className="similarity-bar-bg">
          <div
            className="similarity-bar-fill"
            style={{ width: barWidth, background: barColor }}
          />
        </div>
      </div>

      {/* Matched snippet */}
      {matchedSnippet && (
        <div className="match-snippet">
          <div className="snippet-label">Matched Snippet</div>
          {matchedSnippet}
        </div>
      )}

      {/* Source URL */}
      <div className="match-footer">
        <span className="source-icon">🔗</span>
        <a
          href={sourceUrl}
          className="source-url"
          target="_blank"
          rel="noopener noreferrer"
          title={sourceUrl}
        >
          {truncateUrl(sourceUrl)}
        </a>
      </div>
    </div>
  );
}
