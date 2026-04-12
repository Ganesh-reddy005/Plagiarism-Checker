import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "PlagiarismAI — AI-Powered Semantic Plagiarism Detector",
  description:
    "Detect exact and paraphrased plagiarism using real-time web search and semantic embeddings. Powered by Tavily API and Sentence Transformers.",
  keywords: ["plagiarism checker", "AI", "semantic similarity", "plagiarism detector"],
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
