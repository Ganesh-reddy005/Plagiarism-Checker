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
    <div className="glass-card" style={{ padding: "20px", display: "flex", flexDirection: "column", gap: "12px", height: "100%", overflowY: "auto" }}>
      <h3 style={{ fontFamily: "Space Grotesk", fontSize: "1.1rem", marginBottom: "8px" }}>
        Database & Web Search Breadcrumbs
      </h3>
      <p style={{ fontSize: "0.8rem", color: "var(--text-muted)", marginBottom: "8px", marginTop: "-12px" }}>
        Breakdown of every internal document and external webpage queried per sentence. 
        <span style={{ color: "var(--accent-cyan)", marginLeft: "4px" }}>Click highlighted text to view sources.</span>
      </p>

      {sentenceResults.map((res, i) => (
        <div 
          key={i} 
          ref={el => { itemRefs.current[i] = el; }}
          style={{ 
            background: expandedIndex === i ? "rgba(124, 58, 237, 0.1)" : "rgba(255,255,255,0.03)", 
            border: expandedIndex === i ? "1px solid var(--accent-purple)" : "1px solid var(--border)", 
            borderRadius: "8px",
            overflow: "hidden",
            transition: "all 0.3s ease"
          }}
        >
          <div 
            style={{ padding: "12px 16px", cursor: "pointer", display: "flex", justifyContent: "space-between", alignItems: "flex-start" }}
            onClick={() => toggleExpand(i)}
          >
            <div style={{ flex: 1, fontSize: "0.85rem", fontStyle: "italic", color: res.is_plagiarised ? "var(--danger)" : "var(--text-secondary)", fontWeight: expandedIndex === i ? 600 : 400, lineHeight: "1.4", paddingRight: "12px", overflowWrap: "anywhere", wordBreak: "break-word" }}>
              "{res.sentence}"
            </div>
            <div style={{ display: "flex", alignItems: "center", gap: "12px" }}>
              <span style={{ fontSize: "0.75rem", background: "rgba(0,0,0,0.3)", padding: "2px 8px", borderRadius: "10px" }}>
                {res.sources.length} sources
              </span>
              <span style={{ fontSize: "0.8rem" }}>{expandedIndex === i ? "▲" : "▼"}</span>
            </div>
          </div>
          
          {expandedIndex === i && (
            <div className="custom-scrollbar" style={{ padding: "12px 16px", borderTop: "1px solid var(--border)", background: "rgba(0,0,0,0.2)", display: "flex", flexDirection: "column", gap: "16px", maxHeight: "350px", overflowY: "auto" }}>
              {res.sources.map((src, j) => (
                <div key={j} style={{ fontSize: "0.8rem", display: "flex", flexDirection: "column", gap: "6px", padding: "8px", background: "rgba(255,255,255,0.02)", borderRadius: "6px" }}>
                  <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start" }}>
                    <a href={src.url} target="_blank" rel="noopener noreferrer" style={{ color: "var(--accent-cyan)", textDecoration: "none", display: "flex", gap: "6px", alignItems: "center", flex: 1, paddingRight: "12px" }}>
                      <span>{src.url.startsWith("internal://") ? "🗄️" : "🌐"}</span>
                      <span style={{ wordBreak: "break-all" }}>{src.title || src.url}</span>
                    </a>
                    <span style={{ 
                      fontWeight: 700, 
                      padding: "2px 8px",
                      borderRadius: "12px",
                      background: typeof src.similarity === 'number' && src.similarity >= 0.75 ? "rgba(239, 68, 68, 0.2)" : "rgba(255,255,255,0.05)",
                      color: typeof src.similarity === 'number' && src.similarity >= 0.75 ? "var(--danger)" : "var(--text-secondary)" 
                    }}>
                      {typeof src.similarity === 'number' ? `${(src.similarity * 100).toFixed(1)}%` : "N/A"}
                    </span>
                  </div>
                  <div style={{ color: "var(--text-muted)", fontSize: "0.75rem", lineHeight: "1.5", fontStyle: "italic", borderLeft: "2px solid rgba(255,255,255,0.1)", paddingLeft: "8px", marginTop: "4px", maxHeight: "100px", overflow: "hidden", textOverflow: "ellipsis", display: "-webkit-box", WebkitLineClamp: 4, WebkitBoxOrient: "vertical" }}>
                    {src.snippet}
                  </div>
                </div>
              ))}
              {res.sources.length === 0 && (
                <div style={{ fontSize: "0.8rem", color: "var(--text-muted)", textAlign: "center", padding: "12px" }}>No valid sources retrieved or database is empty.</div>
              )}
            </div>
          )}
        </div>
      ))}
    </div>
  );
}
