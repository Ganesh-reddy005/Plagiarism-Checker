import React, { useEffect, useRef } from "react";

interface MatchResult {
  sentence: string;
  source_url: string;
  similarity: number;
}

interface TextHighlighterProps {
  originalText: string;
  matches: MatchResult[];
  onSentenceClick?: (sentence: string) => void;
}

export default function TextHighlighter({ originalText, matches, onSentenceClick }: TextHighlighterProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  
  // Sort matches by length descending so we don't partially replace sub-sentences
  const sortedMatches = [...matches].sort((a, b) => b.sentence.length - a.sentence.length);
  
  let highlightedHtml = originalText
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;");

  sortedMatches.forEach((match) => {
    // Generate a fuzzy regex that treats any whitespace in the sentence as \s+
    // This allows matching even if the original text has extra spaces or newlines
    const escapedSentence = match.sentence.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
    const fuzzyRegex = escapedSentence.split(/\\s+/).join('\\s+');
    
    let colorClass = "highlight-low";
    if (match.similarity >= 0.85) colorClass = "highlight-high";
    else if (match.similarity >= 0.70) colorClass = "highlight-med";
    
    // We add a class and a data attribute so we can catch the click
    const replacement = `<span class="${colorClass}" data-sentence="${match.sentence.replace(/"/g, '&quot;')}" style="cursor: pointer;" title="${(match.similarity*100).toFixed(1)}% match (Click to view sources)">$1</span>`;
    
    highlightedHtml = highlightedHtml.replace(
      new RegExp(`(${fuzzyRegex})`, 'g'),
      replacement
    );
  });

  // Preserve line breaks
  highlightedHtml = highlightedHtml.replace(/\n/g, '<br />');

  useEffect(() => {
    const container = containerRef.current;
    if (!container || !onSentenceClick) return;

    const handleClick = (e: MouseEvent) => {
      const target = e.target as HTMLElement;
      if (target.tagName.toLowerCase() === 'span' && target.dataset.sentence) {
        onSentenceClick(target.dataset.sentence);
      }
    };

    container.addEventListener("click", handleClick);
    return () => container.removeEventListener("click", handleClick);
  }, [onSentenceClick, highlightedHtml]);

  return (
    <div className="glass-card" style={{ padding: "24px", height: "100%", overflowY: "auto" }}>
      <h3 style={{ marginBottom: "16px", fontFamily: "Space Grotesk", fontSize: "1.1rem" }}>
        Original Text Analysis
      </h3>
      <div 
        ref={containerRef}
        style={{ lineHeight: "1.8", color: "var(--text-primary)", fontSize: "0.95rem" }}
        dangerouslySetInnerHTML={{ __html: highlightedHtml }}
      />
    </div>
  );
}
