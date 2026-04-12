// components/Navbar/Navbar.tsx
import React from "react";

export default function Navbar() {
  return (
    <nav className="navbar">
      <div className="navbar-inner">
        <a href="/" className="navbar-logo">
          <div className="navbar-logo-icon">🔍</div>
          <span className="navbar-logo-text">PlagiarismAI</span>
        </a>
        <div className="navbar-badge">
          <div className="badge-dot" />
          AI-Powered Detection
        </div>
      </div>
    </nav>
  );
}
