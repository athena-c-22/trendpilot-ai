# ARCHITECTURE.md

## System Overview

TrendPilot AI is a **multi-agent market intelligence platform** that autonomously researches markets and generates Go-To-Market (GTM) strategies.

The system uses multiple AI agents, each responsible for a specific part of the research and reasoning process.

The design follows an **agentic pipeline architecture**, where agents collaborate to gather, verify, and synthesize information.

---

# High-Level Architecture

Workflow:

```
User Input
   │
   ▼
Coordinator Agent
   │
 ┌─┴───────────────┐
 ▼                 ▼
Search Agent      Data Agent
(Web research)    (Industry knowledge)
   │                 │
   └───────┬─────────┘
           ▼
     Fact Check Agent
           │
           ▼
      RAG Retrieval
           │
           ▼
      Strategy Agent
           │
           ▼
      Final Report
```

---

# Agent Responsibilities

## Coordinator Agent

Purpose:

* orchestrates the workflow
* manages agent communication
* merges intermediate outputs

Responsibilities:

* receive user topic
* trigger research agents
* aggregate results
* pass results to strategy agent

---

## Search Agent

Purpose:

Collect up-to-date market information from the web.

Tasks:

* search for competitors
* gather market statistics
* identify key trends
* extract structured insights

Example output:

```
{
  "competitors": [],
  "market_trends": [],
  "statistics": []
}
```

---

## Data Agent

Purpose:

Retrieve relevant knowledge from stored reports and datasets.

Sources may include:

* industry research reports
* startup analysis
* marketing frameworks

The data agent interacts with the **RAG system**.

---

## Fact Check Agent

Purpose:

Improve reliability of collected information.

Tasks:

* detect conflicting claims
* remove outdated data
* prioritize high-quality sources

Output includes confidence indicators.

---

## Strategy Agent

Purpose:

Generate the final Go-To-Market strategy.

The agent synthesizes:

* web research
* RAG knowledge
* validated insights

Output sections:

* Market Overview
* Competitor Landscape
* Target Audience
* Pricing Strategy
* Marketing Channels
* Launch Plan

---

# Retrieval-Augmented Generation (RAG)

The RAG system provides domain knowledge during reasoning.

Pipeline:

```
Document ingestion
     │
Embedding generation
     │
Vector database storage
     │
Query retrieval
     │
Context injection into prompts
```

This allows agents to combine:

* **live web dat**
