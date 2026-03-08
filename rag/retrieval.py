"""
RAG retrieval: query the vector store and return relevant context.
"""

from __future__ import annotations

from typing import Any

_collection = None
_embed_fn = None


def _get_embed_fn():
    global _embed_fn
    if _embed_fn is None:
        from backend.config import get_openai_client, OPENAI_EMBEDDING_MODEL
        client = get_openai_client()
        model = OPENAI_EMBEDDING_MODEL

        def embed(texts: list[str]) -> list[list[float]]:
            if not texts:
                return []
            r = client.embeddings.create(input=texts, model=model)
            return [d.embedding for d in r.data]

        _embed_fn = embed
    return _embed_fn


def _get_collection():
    global _collection
    if _collection is None:
        import chromadb
        from backend.config import RAG_PERSIST_DIR, RAG_COLLECTION_NAME
        client = chromadb.PersistentClient(path=str(RAG_PERSIST_DIR))
        try:
            _collection = client.get_collection(name=RAG_COLLECTION_NAME)
        except Exception:
            _collection = client.create_collection(
                name=RAG_COLLECTION_NAME,
                metadata={"description": "TrendPilot knowledge base"},
            )
    return _collection


def retrieve(query: str, top_k: int = 5) -> list[dict[str, Any]]:
    """
    Retrieve the most relevant documents for a query.
    Returns list of dicts with keys: content, metadata, distance.
    """
    try:
        coll = _get_collection()
        embed_fn = _get_embed_fn()
        if coll.count() == 0:
            return []
        q_embedding = embed_fn([query])[0]
        results = coll.query(
            query_embeddings=[q_embedding],
            n_results=min(top_k, coll.count()),
            include=["documents", "metadatas", "distances"],
        )
        out = []
        docs = results.get("documents", [[]])[0]
        metas = results.get("metadatas", [[]])[0]
        dists = results.get("distances", [[]])[0]
        for i, doc in enumerate(docs):
            out.append({
                "content": doc or "",
                "metadata": metas[i] if i < len(metas or []) else {},
                "distance": dists[i] if i < len(dists or []) else None,
            })
        return out
    except Exception:
        return []


def get_context_for_prompt(query: str, top_k: int = 5, max_chars: int = 8000) -> str:
    """
    Retrieve documents and format as a single context string for agent prompts.
    """
    items = retrieve(query, top_k=top_k)
    parts = []
    total = 0
    for item in items:
        content = (item.get("content") or "").strip()
        if not content or total + len(content) > max_chars:
            continue
        parts.append(content)
        total += len(content)
    return "\n\n---\n\n".join(parts) if parts else ""
