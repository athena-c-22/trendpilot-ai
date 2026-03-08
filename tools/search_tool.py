"""
Web search tool for the Search Agent.
Supports real search (Tavily/SerpAPI) or mock results for demos.
"""

from __future__ import annotations

import os
from typing import Any

import httpx

# Optional: set SEARCH_API_KEY and SEARCH_PROVIDER (tavily|serpapi)
SEARCH_API_KEY = os.getenv("SEARCH_API_KEY", "")
SEARCH_PROVIDER = os.getenv("SEARCH_PROVIDER", "tavily").lower()
USE_MOCK = os.getenv("USE_MOCK_SEARCH", "true").strip().lower() in ("1", "true", "yes")


def search_web(query: str, max_results: int = 8) -> list[dict[str, Any]]:
    """
    Perform web search and return structured results.

    Returns list of dicts with keys: title, url, snippet (and optionally content).
    """
    if USE_MOCK or not SEARCH_API_KEY:
        return _mock_search(query, max_results)

    if SEARCH_PROVIDER == "tavily":
        return _tavily_search(query, max_results)
    if SEARCH_PROVIDER == "serpapi":
        return _serpapi_search(query, max_results)

    return _mock_search(query, max_results)


def _mock_search(query: str, max_results: int) -> list[dict[str, Any]]:
    """Return plausible mock results for demos without API keys."""
    return [
        {
            "title": f"Market overview: {query}",
            "url": "https://example.com/market-overview",
            "snippet": f"Growing market segment related to {query}. Key players and trends.",
        },
        {
            "title": f"Competitors in {query}",
            "url": "https://example.com/competitors",
            "snippet": "Leading companies and startups in this space.",
        },
        {
            "title": f"Industry trends: {query}",
            "url": "https://example.com/trends",
            "snippet": "Recent trends and growth projections.",
        },
    ][:max_results]


def _tavily_search(query: str, max_results: int) -> list[dict[str, Any]]:
    """Search using Tavily API."""
    url = "https://api.tavily.com/search"
    payload = {
        "api_key": SEARCH_API_KEY,
        "query": query,
        "max_results": max_results,
        "include_answer": False,
    }
    try:
        with httpx.Client(timeout=15.0) as client:
            r = client.post(url, json=payload)
            r.raise_for_status()
            data = r.json()
        results = []
        for item in data.get("results", [])[:max_results]:
            results.append({
                "title": item.get("title", ""),
                "url": item.get("url", ""),
                "snippet": item.get("content", "")[:500],
            })
        return results
    except Exception:
        return _mock_search(query, max_results)


def _serpapi_search(query: str, max_results: int) -> list[dict[str, Any]]:
    """Search using SerpAPI."""
    url = "https://serpapi.com/search"
    params = {"q": query, "api_key": SEARCH_API_KEY, "num": max_results}
    try:
        with httpx.Client(timeout=15.0) as client:
            r = client.get(url, params=params)
            r.raise_for_status()
            data = r.json()
        results = []
        for item in data.get("organic_results", [])[:max_results]:
            results.append({
                "title": item.get("title", ""),
                "url": item.get("link", ""),
                "snippet": item.get("snippet", ""),
            })
        return results
    except Exception:
        return _mock_search(query, max_results)
