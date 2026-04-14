import React, { useState, useEffect, useRef } from "react";

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

interface SourcesPanelProps {
  sentenceResults: SentenceSearchResult[];
  activeSentence?: string | null;
}

export default function SourcesPanel({ sentenceResults, activeSentence }: SourcesPanelProps) {
  const [expandedIndex, setExpandedIndex] = useState<number | null>(null);
  const itemRefs = useRef<(HTMLDivElement | null)[]>([]);

  useEffect(() => {
    if (activeSentence) {
      const index = sentenceResults.findIndex(r => r.sentence === activeSentence);
      if (index !== -1) {
        setExpandedIndex(index);
        itemRefs.current[index]?.scrollIntoView({ behavior: 'smooth', block: 'start' });
      }
    }
  }, [activeSentence, sentenceResults]);

  const toggleExpand = (index: number) => {
    setExpandedIndex(expandedIndex === index ? null : index);
  };

  return (
    <div className="glass-card" style={{ padding: "20px", height: "100%", overflowY: "auto", boxSizing: "border-box" }}>
      {/* Fixed header — not part of scrollable flow */}
      <h3 style={{ fontFamily: "Space Grotesk", fontSize: "1.1rem", marginBottom: "6px" }}>
        Database &amp; Web Search Breadcrumbs
      </h3>
      <p style={{ fontSize: "0.8rem", color: "var(--text-muted)", marginBottom: "16px" }}>
        Breakdown of every internal document and external webpage queried per sentence.{" "}
        <span style={{ color: "var(--accent-cyan)" }}>Click highlighted text to view sources.</span>
      </p>

      {/* Accordion list — each item has flex-shrink: 0 so it never squashes */}
      <div style={{ display: "flex", flexDirection: "column", gap: "10px" }}>
        {sentenceResults.map((res, i) => (
          <div
            key={i}
            ref={el => { itemRefs.current[i] = el; }}
            style={{
              flexShrink: 0,
              background: expandedIndex === i ? "rgba(124, 58, 237, 0.1)" : "rgba(255,255,255,0.03)",
              border: expandedIndex === i ? "1px solid var(--accent-purple)" : "1px solid var(--border)",
              borderRadius: "8px",
              transition: "background 0.3s ease, border-color 0.3s ease",
            }}
          >
            {/* Row header — always visible */}
            <div
              style={{ padding: "12px 16px", cursor: "pointer", display: "flex", justifyContent: "space-between", alignItems: "flex-start", gap: "12px" }}
              onClick={() => toggleExpand(i)}
            >
              <div style={{
                flex: 1,
                minWidth: 0,
                fontSize: "0.85rem",
                fontStyle: "italic",
                color: res.is_plagiarised ? "var(--danger)" : "var(--text-secondary)",
                fontWeight: expandedIndex === i ? 600 : 400,
                lineHeight: "1.5",
                wordBreak: "break-word",
                overflowWrap: "anywhere",
              }}>
                &ldquo;{res.sentence}&rdquo;
              </div>
              <div style={{ display: "flex", alignItems: "center", gap: "8px", flexShrink: 0, paddingTop: "2px" }}>
                <span style={{ fontSize: "0.72rem", background: "rgba(0,0,0,0.3)", padding: "2px 8px", borderRadius: "10px", whiteSpace: "nowrap", color: "var(--text-muted)" }}>
                  {res.sources.length} src
                </span>
                <span style={{ fontSize: "0.75rem", color: "var(--text-muted)" }}>{expandedIndex === i ? "▲" : "▼"}</span>
              </div>
            </div>

            {/* Expanded sources list */}
            {expandedIndex === i && (
              <div style={{ borderTop: "1px solid var(--border)", background: "rgba(0,0,0,0.2)", padding: "12px 16px", display: "flex", flexDirection: "column", gap: "12px", maxHeight: "320px", overflowY: "auto" }}>
                {res.sources.length === 0 && (
                  <div style={{ fontSize: "0.8rem", color: "var(--text-muted)", textAlign: "center", padding: "12px" }}>
                    No valid sources retrieved.
                  </div>
                )}
                {res.sources.map((src, j) => (
                  <div key={j} style={{ fontSize: "0.8rem", display: "flex", flexDirection: "column", gap: "6px", padding: "8px", background: "rgba(255,255,255,0.02)", borderRadius: "6px" }}>
                    <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", gap: "8px" }}>
                      <a
                        href={src.url}
                        target="_blank"
                        rel="noopener noreferrer"
                        style={{ color: "var(--accent-cyan)", textDecoration: "none", display: "flex", gap: "6px", alignItems: "flex-start", flex: 1, minWidth: 0 }}
                      >
                        <span style={{ flexShrink: 0 }}>{src.url.startsWith("internal://") ? "🗄️" : "🌐"}</span>
                        <span style={{ wordBreak: "break-all", lineHeight: "1.4" }}>{src.title || src.url}</span>
                      </a>
                      <span style={{
                        flexShrink: 0,
                        fontWeight: 700,
                        padding: "2px 8px",
                        borderRadius: "12px",
                        fontSize: "0.78rem",
                        background: typeof src.similarity === "number" && src.similarity >= 0.75 ? "rgba(239, 68, 68, 0.2)" : "rgba(255,255,255,0.05)",
                        color: typeof src.similarity === "number" && src.similarity >= 0.75 ? "var(--danger)" : "var(--text-secondary)",
                      }}>
                        {typeof src.similarity === "number" ? `${(src.similarity * 100).toFixed(1)}%` : "N/A"}
                      </span>
                    </div>
                    <div style={{
                      color: "var(--text-muted)",
                      fontSize: "0.75rem",
                      lineHeight: "1.5",
                      fontStyle: "italic",
                      borderLeft: "2px solid rgba(255,255,255,0.1)",
                      paddingLeft: "8px",
                      marginTop: "2px",
                      display: "-webkit-box",
                      WebkitLineClamp: 4,
                      WebkitBoxOrient: "vertical",
                      overflow: "hidden",
                    }}>
                      {src.snippet}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}
