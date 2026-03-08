"""
Simple scraper to fetch and extract text from URLs.
Used by agents to get page content when needed.
"""

from __future__ import annotations

import re
from typing import Optional

import httpx


def fetch_url(url: str, timeout: float = 10.0) -> Optional[str]:
    """
    Fetch a URL and return plain text content.
    Strips HTML tags and normalizes whitespace.
    """
    try:
        headers = {
            "User-Agent": "TrendPilot-AI/1.0 (Market Research Bot; +https://github.com/trendpilot-ai)",
        }
        with httpx.Client(timeout=timeout, follow_redirects=True) as client:
            response = client.get(url, headers=headers)
            response.raise_for_status()
            html = response.text
    except Exception:
        return None

    return _extract_text(html)


def _extract_text(html: str, max_chars: int = 50000) -> str:
    """Remove HTML tags and script/style, normalize whitespace."""
    # Remove script and style
    html = re.sub(r"<script[^>]*>[\s\S]*?</script>", "", html, flags=re.IGNORECASE)
    html = re.sub(r"<style[^>]*>[\s\S]*?</style>", "", html, flags=re.IGNORECASE)
    # Strip tags
    text = re.sub(r"<[^>]+>", " ", html)
    # Decode common entities
    text = text.replace("&nbsp;", " ").replace("&amp;", "&").replace("&lt;", "<").replace("&gt;", ">")
    # Normalize whitespace
    text = re.sub(r"\s+", " ", text).strip()
    return text[:max_chars] if len(text) > max_chars else text
