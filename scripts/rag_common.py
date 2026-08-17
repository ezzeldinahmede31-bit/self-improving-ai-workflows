#!/usr/bin/env python3
"""Shared RAG helpers: NVIDIA embeddings, langchain-equivalent text splitting,
and Qdrant vector-store CRUD. Encodes the hard-won lessons from the first RAG
build (Apple Q1.pdf -> Qdrant, Aug 2026):

  * Qdrant upsert is **PUT** `/collections/{name}/points?wait=true` — POST on
    that path is the RETRIEVE endpoint and errors with
    `"Format error in JSON body: missing field `ids`"` (verified on Qdrant
    1.19.0). Search/retrieve genuinely IS a POST
    (`/collections/{name}/points/search`).
  * The upsert response shape is
    `{"result": {"operation_id": N, "status": "completed"}, "status": "ok"}`
    — the status lives at `result.status`, not the top level.
  * NVIDIA embeddings (`nvidia/nv-embedqa-e5-v5`) need `input_type`
    passage (index) / query (search) and a small batch (<= 2) to avoid 4xx.
  * Qdrant payload keys are `content` (the chunk text) and `metadata`
    (labels) — matches @langchain/qdrant so the n8n vector-store node can
    read them directly.

Secrets come from the environment / project `.env`
(NVIDIA_API_KEY, QDRANT_URL, QDRANT_API_KEY) — never hardcoded.
"""

from __future__ import annotations

import json
import os
import sys
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

DEFAULT_EMBED_MODEL = "nvidia/nv-embedqa-e5-v5"
EMBED_DIM = 1024
DEFAULT_BATCH = 2
DEFAULT_CHUNK_SIZE = 1000
DEFAULT_CHUNK_OVERLAP = 0


def env_or_dotenv(name: str, default: str = "") -> str:
    """Environment first, then a `KEY=value` .env next to this module, then the
    project-root .env (where the real secrets live)."""
    val = os.environ.get(name)
    if val:
        return val
    for env_path in (Path(__file__).resolve().parent / ".env", ROOT / ".env"):
        if env_path.exists():
            for line in env_path.read_text(encoding="utf-8").splitlines():
                line = line.strip()
                if line.startswith(name + "="):
                    return line.split("=", 1)[1].strip()
    return default


NVIDIA_URL = env_or_dotenv("NVIDIA_URL", "https://integrate.api.nvidia.com/v1")
NVIDIA_KEY = env_or_dotenv("NVIDIA_API_KEY", "")
QDRANT_URL = env_or_dotenv("QDRANT_URL", "").rstrip("/")
QDRANT_KEY = env_or_dotenv("QDRANT_API_KEY", "")


def _require(secret: str, name: str) -> str:
    if not secret:
        raise SystemExit(
            f"missing {name} — set it in the project .env (gitignored) or the "
            f"environment, e.g.:\n  {name}=... in .env"
        )
    return secret


def request(url: str, payload: dict, headers: dict, method: str) -> dict:
    data = json.dumps(payload).encode()
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    with urllib.request.urlopen(req, timeout=180) as r:
        return json.load(r)


# ---------------------------------------------------------------------------
# NVIDIA embeddings
# ---------------------------------------------------------------------------

def embed(texts: list[str], input_type: str = "passage",
          model: str = DEFAULT_EMBED_MODEL, batch_size: int = DEFAULT_BATCH,
          progress: bool = True) -> list[list[float]]:
    """Embed a list of texts. `input_type` must be 'passage' when indexing and
    'query' when searching (nv-embedqa-e5-v5). Batches <= 2 to stay clear of
    NVIDIA's per-request limits."""
    _require(NVIDIA_KEY, "NVIDIA_API_KEY")
    emb: list[list[float]] = []
    for i in range(0, len(texts), batch_size):
        batch = texts[i:i + batch_size]
        out = request(
            NVIDIA_URL + "/embeddings",
            {"model": model, "input": batch, "input_type": input_type},
            {"Authorization": "Bearer " + NVIDIA_KEY,
             "Content-Type": "application/json"},
            "POST",
        )
        emb.extend(e["embedding"] for e in out["data"])
        if progress:
            sys.stderr.write(
                f"  embedded batch {i // batch_size + 1} "
                f"({len(batch)} chunks, {len(batch[0] if batch else [])} dims)\n"
            )
    return emb


def embed_query(query: str, model: str = DEFAULT_EMBED_MODEL) -> list[float]:
    """Embed a single search query (input_type 'query')."""
    return embed([query], input_type="query", model=model, progress=False)[0]


# ---------------------------------------------------------------------------
# RecursiveCharacterTextSplitter (langchain-equivalent)
# ---------------------------------------------------------------------------

def split_text(text: str, chunk_size: int = DEFAULT_CHUNK_SIZE,
               chunk_overlap: int = DEFAULT_CHUNK_OVERLAP,
               separators: list[str] | None = None) -> list[str]:
    """langchain-compatible recursive character split: try ['\\n\\n', '\\n',
    ' ', ''] in order so blocks/paragraphs/sentences stay whole when they fit.
    Overlap is NOT honored in this compact port (0 default) — kept as a param
    for parity; callers needing overlap should use the full langchain port."""
    separators = separators or ["\n\n", "\n", " ", ""]

    def _split(text_in: str, idx: int) -> list[str]:
        if idx >= len(separators):
            return [text_in]
        sep = separators[idx]
        parts = text_in.split(sep) if sep else [text_in]
        result = []
        for p in parts:
            if len(p) > chunk_size:
                result.extend(_split(p, idx + 1))
            else:
                result.append(p)
        return result

    rough = _split(text, 0)
    merged = []
    buf = ""
    for p in rough:
        if len(buf) + len(p) <= chunk_size:
            buf += p
        else:
            if buf:
                merged.append(buf)
            buf = p
    if buf:
        merged.append(buf)
    return [c for c in merged if c and c.strip()]


# ---------------------------------------------------------------------------
# Qdrant
# ---------------------------------------------------------------------------

def _qdrant_headers() -> dict:
    return {"api-key": _require(QDRANT_KEY, "QDRANT_API_KEY"),
            "Content-Type": "application/json"}


def ensure_collection(collection: str, size: int = EMBED_DIM,
                      distance: str = "Cosine") -> dict:
    """Create a collection if it does not already exist (idempotent)."""
    _require(QDRANT_URL, "QDRANT_URL")
    url = QDRANT_URL + f"/collections/{collection}"
    try:
        return request(url, {}, _qdrant_headers(), "GET")
    except urllib.error.HTTPError as e:
        if e.code != 404:
            raise
        return request(url, {"vectors": {"size": size, "distance": distance}},
                       _qdrant_headers(), "PUT")


def delete_all_points(collection: str) -> None:
    """Delete every point in a collection (used by --recreate)."""
    _require(QDRANT_URL, "QDRANT_URL")
    request(QDRANT_URL + f"/collections/{collection}/points/delete",
            {"filter": {}}, _qdrant_headers(), "POST")


def upsert_points(collection: str, points: list[dict],
                  batch: int = 16, progress: bool = True) -> int:
    """Upsert points. **PUT** (POST = retrieve, errors 'missing field ids')."""
    _require(QDRANT_URL, "QDRANT_URL")
    total = 0
    for i in range(0, len(points), batch):
        chunk = points[i:i + batch]
        resp = request(
            QDRANT_URL + f"/collections/{collection}/points?wait=true",
            {"points": chunk}, _qdrant_headers(), "PUT",
        )
        status = resp.get("result", {}).get("status")
        if status != "completed":
            raise RuntimeError(f"Qdrant upsert failed: {resp}")
        total += len(chunk)
        if progress:
            sys.stderr.write(f"  upserted {total}/{len(points)} points\n")
    return total


def search_points(collection: str, vector: list[float],
                  limit: int = 3, with_payload: bool = True) -> list[dict]:
    """Nearest-neighbour search. This IS a POST (the retrieve/search path)."""
    _require(QDRANT_URL, "QDRANT_URL")
    resp = request(
        QDRANT_URL + f"/collections/{collection}/points/search",
        {"vector": vector, "limit": limit, "with_payload": with_payload},
        _qdrant_headers(), "POST",
    )
    return resp.get("result", [])
