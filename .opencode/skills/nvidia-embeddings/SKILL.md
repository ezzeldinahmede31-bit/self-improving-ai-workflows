---
name: nvidia-embeddings
description: "Embed text with NVIDIA's nv-embedqa-e5-v5 via the integrate.api.nvidia.com API — correct input_type (passage when indexing, query when searching), small batches (<=2), and the 1024-dimension contract that must match the Qdrant collection size. Wraps the proven scripts/rag_common.py embed()/embed_query() so embeddings are called with the right payload every time, and flags the classic 4xx causes. Use when the user says 'embed these docs', 'why is embedding failing', 'NVIDIA embeddings 400', 'vector dimension mismatch', 'input_type', 'nvidia-embeddings', or when building a RAG ingest/query step. Pairs with qdrant-ops, n8n-rag-vector-qa, rag_ingest.py, rag_query.py."
---

# NVIDIA Embeddings (nv-embedqa-e5-v5)

Embed text through NVIDIA's hosted embeddings API for the RAG pipeline. Proven
live (Aug 2026) on this workspace's Apple Q1.pdf pipeline and encoded in
`scripts/rag_common.py`.

## Endpoint & secret
- Base: `https://integrate.api.nvidia.com/v1`, path `/embeddings`, method POST.
- Auth: `Authorization: Bearer <NVIDIA_API_KEY>` (+ `Content-Type: application/json`).
- Secret comes from env / gitignored `.env` — never hardcode.

## The two things that make it work (hard-won)
1. **`input_type` is mandatory** for `nv-embedqa-e5-v5`:
   - `"input_type": "passage"` when embedding chunks for INDEXING.
   - `"input_type": "query"` when embedding a search question.
   Missing or wrong `input_type` => 4xx (NVIDIA rejects the request).
2. **Batch <= 2.** Larger batches hit NVIDIA's per-request limit and 4xx. The
   n8n vectorStoreQdrant "Insert" node and `rag_common.embed()` both use small
   batches by design.

## Payload
```json
POST https://integrate.api.nvidia.com/v1/embeddings
{"model": "nvidia/nv-embedqa-e5-v5", "input": ["chunk text", "..."], "input_type": "passage"}
```
Response: `{"data": [{"embedding": [...], "index": 0, "object": "embedding"}]}`.
Each embedding is **1024 floats** — the Qdrant collection vector size must be
1024 (Cosine). Changing model/dimension means re-embedding AND recreating the
collection.

## Usage
Index (passage):
```
venv/bin/python scripts/rag_ingest.py --text file.txt --collection NAME --recreate
```
Search (query): `scripts/rag_query.py --query "..." --collection NAME` (embeds
with `input_type: query` then searches Qdrant).

Direct: `scripts/rag_common.py` exposes `embed(texts, input_type="passage")`
and `embed_query(query)`.

## Troubleshooting
- 400/422 => check `input_type` present and valid (passage/query); check `input`
  is an array of strings; check batch size <= 2.
- 401 => NVIDIA_API_KEY wrong/rotated; update `.env`.
- Embeddings returned but search finds nothing => dimension mismatch with the
  Qdrant vector size, or store payload keys not `content`/`metadata`.
- Slow first call => cold model load; retry once before assuming failure.

## Output contract
Report: model, embedding dimension (must be 1024), input_type used per call,
batch sizes, and a successful round-trip (embed -> search hit) as evidence.
