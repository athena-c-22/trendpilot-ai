"""
Fact-Check Agent: validates claims, resolves conflicts, prioritizes reliable sources.
"""

from __future__ import annotations

import json
import re
from typing import Any

from backend.config import get_openai_client

FACTCHECK_SYSTEM = """You are a fact-checking specialist for market research.
Your task is to validate collected data, identify conflicting claims, and prioritize reliable sources.
Output structured JSON only."""

FACTCHECK_USER_TEMPLATE = """Topic: {topic}

Search agent output:
{search_output}

Data agent output:
{data_output}

Produce a single JSON object with:
- validated_competitors: array of {{ "name": string, "description": string, "confidence": "high"|"medium"|"low" }}
- validated_market_size: string
- validated_trends: array of strings
- conflicts: array of {{ "claim": string, "resolution": string }} (if any)
- source_quality: array of {{ "source": string, "quality": "high"|"medium"|"low" }}
- insights: array of strings (verified key takeaways)
"""


def run_factcheck_agent(
    topic: str,
    search_output: dict[str, Any],
    data_output: dict[str, Any],
) -> dict[str, Any]:
    """
    Run the Fact-Check Agent on combined search and data agent outputs.
    """
    client = get_openai_client()
    model = __import__("os").getenv("OPENAI_MODEL", "gpt-4o-mini")
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": FACTCHECK_SYSTEM},
            {"role": "user", "content": FACTCHECK_USER_TEMPLATE.format(
                topic=topic,
                search_output=json.dumps(search_output, indent=2),
                data_output=json.dumps(data_output, indent=2),
            )},
        ],
        temperature=0.1,
    )
    content = (response.choices[0].message.content or "").strip()
    if content.startswith("```"):
        content = re.sub(r"^```(?:json)?\s*", "", content)
        content = re.sub(r"\s*```$", "", content)
    try:
        return json.loads(content)
    except json.JSONDecodeError:
        return {
            "validated_competitors": search_output.get("competitors", []),
            "validated_market_size": search_output.get("market_size", ""),
            "validated_trends": search_output.get("industry_trends", []),
            "conflicts": [],
            "source_quality": [],
            "insights": search_output.get("insights", []),
        }
