"""
TrendPilot AI — FastAPI backend.
Run from repo root: uvicorn backend.main:app --reload
Or: python -m backend.main (uses PORT from env for deployment)
"""

import logging
import os
import sys
import time
from pathlib import Path

logger = logging.getLogger(__name__)

# Ensure repo root is on path
ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

# Load .env before any config import so OPENAI_API_KEY is available
try:
    from dotenv import load_dotenv
    load_dotenv(ROOT / ".env", override=True)
    load_dotenv(Path.cwd() / ".env", override=True)
except ImportError:
    pass

from fastapi import FastAPI, HTTPException, Request, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from backend.config import (
    RAG_TOP_K,
    OPENAI_API_KEY,
    TRENDPILOT_API_KEY,
    RATE_LIMIT_PER_MINUTE,
    PORT,
)

# In-memory rate limit: ip -> list of request timestamps (pruned to last minute)
_rate_limit_store: dict[str, list[float]] = {}
_RATE_WINDOW = 60.0  # seconds

FRONTEND_DIR = ROOT / "frontend"

app = FastAPI(
    title="TrendPilot AI",
    description="Multi-agent market intelligence — GTM strategy from a topic",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class TopicInput(BaseModel):
    topic: str


class ReportResponse(BaseModel):
    topic: str
    report: dict
    intermediate: dict | None = None


def _get_client_ip(request: Request) -> str:
    return request.client.host if request.client else "unknown"


def _check_auth(request: Request) -> None:
    """If TRENDPILOT_API_KEY is set, require X-API-Key or Authorization header to match."""
    if not TRENDPILOT_API_KEY:
        return
    key = request.headers.get("X-API-Key") or (
        request.headers.get("Authorization") or ""
    ).replace("Bearer ", "").strip()
    if key != TRENDPILOT_API_KEY:
        raise HTTPException(status_code=401, detail="Invalid or missing API key")


def _check_rate_limit(request: Request) -> None:
    """Enforce per-IP rate limit for /research."""
    if RATE_LIMIT_PER_MINUTE <= 0:
        return
    ip = _get_client_ip(request)
    now = time.monotonic()
    if ip not in _rate_limit_store:
        _rate_limit_store[ip] = []
    times = _rate_limit_store[ip]
    # Drop timestamps outside the window
    times[:] = [t for t in times if now - t < _RATE_WINDOW]
    if len(times) >= RATE_LIMIT_PER_MINUTE:
        raise HTTPException(
            status_code=429,
            detail=f"Rate limit exceeded. Try again in a minute.",
        )
    times.append(now)


@app.post("/research", response_model=ReportResponse)
def run_research(request: Request, input: TopicInput):
    """Run the full agent pipeline and return the GTM report."""
    _check_auth(request)
    _check_rate_limit(request)
    topic = (input.topic or "").strip()
    if not topic:
        raise HTTPException(status_code=400, detail="topic is required")
    api_key = OPENAI_API_KEY or os.getenv("OPENAI_API_KEY", "")
    if not api_key:
        # Retry loading .env in case server was started from another cwd
        try:
            from dotenv import load_dotenv
            load_dotenv(ROOT / ".env", override=True)
            load_dotenv(Path.cwd() / ".env", override=True)
            api_key = os.getenv("OPENAI_API_KEY", "")
        except ImportError:
            pass
    if not api_key:
        raise HTTPException(
            status_code=503,
            detail="OPENAI_API_KEY not set. Set it in the environment to run the pipeline.",
        )
    try:
        from agents.coordinator_agent import run_pipeline
        result = run_pipeline(topic, rag_top_k=RAG_TOP_K)
        return ReportResponse(
            topic=result["topic"],
            report=result["report"],
            intermediate=result.get("intermediate"),
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Pipeline failed")
        try:
            from openai import RateLimitError, APIConnectionError
            if isinstance(e, (RateLimitError,)):
                raise HTTPException(
                    status_code=503,
                    detail="OpenAI API quota exceeded. Check your plan and billing at https://platform.openai.com/account/billing",
                ) from e
        except ImportError:
            pass
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
def health():
    return {"status": "ok"}


# Serve frontend: inject API key into index.html when set (for deployment), then static files
if FRONTEND_DIR.is_dir():
    _index_path = FRONTEND_DIR / "index.html"
    if _index_path.exists():
        _index_template = _index_path.read_text(encoding="utf-8")

        @app.get("/")
        def serve_index():
            from fastapi.responses import HTMLResponse
            html = _index_template
            if TRENDPILOT_API_KEY and 'name="api-key"' in html:
                # Inject key so the frontend can call /research (key is same as server check)
                safe_key = TRENDPILOT_API_KEY.replace("&", "&amp;").replace('"', "&quot;").replace("<", "&lt;")
                html = html.replace(
                    '<meta name="api-key" content="" />',
                    f'<meta name="api-key" content="{safe_key}" />',
                    1,
                )
            return HTMLResponse(html)

    app.mount("/", StaticFiles(directory=str(FRONTEND_DIR), html=True), name="frontend")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "backend.main:app",
        host="0.0.0.0",
        port=PORT,
        reload=(os.getenv("RELOAD", "").lower() in ("1", "true", "yes")),
    )
