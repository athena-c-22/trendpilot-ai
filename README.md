# TrendPilot AI

Multi-agent market intelligence system that autonomously researches a topic and generates a Go-To-Market (GTM) strategy.

## Overview

- **Coordinator** orchestrates the pipeline.
- **Search Agent** gathers market/competitor info from the web.
- **Data Agent** pulls insights from the RAG knowledge base.
- **Fact-Check Agent** validates and merges findings.
- **Strategy Agent** produces the final GTM report.

## Setup

**Python 3.10+**

```bash
cd trendpilot-ai
python -m venv .venv
.venv\Scripts\activate   # Windows
# source .venv/bin/activate  # macOS/Linux
pip install -r requirements.txt
```

## Environment

Create a `.env` (or set in shell):

- `OPENAI_API_KEY` — **required** (OpenAI key or OpenRouter key if using OpenRouter).
- `OPENAI_BASE_URL` — optional; set to use an OpenAI-compatible API (e.g. OpenRouter). Leave unset for OpenAI.
- `OPENAI_MODEL` — optional; default `gpt-4o-mini`. With OpenRouter use e.g. `anthropic/claude-3.5-haiku`.
- `OPENAI_EMBEDDING_MODEL` — optional; default `text-embedding-3-small` (OpenRouter supports embeddings too).
- `SEARCH_API_KEY` — optional; for real web search (Tavily or SerpAPI). If unset, mock search is used.
- `SEARCH_PROVIDER` — optional; `tavily` or `serpapi`.
- `RAG_TOP_K` — optional; number of RAG docs per query (default `5`).
- `TRENDPILOT_API_KEY` — optional; when set, `/research` requires `X-API-Key` header (for public deployment).
- `RATE_LIMIT_PER_MINUTE` — optional; max `/research` requests per IP per minute (default `10`). Set `0` to disable.
- `PORT` — optional; server port (default `8080`). Set by Render, etc.

### Using OpenRouter

Use [OpenRouter](https://openrouter.ai/) to call Claude, Gemini, Llama, etc. with one API:

```env
OPENAI_API_KEY=sk-or-v1-...your-openrouter-key...
OPENAI_BASE_URL=https://openrouter.ai/api/v1
OPENAI_MODEL=anthropic/claude-3.5-haiku
```

Get a key at https://openrouter.ai/keys. Model IDs: https://openrouter.ai/docs/models.

## Run the app

From the **repo root**:

```bash
uvicorn backend.main:app --reload
```

On Windows, if you see a socket/permission error on port 8000, use port 8080 instead:

```bash
uvicorn backend.main:app --reload --port 8080
```
Then open http://127.0.0.1:8080

### Run the frontend

The same command serves both the backend and the frontend. After starting the server above, open in your browser:

- **Frontend (Web UI):** http://127.0.0.1:8000 — enter a topic and click **Run research** to get a GTM report. (Use 8080 if you started with `--port 8080`.)

Other URLs:

- **API docs:** http://127.0.0.1:8000/docs  
- **Health:** http://127.0.0.1:8000/health  

### Run research via API

```bash
curl -X POST http://127.0.0.1:8000/research -H "Content-Type: application/json" -d "{\"topic\": \"AI productivity app for university students\"}"
```

## RAG (optional)

To add documents to the knowledge base:

1. Put `.txt` files under `data/reports/` or `data/datasets/`.
2. Use the RAG ingest helper (e.g. from a script at repo root):

```python
from pathlib import Path
from rag.ingest import ingest_directory

ingest_directory(Path("data/reports"))
```

If the vector store is empty, the Data Agent still runs using an empty context.

## Public deployment

The app is ready to deploy to **Render**, **Fly.io**, or any host that runs Python and sets `PORT`.

### Deploy backend to Render

1. Push your repo to GitHub and go to [Render](https://render.com). **New** → **Web Service**, connect the repo.
2. **Settings:**
   - **Runtime:** Python 3
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `python -m backend.main` or `uvicorn backend.main:app --host 0.0.0.0 --port $PORT`
3. **Environment:** Add variables (e.g. `OPENAI_API_KEY`, `OPENAI_BASE_URL`, `OPENAI_MODEL`). Render sets `PORT` automatically.
4. Deploy; your API (and the same-origin UI) will be at https://trendpilot-ai.onrender.com/

**Notes:**
- **Protection:** Rate limit is 10 requests per IP per minute (`RATE_LIMIT_PER_MINUTE`); optional `TRENDPILOT_API_KEY` for API key auth.
- **RAG:** ChromaDB uses `data/chroma_db`. Render’s disk is persistent; serverless hosts will not persist the vector DB.

### Deploy frontend to GitHub Pages

GitHub Pages only serves **static files**; it cannot run the FastAPI backend. You can host the **UI** on GitHub Pages and call a **backend** deployed elsewhere (e.g. Render).

1. **Deploy the backend first** on Render and note the URL: https://trendpilot-ai.onrender.com/

2. **Copy the frontend into `docs/`** so GitHub Pages can serve it:
   ```bash
   mkdir -p docs
   cp frontend/index.html frontend/styles.css frontend/app.js docs/
   ```

3. **Edit `docs/index.html`**:
   - Add a `<base>` tag so assets load correctly (use your repo name):
     ```html
     <head>
       <base href="/trendpilot-ai/" />
     ```
   - Set your backend URL so the UI calls your API:
     ```html
     <meta name="api-base" content="https://trendpilot-ai.onrender.com" />
     ```

4. **Turn on GitHub Pages:** Repo → **Settings** → **Pages** → Source: **Deploy from a branch** → Branch: **main** → Folder: **/docs** → Save.

5. The site will be at `https://<your-username>.github.io/trendpilot-ai/`. It will use the backend URL you set in `api-base`.

## Project layout

```
backend/     main.py, config.py (serves frontend at /)
frontend/    index.html, styles.css, app.js
agents/      coordinator, search, data, factcheck, strategy
rag/         ingest.py, retrieval.py
tools/       search_tool.py, scraper.py
data/        reports/, datasets/, chroma_db (created at runtime)
```

See `CLAUDE.md`, `ARCHITECTURE.md`, and `PROMPTS.md` for design and prompts.
