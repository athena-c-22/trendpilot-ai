# CLAUDE.md

## Project Overview

TrendPilot AI is a **multi-agent market intelligence system** that
autonomously conducts market research and generates Go-To-Market (GTM)
strategies from a user-defined topic.

The system uses multiple AI agents working collaboratively to:

1.  Collect market and competitor information from the web
2.  Retrieve relevant industry knowledge using RAG
3.  Analyze **user-provided industry reports or datasets**
4.  Verify and correct information
5.  Generate a structured market analysis and GTM strategy report

Users may optionally **upload industry data, market reports, or
datasets**. These documents are processed using **Retrieval-Augmented
Generation (RAG)** so the agents can incorporate the uploaded knowledge
into their analysis alongside information retrieved from AI-powered web
search.

The goal of this project is to demonstrate **agentic workflows**,
**AI-assisted research**, **document-aware analysis**, and **automated
strategic insights**.

------------------------------------------------------------------------

# Core Principles

When contributing code or generating features for this repository,
follow these principles:

### 1. Agent-first architecture

The system should rely on **multiple specialized AI agents**, not a
single monolithic prompt.

Agents should have clear responsibilities such as:

-   search
-   document analysis
-   verification
-   synthesis
-   strategy generation

### 2. Modular design

Each agent should be implemented as an independent module.

Example structure:

    agents/
        coordinator_agent.py
        search_agent.py
        data_agent.py
        factcheck_agent.py
        strategy_agent.py

Agents should communicate through **structured outputs**.

### 3. Deterministic pipelines where possible

Agent workflows should be predictable and reproducible. Prefer
**structured data formats (JSON)** when passing information between
agents.

### 4. Minimal external dependencies

The project should remain lightweight and easy to deploy.

------------------------------------------------------------------------

# System Architecture

High-level workflow:

    User Query + Optional Uploaded Reports
       │
    Coordinator Agent
       │
     ┌─┴─────────────┐
    Search Agent   Data Agent
    (web search)   (document analysis)
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

The system combines **external AI search** with **knowledge extracted
from user-provided documents** to produce more reliable market insights.

------------------------------------------------------------------------

# Agent Responsibilities

### Coordinator Agent

Responsibilities:

-   orchestrates the workflow
-   assigns tasks to agents
-   aggregates outputs
-   manages user-provided data sources

------------------------------------------------------------------------

### Search Agent

Responsibilities:

-   perform AI-powered web searches
-   gather relevant articles and sources
-   identify competitors and market signals
-   return structured summaries

------------------------------------------------------------------------

### Data Agent

Responsibilities:

-   process **user-uploaded reports or datasets**
-   extract relevant market insights from documents
-   prepare structured knowledge for RAG retrieval
-   summarize key findings from uploaded data

Supported document types may include:

-   PDFs
-   text reports
-   spreadsheets
-   structured datasets

------------------------------------------------------------------------

### Fact-Check Agent

Responsibilities:

-   validate claims from web sources and documents
-   identify conflicting data
-   prioritize reliable sources
-   flag uncertain or unverifiable information

------------------------------------------------------------------------

### Strategy Agent

Responsibilities:

-   synthesize collected information
-   combine **web insights and uploaded industry data**
-   generate Go-To-Market strategy
-   produce final structured report

------------------------------------------------------------------------

# Repository Structure

Expected project layout:

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

Uploaded documents may be stored in:

    data/reports/
    data/datasets/

before being processed into the RAG knowledge base.

------------------------------------------------------------------------

# Coding Guidelines

### Python version

Use **Python 3.10+**

### Style

Follow:

-   PEP8
-   type hints
-   clear function documentation

Example:

``` python
def generate_market_report(topic: str) -> dict:
    """
    Generate a GTM strategy report for a given market topic.
    """
```

------------------------------------------------------------------------

# Agent Output Format

Agents should return **structured JSON**.

Example:

    {
      "market_size": "...",
      "key_competitors": [],
      "target_audience": [],
      "insights": [],
      "sources": []
    }

------------------------------------------------------------------------

# Prompt Engineering Guidelines

Prompts should:

-   define clear agent roles
-   request structured outputs
-   avoid vague instructions

Example pattern:

    You are a market research analyst.

    Your task is to analyze the following market topic and supporting documents.

    Focus on:
    - competitors
    - user demographics
    - pricing models
    - insights from uploaded industry reports

    Return results in structured JSON.

------------------------------------------------------------------------

# Retrieval-Augmented Generation (RAG)

The system includes a knowledge base built from:

-   **user-uploaded industry reports**
-   startup analysis documents
-   marketing frameworks
-   market datasets

Document pipeline:

1.  User uploads reports or datasets
2.  Documents are parsed and chunked
3.  Text is embedded
4.  Embeddings are stored in a vector database
5.  Agents retrieve relevant chunks during reasoning

This allows the system to **combine private knowledge with real-time web
search**.

------------------------------------------------------------------------

# Deployment Goals

The application should be deployable as a simple web service.

Preferred setup:

Backend

-   FastAPI

Frontend

-   simple web interface (optional)

Deployment

-   Vercel
-   Railway
-   Render

------------------------------------------------------------------------

# Future Improvements

Potential extensions include:

-   social media trend analysis
-   automated competitor dashboards
-   visualization of market insights
-   integration with real-time APIs
-   support for larger enterprise knowledge bases

------------------------------------------------------------------------

# Contribution Guidelines

When adding new features:

1.  Maintain the **multi-agent architecture**
2.  Keep agents **single-responsibility**
3.  Ensure outputs are **structured**
4.  Document any new agent roles
5.  Ensure compatibility with the **RAG document pipeline**

------------------------------------------------------------------------

# Summary

TrendPilot AI demonstrates how **collaborating AI agents** can automate
complex market research tasks.

The repository prioritizes:

-   clear architecture
-   modular agent design
-   integration of **AI search + user-provided data**
-   reproducible workflows
-   high-quality prompt engineering
