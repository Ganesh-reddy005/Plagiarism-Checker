# AI-Powered Semantic Plagiarism Checker

Detects exact and paraphrased plagiarism using real-time web search (Tavily API) and semantic embeddings (Sentence Transformers).

---

## 🚀 Quick Start

### 1. Backend Setup

```bash
cd backend

# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set your Tavily API key
cp .env.example .env
# Edit .env and add your key: TAVILY_API_KEY=tvly-your-key-here
# Get a free key at https://tavily.com

# Start the backend server
uvicorn main:app --reload --port 8000
```

### 2. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Start the development server
npm run dev
```

### 3. Open the App

Navigate to **http://localhost:3000** in your browser.

---

## 🏗️ Architecture

```
plagiarism_checker/
├── backend/
│   ├── main.py                  # FastAPI entry point
│   ├── requirements.txt
│   ├── .env                     # Your Tavily API key (not committed)
│   └── app/
│       ├── models.py            # Pydantic schemas
│       ├── preprocessor.py      # Text cleaning + sentence splitting
│       ├── web_searcher.py      # Tavily API integration
│       ├── embedder.py          # Sentence Transformers (all-MiniLM-L6-v2)
│       ├── similarity.py        # Cosine similarity computation
│       ├── detector.py          # Pipeline orchestration
│       └── reporter.py          # Report enrichment
└── frontend/
    └── src/
        ├── app/
        │   ├── layout.tsx
        │   ├── page.tsx         # Main page
        │   └── globals.css      # Full design system
        └── components/
            ├── Navbar/
            ├── InputSection/    # Text + controls
            ├── LoadingState/    # Animated scanning UI
            ├── ScoreGauge/      # Circular score gauge
            ├── MatchCard/       # Individual match result
            └── ResultsSection/  # Full results view
```

## 🔑 API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/health` | Health check |
| POST | `/api/check` | Run plagiarism detection |

### POST `/api/check` Body

```json
{
  "text": "Your text here",
  "threshold": 0.75,
  "max_sentences": 10
}
```

## ⚠️ Notes

- First model load takes ~30s (downloaded once, then cached)
- Free Tavily tier: 1000 searches/month
- Accuracy depends on embedding model and web search quality
