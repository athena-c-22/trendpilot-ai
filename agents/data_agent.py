"""
Data Agent: retrieves industry knowledge from RAG and extracts relevant insights.
"""

from __future__ import annotations

import json
import re
from typing import Any

from backend.config import get_openai_client
from rag.retrieval import get_context_for_prompt

DATA_AGENT_SYSTEM = """You are an industry research specialist.
Using the provided knowledge base context (which may include user-uploaded industry reports and datasets), extract insights relevant to the topic.
If context is empty, return structured empty/minimal JSON from general knowledge.
Always return valid JSON only."""

DATA_AGENT_USER_TEMPLATE = """Topic: {topic}

Knowledge base context (web-sourced and/or user-uploaded reports/datasets):
{context}

Return exactly one JSON object with these keys:
- framework_insights: array of strings (from frameworks/reports)
- industry_benchmarks: array of strings
- recommendations: array of strings
- sources_used: array of strings (brief)
"""


def run_data_agent(topic: str, top_k: int = 5) -> dict[str, Any]:
    """
    Run the Data Agent: RAG retrieval + LLM to produce structured insights.
    """
    context = get_context_for_prompt(topic, top_k=top_k)
    if not context.strip():
        context = "(No documents in knowledge base. Provide brief generic insights if relevant.)"

    client = get_openai_client()
    model = __import__("os").getenv("OPENAI_MODEL", "gpt-4o-mini")
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": DATA_AGENT_SYSTEM},
            {"role": "user", "content": DATA_AGENT_USER_TEMPLATE.format(
                topic=topic,
                context=context,
            )},
        ],
        temperature=0.2,
    )
    content = (response.choices[0].message.content or "").strip()
    if content.startswith("```"):
        content = re.sub(r"^```(?:json)?\s*", "", content)
        content = re.sub(r"\s*```$", "", content)
    try:
        return json.loads(content)
    except json.JSONDecodeError:
        return {
            "framework_insights": [],
            "industry_benchmarks": [],
            "recommendations": [],
            "sources_used": [],
        }
