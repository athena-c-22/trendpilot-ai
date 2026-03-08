"""
Coordinator Agent: orchestrates the pipeline and aggregates agent outputs.
"""

from __future__ import annotations

from typing import Any

from agents.search_agent import run_search_agent
from agents.data_agent import run_data_agent
from agents.factcheck_agent import run_factcheck_agent
from agents.strategy_agent import run_strategy_agent


def run_pipeline(topic: str, rag_top_k: int = 5) -> dict[str, Any]:
    """
    Run the full TrendPilot pipeline:
    Coordinator → Search + Data → Fact-Check → RAG context → Strategy → Report.
    """
    # 1. Search and Data in parallel (coordinator assigns tasks)
    search_output = run_search_agent(topic)
    data_output = run_data_agent(topic, top_k=rag_top_k)

    # 2. Fact-Check merges and validates
    factcheck_output = run_factcheck_agent(topic, search_output, data_output)

    # 3. Strategy produces final report
    report = run_strategy_agent(topic, factcheck_output)

    return {
        "topic": topic,
        "report": report,
        "intermediate": {
            "search": search_output,
            "data": data_output,
            "factcheck": factcheck_output,
        },
    }
