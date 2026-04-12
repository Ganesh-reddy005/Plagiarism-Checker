"use client";

import React, { useState } from "react";
import Navbar from "@/components/Navbar/Navbar";
import InputSection from "@/components/InputSection/InputSection";
import LoadingState from "@/components/LoadingState/LoadingState";
import ResultsSection from "@/components/ResultsSection/ResultsSection";
import UploadSection from "@/components/UploadSection/UploadSection";

type AppState = "idle" | "loading" | "results" | "error";

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

interface ReportData {
  score: number;
  total_sentences: number;
  matched_sentences: number;
  matches: Array<{
    sentence: string;
    source_url: string;
    source_title: string;
    similarity: number;
    matched_snippet: string;
    all_sources: SearchedSource[];
  }>;
  sentence_search_results: SentenceSearchResult[];
  processing_time: number;
  risk_level: string;
  summary: string;
}

export default function HomePage() {
  const [appState, setAppState] = useState<AppState>("idle");
  const [report, setReport] = useState<ReportData | null>(null);
  const [originalText, setOriginalText] = useState("");
  const [errorMsg, setErrorMsg] = useState("");

  const handleSubmit = async (
    text: string,
    threshold: number,
    maxSentences: number
  ) => {
    setAppState("loading");
    setErrorMsg("");
    setOriginalText(text);

    try {
      const res = await fetch("/api/check", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text, threshold, max_sentences: maxSentences }),
      });

      if (!res.ok) {
        const errData = await res.json().catch(() => ({}));
        throw new Error(errData.detail || `Server error: ${res.status}`);
      }

      const data: ReportData = await res.json();
      setReport(data);
      setAppState("results");
    } catch (err: unknown) {
      const message =
        err instanceof Error ? err.message : "Unexpected error occurred.";
      setErrorMsg(message);
      setAppState("error");
    }
  };

  const handleReset = () => {
    setAppState("idle");
    setReport(null);
    setOriginalText("");
    setErrorMsg("");
  };

  return (
    <>
      <div className="bg-mesh" />
      <div className="page-wrapper">
        <Navbar />

        <main>
          <div className="container">
            {/* Hero */}
            <section className="hero">
              <div className="hero-eyebrow">✨ Semantic AI Detection</div>
              <h1 className="hero-title">
                <span className="hero-title-gradient">
                  AI-Powered Plagiarism
                  <br />
                  Checker
                </span>
              </h1>
              <p className="hero-subtitle">
                Detect copied and paraphrased content using real-time web
                search, internal databases, and semantic AI.
              </p>
            </section>

            {/* Main content */}
            {appState === "idle" && (
              <>
                <UploadSection />
                <InputSection onSubmit={handleSubmit} isLoading={false} />
              </>
            )}

            {appState === "loading" && <LoadingState />}

            {appState === "results" && report && (
              <ResultsSection report={report} originalText={originalText} onReset={handleReset} />
            )}

            {appState === "error" && (
              <div className="glass-card">
                <div className="error-card">
                  <div className="error-icon">⚠️</div>
                  <div className="error-title">Something went wrong</div>
                  <p className="error-message">{errorMsg}</p>
                  <button className="btn-retry" onClick={handleReset}>
                    Try Again
                  </button>
                </div>
              </div>
            )}
          </div>
        </main>

        {/* Footer */}
        <footer className="footer">
          <p>
            Built with FastAPI + Sentence Transformers + Tavily API ·{" "}
            <a
              href="https://tavily.com"
              target="_blank"
              rel="noopener noreferrer"
            >
              Tavily
            </a>
          </p>
        </footer>
      </div>
    </>
  );
}
