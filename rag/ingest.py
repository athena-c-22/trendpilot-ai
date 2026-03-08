"""
Document ingestion for RAG: load docs, parse (PDF/CSV/text), chunk, embed, store.
Supports user-uploaded industry reports and datasets per CLAUDE.md.
"""

from __future__ import annotations

import csv
import hashlib
from pathlib import Path
from typing import Any, Optional

# Lazy imports for chromadb and openai to keep startup light
_collection = None
_embed_fn = None

# Chunk size for long documents (embedding and retrieval)
CHUNK_SIZE = 6000
CHUNK_OVERLAP = 200


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


def _chunk_text(text: str, chunk_size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP) -> list[str]:
    """Split long text into overlapping chunks for embedding."""
    text = text.strip()
    if len(text) <= chunk_size:
        return [text] if text else []
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end]
        # Try to break at paragraph or sentence
        if end < len(text):
            for sep in ("\n\n", "\n", ". "):
                last = chunk.rfind(sep)
                if last > chunk_size // 2:
                    chunk = chunk[: last + len(sep)]
                    end = start + len(chunk)
                    break
        chunks.append(chunk.strip())
        start = end - overlap
    return chunks


def _parse_pdf(path: Path) -> str:
    """Extract text from a PDF file."""
    try:
        from pypdf import PdfReader
    except ImportError:
        raise ValueError("PDF support requires pypdf: pip install pypdf")
    reader = PdfReader(str(path))
    parts = []
    for page in reader.pages:
        text = page.extract_text()
        if text:
            parts.append(text)
    return "\n\n".join(parts)


def _parse_csv(path: Path) -> str:
    """Convert CSV to a readable text representation for RAG."""
    with path.open(encoding="utf-8", errors="replace", newline="") as f:
        try:
            dialect = csv.Sniffer().sniff(f.read(4096))
            f.seek(0)
            reader = csv.DictReader(f, dialect=dialect)
            rows = list(reader)
        except Exception:
            f.seek(0)
            reader = csv.reader(f)
            rows = list(reader)
            if not rows:
                return ""
            headers = rows[0]
            rows = [dict(zip(headers, row)) for row in rows[1:]]
    if not rows:
        return ""
    # Format as "Header: value, ..." per row
    lines = []
    for i, row in enumerate(rows[:500]):  # cap rows
        parts = [f"{k}: {v}" for k, v in (row if isinstance(row, dict) else {}).items() if v]
        lines.append(f"Row {i + 1}: " + "; ".join(parts))
    return "\n".join(lines)


def _text_from_file(path: Path) -> str:
    """Get plain text from a file (PDF, CSV, or text)."""
    path = Path(path)
    suffix = path.suffix.lower()
    if suffix == ".pdf":
        return _parse_pdf(path)
    if suffix in (".csv", ".tsv"):
        return _parse_csv(path)
    if suffix in (".txt", ".md", ".json", ""):
        return path.read_text(encoding="utf-8", errors="replace")
    # Default: try as text
    return path.read_text(encoding="utf-8", errors="replace")


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


def process_and_ingest_file(
    file_path: Path,
    base_doc_id: Optional[str] = None,
    metadata: Optional[dict[str, Any]] = None,
) -> list[str]:
    """
    Parse a file (PDF, CSV, or text), chunk if needed, and ingest into RAG.
    Returns list of document ids.
    """
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(str(path))
    text = _text_from_file(path)
    if not text.strip():
        return []
    meta = dict(metadata or {}, source=path.name)
    base = base_doc_id or path.stem
    chunks = _chunk_text(text)
    if len(chunks) == 1:
        return [ingest_document(chunks[0], doc_id=base, metadata=meta)]
    ids = []
    for i, chunk in enumerate(chunks):
        ids.append(ingest_document(chunk, doc_id=f"{base}_chunk{i}", metadata={**meta, "chunk": i}))
    return ids


_ALLOWED_SUFFIXES = {".pdf", ".csv", ".txt", ".md", ".tsv"}


def ingest_directory(dir_path: Path, glob: str = "**/*") -> list[str]:
    """Ingest all matching files in a directory (PDF, CSV, TXT, MD). Returns list of doc ids."""
    path = Path(dir_path)
    if not path.is_dir():
        return []
    ids = []
    for f in sorted(path.glob(glob)):
        if f.is_file() and f.suffix.lower() in _ALLOWED_SUFFIXES:
            try:
                ids.extend(process_and_ingest_file(f))
            except Exception:
                pass
    return ids
