"""
Document ingestion for RAG: load docs, embed, store in vector DB.
"""

from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Any, Optional

# Lazy imports for chromadb and openai to keep startup light
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
        RAG_PERSIST_DIR.mkdir(parents=True, exist_ok=True)
        client = chromadb.PersistentClient(path=str(RAG_PERSIST_DIR))
        _collection = client.get_or_create_collection(
            name=RAG_COLLECTION_NAME,
            metadata={"description": "TrendPilot knowledge base"},
        )
    return _collection


def ingest_document(
    text: str,
    doc_id: Optional[str] = None,
    metadata: Optional[dict[str, Any]] = None,
) -> str:
    """
    Ingest a single document: embed and add to the vector store.
    Returns the document id used.
    """
    if not text.strip():
        raise ValueError("Document text cannot be empty")
    coll = _get_collection()
    embed_fn = _get_embed_fn()
    id_ = doc_id or hashlib.sha256(text.encode()).hexdigest()[:32]
    meta = dict(metadata or {})
    embedding = embed_fn([text])[0]
    coll.upsert(ids=[id_], embeddings=[embedding], documents=[text], metadatas=[meta])
    return id_


def ingest_file(file_path: Path, doc_id: Optional[str] = None) -> str:
    """Load a text file and ingest it."""
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(str(path))
    text = path.read_text(encoding="utf-8", errors="replace")
    return ingest_document(
        text,
        doc_id=doc_id or path.name,
        metadata={"source": str(path)},
    )


def ingest_directory(dir_path: Path, glob: str = "**/*.txt") -> list[str]:
    """Ingest all matching files in a directory. Returns list of doc ids."""
    path = Path(dir_path)
    if not path.is_dir():
        return []
    ids = []
    for f in path.glob(glob):
        if f.is_file():
            try:
                ids.append(ingest_file(f))
            except Exception:
                pass
    return ids
