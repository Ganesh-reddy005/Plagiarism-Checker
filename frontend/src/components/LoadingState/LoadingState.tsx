"use client";

import React, { useEffect, useState } from "react";

const STEPS = [
  { icon: "🔤", label: "Preprocessing text & splitting sentences" },
  { icon: "🌐", label: "Searching web sources via Tavily" },
  { icon: "🧠", label: "Generating semantic embeddings" },
  { icon: "📐", label: "Computing cosine similarity" },
  { icon: "📊", label: "Aggregating plagiarism score" },
];

export default function LoadingState() {
  const [activeStep, setActiveStep] = useState(0);
  const [doneSteps, setDoneSteps] = useState<number[]>([]);

  useEffect(() => {
    const intervals = STEPS.map((_, i) => {
      return setTimeout(() => {
        setDoneSteps((prev) => [...prev, i - 1].filter((s) => s >= 0));
        setActiveStep(i);
      }, i * 4000);
    });
    return () => intervals.forEach(clearTimeout);
  }, []);

  return (
    <div className="glass-card">
      <div className="loading-wrapper">
        <div className="loading-orb">🔍</div>

        <div style={{ textAlign: "center" }}>
          <div className="loading-title">Analysing Your Text</div>
          <div className="loading-subtitle" style={{ marginTop: 6 }}>
            This may take 20–60 seconds on the first run
          </div>
        </div>

        <div className="loading-steps">
          {STEPS.map((step, i) => {
            const isDone = doneSteps.includes(i);
            const isActive = activeStep === i && !isDone;
            return (
              <div
                key={i}
                className={`loading-step ${isActive ? "active" : ""} ${isDone ? "done" : ""}`}
                style={{ animationDelay: `${i * 0.1}s` }}
              >
                {isDone ? (
                  <span className="step-icon">✅</span>
                ) : isActive ? (
                  <div className="step-spinner" />
                ) : (
                  <span className="step-icon" style={{ opacity: 0.3 }}>
                    {step.icon}
                  </span>
                )}
                <span>{step.label}</span>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}
