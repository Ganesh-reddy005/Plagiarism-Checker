"""
FastAPI entry point.
Defines routes and configures CORS + lifespan events.
"""
from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from app.detector import run_detection
from app.embedder import get_local_model, get_openai_client, _OPENROUTER_MODEL
from app.models import CheckRequest, HealthResponse
from app.reporter import format_report_summary


# ---------------------------------------------------------------------------
# Lifespan: warm-up the embedding model on startup so first request is fast
# ---------------------------------------------------------------------------
@asynccontextmanager
async def lifespan(app: FastAPI):
    print("[startup] Initializing embedding providers...")
    # Initialize OpenRouter API if configured
    get_openai_client()
    
    # Warm up local model only if OpenRouter is not set
    if not _OPENROUTER_MODEL:
        print("[startup] Pre-loading local embedding model...")
        get_local_model()
        
    print("[startup] Ready.")
    yield


# ---------------------------------------------------------------------------
# App
# ---------------------------------------------------------------------------
app = FastAPI(
    title="AI Plagiarism Checker API",
    description="Semantic plagiarism detection using Tavily web search + Sentence Transformers",
    version="1.0.0",
    lifespan=lifespan,
)

# Allow the Next.js frontend (any localhost port during dev)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------
@app.get("/api/health", response_model=HealthResponse, tags=["Health"])
async def health():
    """Health check — confirms API is running and model is loaded."""
    from app.embedder import _model, _openai_client

    if _OPENROUTER_MODEL:
        is_ready = _openai_client is not None
    else:
        is_ready = _model is not None

    return HealthResponse(status="ok", model_loaded=is_ready)


@app.post("/api/check", tags=["Plagiarism"])
async def check_plagiarism(request: CheckRequest):
    """
    Run the full plagiarism detection pipeline.
    Returns a structured plagiarism report.
    """
    try:
        report = await run_detection(request)
        return format_report_summary(report)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")

from app.routes.documents import router as documents_router
app.include_router(documents_router, prefix="/api/documents", tags=["Documents"])

