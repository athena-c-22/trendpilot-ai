# CLAUDE.md

## Project Overview

TrendPilot AI is a **multi-agent market intelligence system** that autonomously conducts market research and generates Go-To-Market (GTM) strategies from a user-defined topic.

The system uses multiple AI agents working collaboratively to:

1. Collect market and competitor information from the web
2. Retrieve relevant industry knowledge using RAG
3. Verify and correct information
4. Generate a structured market analysis and GTM strategy report

The goal of this project is to demonstrate **agentic workflows**, **AI-assisted research**, and **automated strategic analysis**.

---

# Core Principles

When contributing code or generating features for this repository, follow these principles:

### 1. Agent-first architecture

The system should rely on **multiple specialized AI agents**, not a single monolithic prompt.

Agents should have clear responsibilities such as:

* search
* verification
* synthesis
* strategy generation

### 2. Modular design

Each agent should be implemented as an independent module.

Example structure:

```
agents/
    coordinator_agent.py
    search_agent.py
    data_agent.py
    factcheck_agent.py
    strategy_agent.py
```

Agents should communicate through structured outputs.

### 3. Deterministic pipelines where possible

Agent workflows should be predictable and reproducible. Prefer structured data formats (JSON) when passing information between agents.

### 4. Minimal external dependencies

The project should remain lightweight and easy to deploy.

---

# System Architecture

High-level workflow:

```
User Query
   │
Coordinator Agent
   │
 ┌─┴─────────────┐
Search Agent   Data Agent
   │               │
   └─────┬─────────┘
         ▼
   Fact Check Agent
         │
         ▼
   RAG Retrieval Layer
         │
         ▼
   Strategy Agent
         │
         ▼
    Final Report
```

### Coordinator Agent

Responsibilities:

* orchestrates the workflow
* assigns tasks to agents
* aggregates outputs

### Search Agent

Responsibilities:

* perform web searches
* gather relevant articles and sources
* return structured summaries

### Data Agent

Responsibilities:

* retrieve industry reports and datasets
* extract relevant market insights

### Fact-Check Agent

Responsibilities:

* validate claims
* identify conflicting data
* prioritize reliable sources

### Strategy Agent

Responsibilities:

* synthesize collected data
* generate Go-To-Market strategy
* produce final structured report

---

# Repository Structure

Expected project layout:

```
trendpilot-ai-agent/

README.md
CLAUDE.md
ARCHITECTURE.md
DEMO.md
PROMPTS.md

backend/
    main.py
    config.py

agents/
    coordinator_agent.py
    search_agent.py
    data_agent.py
    factcheck_agent.py
    strategy_agent.py

rag/
    ingest.py
    retrieval.py

tools/
    search_tool.py
    scraper.py

frontend/
    index.html
    styles.css
    app.js

data/
    reports/
    datasets/
```

---

# Coding Guidelines

### Python version

Use **Python 3.10+**

### Style

Follow:

* PEP8
* type hints
* clear function documentation

Example:

```python
def generate_market_report(topic: str) -> dict:
    """
    Generate a GTM strategy report for a given market topic.
    """
```

### Agent Output Format

Agents should return **structured JSON**.

Example:

```
{
  "market_size": "...",
  "key_competitors": [],
  "target_audience": [],
  "insights": []
}
```

---

# Prompt Engineering Guidelines

Prompts should:

* define clear agent roles
* request structured outputs
* avoid vague instructions

Example pattern:

```
You are a market research analyst.

Your task is to analyze the following market topic.

Focus on:
- competitors
- user demographics
- pricing models

Return results in structured JSON.
```

---

# Retrieval-Augmented Generation (RAG)

The system may include a knowledge base containing:

* industry reports
* startup analysis
* marketing frameworks

Documents should be:

1. embedded
2. stored in a vector database
3. retrieved during agent reasoning

---

# Deployment Goals

The application should be deployable as a simple web service.

Preferred setup:

Backend

* FastAPI

Frontend

* simple web interface (optional)

Deployment

* Vercel
* Railway
* Render

---

# Future Improvements

Potential extensions include:

* social media trend analysis
* automated competitor dashboards
* visualization of market insights
* integration with real-time APIs

---

# Contribution Guidelines

When adding new features:

1. Maintain the **multi-agent architecture**
2. Keep agents **single-responsibility**
3. Ensure outputs are **structured**
4. Document any new agent roles

---

# Summary

TrendPilot AI demonstrates how **collaborating AI agents** can automate complex market research tasks.

The repository should prioritize:

* clear architecture
* modular agent design
* reproducible workflows
* high-quality prompt engineering
