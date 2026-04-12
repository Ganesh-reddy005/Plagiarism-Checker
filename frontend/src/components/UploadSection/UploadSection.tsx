"use client";

import React, { useState } from "react";

export default function UploadSection() {
  const [file, setFile] = useState<File | null>(null);
  const [title, setTitle] = useState("");
  const [status, setStatus] = useState<"idle" | "uploading" | "success" | "error">("idle");
  const [message, setMessage] = useState("");

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setFile(e.target.files[0]);
    }
  };

  const handleUpload = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!file || !title) return;

    setStatus("uploading");
    
    const formData = new FormData();
    formData.append("title", title);
    formData.append("file", file);

    try {
      const res = await fetch("/api/documents/upload", {
        method: "POST",
        body: formData,
      });

      if (!res.ok) {
        throw new Error(await res.text());
      }

      const data = await res.json();
      setStatus("success");
      setMessage(`Successfully indexed ${data.sentences_indexed} sentences into the Internal Database.`);
      setFile(null);
      setTitle("");
    } catch (err: any) {
      setStatus("error");
      setMessage(err.message || "Upload failed");
    }
  };

  return (
    <div className="glass-card" style={{ padding: "24px", marginBottom: "32px", borderTop: "4px solid var(--accent-purple)" }}>
      <div style={{ display: "flex", alignItems: "center", gap: "12px", marginBottom: "16px" }}>
        <span style={{ fontSize: "1.5rem" }}>🗄️</span>
        <h3 style={{ fontFamily: "Space Grotesk", fontSize: "1.1rem" }}>
          Internal Database (Knowledge Base)
        </h3>
      </div>
      <p style={{ fontSize: "0.85rem", color: "var(--text-muted)", marginBottom: "20px" }}>
        Upload internal reference documents (e.g. past research papers). The AI will cross-reference future scans against these documents securely using Qdrant vector search.
      </p>

      <form onSubmit={handleUpload} style={{ display: "flex", gap: "16px", flexWrap: "wrap", alignItems: "flex-end" }}>
        <div style={{ flex: 1, minWidth: "200px" }}>
          <label style={{ display: "block", fontSize: "0.8rem", color: "var(--text-secondary)", marginBottom: "8px" }}>Document Title</label>
          <input 
            type="text" 
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            style={{ width: "100%", padding: "10px", background: "rgba(0,0,0,0.3)", border: "1px solid var(--border)", borderRadius: "8px", color: "white" }}
            placeholder="e.g. Thesis 2024 - John Doe"
            required
          />
        </div>
        <div style={{ flex: 1, minWidth: "200px" }}>
          <label style={{ display: "block", fontSize: "0.8rem", color: "var(--text-secondary)", marginBottom: "8px" }}>File (PDF/TXT)</label>
          <input 
            type="file" 
            accept=".txt,.pdf"
            onChange={handleFileChange}
            style={{ width: "100%", padding: "8px", background: "rgba(0,0,0,0.3)", border: "1px solid var(--border)", borderRadius: "8px", color: "white" }}
            required
          />
        </div>
        <div style={{ width: "120px" }}>
          <button 
            type="submit" 
            disabled={status === "uploading"}
            className="btn-submit"
            style={{ padding: "10px 16px", opacity: status === "uploading" ? 0.5 : 1 }}
          >
            {status === "uploading" ? "Indexing..." : "Upload & Index"}
          </button>
        </div>
      </form>

      {status === "success" && (
        <div style={{ marginTop: "16px", padding: "12px", background: "rgba(34, 197, 94, 0.1)", color: "var(--success)", borderRadius: "6px", fontSize: "0.85rem", border: "1px solid rgba(34,197,94,0.3)" }}>
          ✅ {message}
        </div>
      )}
      {status === "error" && (
        <div style={{ marginTop: "16px", padding: "12px", background: "rgba(239, 68, 68, 0.1)", color: "var(--danger)", borderRadius: "6px", fontSize: "0.85rem", border: "1px solid rgba(239,68,68,0.3)" }}>
          ⚠️ {message}
        </div>
      )}
    </div>
  );
}
