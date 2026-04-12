"use client";

import React, { useState, useRef, ChangeEvent } from "react";

interface InputSectionProps {
  onSubmit: (text: string, threshold: number, maxSentences: number) => void;
  isLoading: boolean;
}

export default function InputSection({ onSubmit, isLoading }: InputSectionProps) {
  const [text, setText] = useState("");
  const [threshold, setThreshold] = useState(0.75);
  const [maxSentences, setMaxSentences] = useState(10);
  const [isExtracting, setIsExtracting] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleThresholdChange = (e: ChangeEvent<HTMLInputElement>) => {
    const val = parseFloat(e.target.value);
    setThreshold(val);
    // Update CSS custom property for slider fill
    e.target.style.setProperty("--pct", `${val * 100}%`);
  };

  const handleSentenceChange = (e: ChangeEvent<HTMLInputElement>) => {
    const val = parseInt(e.target.value);
    setMaxSentences(val);
    const pct = ((val - 1) / 29) * 100;
    e.target.style.setProperty("--pct", `${pct}%`);
  };

  const handleSubmit = () => {
    if (text.trim().length < 10) return;
    onSubmit(text.trim(), threshold, maxSentences);
  };

  const handleClear = () => {
    setText("");
    if (fileInputRef.current) fileInputRef.current.value = "";
  };

  const handleFileUpload = async (e: ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      const file = e.target.files[0];
      setIsExtracting(true);
      
      const formData = new FormData();
      formData.append("file", file);

      try {
        const res = await fetch("/api/documents/extract-text", {
          method: "POST",
          body: formData,
        });

        if (!res.ok) throw new Error("Failed to extract text");
        
        const data = await res.json();
        setText(data.text);
      } catch (err) {
        console.error("Extraction error:", err);
        alert("Failed to extract text from file. Please try again.");
      } finally {
        setIsExtracting(false);
      }
    }
  };

  const canSubmit = text.trim().length >= 10 && !isLoading && !isExtracting;

  return (
    <div className="input-section glass-card">
      <div className="section-header" style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
        <div style={{ display: "flex", alignItems: "center", gap: "12px" }}>
          <div className="section-icon">📝</div>
          <h2 className="section-title">Enter Your Text</h2>
        </div>
        
        <div style={{ display: "flex", gap: "8px" }}>
          <input 
            type="file" 
            ref={fileInputRef}
            onChange={handleFileUpload}
            accept=".txt,.pdf"
            style={{ display: "none" }}
          />
          <button 
            onClick={() => fileInputRef.current?.click()}
            className="btn-secondary"
            style={{ display: "flex", alignItems: "center", gap: "6px", fontSize: "0.85rem", padding: "8px 14px" }}
            disabled={isLoading || isExtracting}
          >
            <span>📁</span> {isExtracting ? "Reading..." : "Upload Paper"}
          </button>
          <button 
            onClick={handleClear}
            className="btn-secondary"
            style={{ display: "flex", alignItems: "center", gap: "6px", fontSize: "0.85rem", padding: "8px 14px", background: "rgba(255,255,255,0.05)" }}
            disabled={isLoading || isExtracting || !text}
          >
            <span>🗑️</span> Clear
          </button>
        </div>
      </div>

      <div className="textarea-wrapper">
        <textarea
          id="input-text"
          className="main-textarea"
          placeholder="Paste your essay, research paper, or any text here to check for plagiarism..."
          value={text}
          onChange={(e) => setText(e.target.value)}
          rows={8}
          disabled={isLoading || isExtracting}
        />
        <div className="char-count">{text.length} characters</div>
      </div>

      <div className="controls-row">
        <div className="control-group">
          <label className="control-label">
            <span>Similarity Threshold</span>
            <span className="control-value">{(threshold * 100).toFixed(0)}%</span>
          </label>
          <input
            id="threshold-slider"
            type="range"
            className="slider"
            min="0.4"
            max="0.99"
            step="0.01"
            value={threshold}
            onChange={handleThresholdChange}
            style={{ "--pct": `${threshold * 100}%` } as React.CSSProperties}
            disabled={isLoading || isExtracting}
          />
          <span style={{ fontSize: "0.72rem", color: "var(--text-muted)" }}>
            Higher = stricter detection
          </span>
        </div>

        <div className="control-group">
          <label className="control-label">
            <span>Max Sentences</span>
            <span className="control-value">{maxSentences}</span>
          </label>
          <input
            id="sentences-slider"
            type="range"
            className="slider"
            min="1"
            max="30"
            step="1"
            value={maxSentences}
            onChange={handleSentenceChange}
            style={{ "--pct": `${((maxSentences - 1) / 29) * 100}%` } as React.CSSProperties}
            disabled={isLoading || isExtracting}
          />
          <span style={{ fontSize: "0.72rem", color: "var(--text-muted)" }}>
            More sentences = more API calls
          </span>
        </div>
      </div>

      <div className="btn-row">
        <button
          id="check-button"
          className="btn-submit"
          onClick={handleSubmit}
          disabled={!canSubmit}
        >
          <span className="btn-submit-inner">
            <span className="btn-icon">🚀</span>
            {isLoading ? "Analysing..." : "Check for Plagiarism"}
          </span>
        </button>
      </div>
    </div>
  );
}
