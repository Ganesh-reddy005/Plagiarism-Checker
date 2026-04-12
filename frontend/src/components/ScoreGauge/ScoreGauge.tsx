"use client";

import React, { useEffect, useState } from "react";

interface ScoreGaugeProps {
  score: number;
  riskLevel: string;
}

function getGaugeColor(score: number): string {
  if (score < 30) return "#22c55e";
  if (score < 60) return "#f59e0b";
  return "#ef4444";
}

function getRiskClass(riskLevel: string): string {
  const map: Record<string, string> = {
    Low: "risk-low",
    Moderate: "risk-moderate",
    High: "risk-high",
    "Very High": "risk-very-high",
  };
  return map[riskLevel] || "risk-low";
}

export default function ScoreGauge({ score, riskLevel }: ScoreGaugeProps) {
  const [displayScore, setDisplayScore] = useState(0);
  const radius = 54;
  const circumference = 2 * Math.PI * radius;
  const progress = (displayScore / 100) * circumference;
  const strokeColor = getGaugeColor(score);

  // Animate score counter
  useEffect(() => {
    let start = 0;
    const duration = 1500;
    const step = score / (duration / 16);
    const timer = setInterval(() => {
      start += step;
      if (start >= score) {
        setDisplayScore(score);
        clearInterval(timer);
      } else {
        setDisplayScore(Math.round(start));
      }
    }, 16);
    return () => clearInterval(timer);
  }, [score]);

  return (
    <div className="score-row">
      <div className="gauge-wrapper">
        <svg className="gauge-svg" viewBox="0 0 140 140">
          <circle
            className="gauge-track"
            cx="70"
            cy="70"
            r={radius}
          />
          <circle
            className="gauge-fill"
            cx="70"
            cy="70"
            r={radius}
            stroke={strokeColor}
            strokeDasharray={`${progress} ${circumference}`}
            strokeDashoffset={0}
            style={{ filter: `drop-shadow(0 0 8px ${strokeColor}80)` }}
          />
        </svg>
        <div className="gauge-center">
          <span className="gauge-score" style={{ color: strokeColor }}>
            {displayScore}%
          </span>
          <span className="gauge-label">Plagiarised</span>
        </div>
      </div>

      <div className="score-meta">
        <div className={`risk-badge ${getRiskClass(riskLevel)}`}>
          🛡️ {riskLevel} Risk
        </div>
      </div>
    </div>
  );
}
