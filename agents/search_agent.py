"""
Search Agent: performs web searches and returns structured market summaries.
"""

from __future__ import annotations

import json
import re
from typing import Any

from backend.config import get_openai_client
from tools.search_tool import search_web

SEARCH_AGENT_SYSTEM = """You are a market research analyst.
Your task is to collect relevant information about a given topic from search results.
Focus on: competitors, market size, industry trends, notable companies.
Always return valid JSON only, no markdown or extra text."""

SEARCH_AGENT_USER_TEMPLATE = """Topic: {topic}

Search results (use these to fill the JSON):
{search_results}

Return exactly one JSON object with these keys:
- competitors: array of {{ "name": string, "description": string }}
- market_size: string (brief)
- industry_trends: array of strings
- sources: array of {{ "title": string, "url": string }}
- insights: array of strings (key takeaways)
"""


def run_search_agent(topic: str, max_search_results: int = 8) -> dict[str, Any]:
    """
    Run the Search Agent: search the web and synthesize structured output.
    """
    results = search_web(topic, max_results=max_search_results)
    search_results_text = "\n\n".join(
        f"[{i+1}] {r.get('title', '')}\n{r.get('url', '')}\n{r.get('snippet', '')}"
        for i, r in enumerate(results)
    )
    if not search_results_text.strip():
        search_results_text = "No search results available. Infer plausible structure from the topic."

    client = get_openai_client()
    model = __import__("os").getenv("OPENAI_MODEL", "gpt-4o-mini")
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": SEARCH_AGENT_SYSTEM},
            {"role": "user", "content": SEARCH_AGENT_USER_TEMPLATE.format(
                topic=topic,
                search_results=search_results_text,
            )},
        ],
        temperature=0.2,
    )
    content = (response.choices[0].message.content or "").strip()
    # Strip markdown code block if present
    if content.startswith("```"):
        content = re.sub(r"^```(?:json)?\s*", "", content)
        content = re.sub(r"\s*```$", "", content)
    try:
        return json.loads(content)
    except json.JSONDecodeError:
        return {
            "competitors": [],
            "market_size": "",
            "industry_trends": [],
            "sources": [{"title": r.get("title", ""), "url": r.get("url", "")} for r in results],
            "insights": [content[:500]],
        }
