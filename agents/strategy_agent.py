"""
Strategy Agent: synthesizes research and produces the final GTM strategy report.
"""

from __future__ import annotations

import json
import re
from typing import Any

from backend.config import get_openai_client

STRATEGY_SYSTEM = """You are a Go-To-Market strategy expert.
Synthesize the provided research into a clear, actionable GTM strategy report.
Output structured JSON suitable for a final report."""

STRATEGY_USER_TEMPLATE = """Topic: {topic}

Validated research (fact-check output):
{factcheck_output}

Produce a single JSON object with these sections for the final report:
- market_overview: string (2-4 sentences)
- competitor_landscape: array of {{ "name": string, "positioning": string, "strength": string }}
- target_audience: array of {{ "segment": string, "description": string }}
- pricing_strategy: string
- marketing_channels: array of {{ "channel": string, "tactics": string }}
- launch_plan: array of {{ "phase": string, "actions": string }}
- key_insights: array of strings
- risks_and_mitigations: array of {{ "risk": string, "mitigation": string }}
"""


def run_strategy_agent(topic: str, factcheck_output: dict[str, Any]) -> dict[str, Any]:
    """
    Run the Strategy Agent to generate the final GTM report.
    """
    client = get_openai_client()
    model = __import__("os").getenv("OPENAI_MODEL", "gpt-4o-mini")
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": STRATEGY_SYSTEM},
            {"role": "user", "content": STRATEGY_USER_TEMPLATE.format(
                topic=topic,
                factcheck_output=json.dumps(factcheck_output, indent=2),
            )},
        ],
        temperature=0.3,
    )
    content = (response.choices[0].message.content or "").strip()
    if content.startswith("```"):
        content = re.sub(r"^```(?:json)?\s*", "", content)
        content = re.sub(r"\s*```$", "", content)
    try:
        return json.loads(content)
    except json.JSONDecodeError:
        return {
            "market_overview": "",
            "competitor_landscape": [],
            "target_audience": [],
            "pricing_strategy": "",
            "marketing_channels": [],
            "launch_plan": [],
            "key_insights": [],
            "risks_and_mitigations": [],
        }
