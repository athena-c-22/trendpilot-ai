"""
Application configuration for TrendPilot AI.
Loads settings from environment variables and from .env in the repo root.
"""

import os
from pathlib import Path

# Load .env so OPENAI_API_KEY etc. are available (repo root, then cwd)
_ROOT_DIR = Path(__file__).resolve().parent.parent
try:
    from dotenv import load_dotenv
    load_dotenv(_ROOT_DIR / ".env", override=True)
    if not os.getenv("OPENAI_API_KEY"):
        load_dotenv(Path.cwd() / ".env", override=True)
except ImportError:
    pass

def _env_bool(name: str, default: bool = False) -> bool:
    raw = os.getenv(name, "").strip().lower()
    if not raw:
        return default
    return raw in ("1", "true", "yes", "on")


# Paths
ROOT_DIR = _ROOT_DIR
DATA_DIR = ROOT_DIR / "data"
REPORTS_DIR = DATA_DIR / "reports"
DATASETS_DIR = DATA_DIR / "datasets"
RAG_PERSIST_DIR = DATA_DIR / "chroma_db"

# API keys (set in environment)
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL", "").rstrip("/")  # e.g. https://openrouter.ai/api/v1
SEARCH_API_KEY = os.getenv("SEARCH_API_KEY", "")  # e.g. Tavily, SerpAPI

# LLM settings
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
OPENAI_EMBEDDING_MODEL = os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small")


def get_openai_client():
    """Return an OpenAI client (uses OPENAI_BASE_URL when set, e.g. for OpenRouter)."""
    from openai import OpenAI
    kwargs = {"api_key": OPENAI_API_KEY}
    if OPENAI_BASE_URL:
        kwargs["base_url"] = OPENAI_BASE_URL
    return OpenAI(**kwargs)

# RAG
RAG_COLLECTION_NAME = "trendpilot_knowledge"
RAG_TOP_K = int(os.getenv("RAG_TOP_K", "5"))

# Optional: use mock tools when no API keys (for local demo)
USE_MOCK_SEARCH = _env_bool("USE_MOCK_SEARCH", default=not bool(SEARCH_API_KEY))

# Public deployment: optional API key to protect /research (set in host env)
TRENDPILOT_API_KEY = os.getenv("TRENDPILOT_API_KEY", "").strip()
# Rate limit: max requests per IP per minute for /research (0 = no limit)
RATE_LIMIT_PER_MINUTE = int(os.getenv("RATE_LIMIT_PER_MINUTE", "10"))
# Port for server (Railway, Render, etc. set PORT)
PORT = int(os.getenv("PORT", "8080"))
