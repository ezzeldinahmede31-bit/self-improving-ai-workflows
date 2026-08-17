---
name: qdrant-ops
description: "Operate the workspace's Qdrant vector store safely and correctly — create/delete/search collections, upsert and inspect points, and troubleshoot the classic Qdrant API mistakes (POST vs PUT on /points, payload key shapes, result.status, vector dimension mismatches). Wraps the proven scripts/rag_common.py, rag_ingest.py and rag_query.py CLIs so collection ops never re-discover the hard-won lessons. Use when the user says 'check the Qdrant collection', 're-ingest the docs', 'delete/recreate the collection', 'search the vector store', 'why is retrieval returning nothing', 'Qdrant upsert failing', 'qdrant-ops'. Pairs with n8n-rag-vector-qa, nvidia-embeddings, build-gates-pipeline, rag_ingest.py, rag_query.py."
---

# Qdrant Vector-Store Operations

Operate the Qdrant collections this workspace uses for RAG. Every command below
is proven on the live instance (Qdrant cloud, Aug 2026) and encodes the exact
API shapes that burned the first build.

## Secrets
Qdrant is reached with two gitignored `.env` values (never hardcode):
- `QDRANT_URL` — e.g. `https://<uuid>.sa-east-1-0.aws.cloud.qdrant.io`
- `QDRANT_API_KEY`
Auth header: `api-key: <key>` (+ `Content-Type: application/json`). NVIDIA key
also needed for embedding/searches: `NVIDIA_API_KEY`.

## The API shapes that matter (hard-won)
- **UPSERT is PUT** `/collections/{name}/points?wait=true` with body
  `{"points": [{id, vector, payload}]}`. Using POST on that exact path hits the
  RETRIEVE endpoint and fails with
  `"Format error in JSON body: missing field \`ids\`"`. Verified on Qdrant 1.19.0.
- **Search/retrieve IS a POST** `/collections/{name}/points/search` with
  `{"vector": [...], "limit": N, "with_payload": true}`.
- **Create collection is PUT** `/collections/{name}` with
  `{"vectors": {"size": 1024, "distance": "Cosine"}}`; GET the same path to check
  existence (404 = missing).
- **Delete all points is POST** `/collections/{name}/points/delete` with
  `{"filter": {}}`.
- The upsert response is `{"result": {"status": "completed"}, "status": "ok"}` —
  **check `result.status`**, not the top level. Anything else = failed upsert.
- Payload keys MUST be `content` (chunk text) and `metadata` (labels) to match
  @langchain/qdrant, so the n8n vectorStoreQdrant node reads points directly.
- Dimension mismatch: store vector size must equal the embeddings model dim
  (this workspace: NVIDIA `nv-embedqa-e5-v5` = **1024**). Re-embed after any
  model/dim change, then recreate the collection.

## Collection operations via the scripts (preferred)
Ingest / re-ingest a corpus (splits, embeds with input_type 'passage', upserts):
```
venv/bin/python scripts/rag_ingest.py --text /tmp/rag_ingest/Q1.txt \
    --collection Q1.pdf --chunk-size 1000 --metadata source=Q1.pdf --recreate
```
- `--recreate` drops + recreates so point ids stay 1..N (avoids stale points).
- `--dry-run` splits + embeds and prints the plan WITHOUT touching Qdrant.
- `--batch 2` keeps NVIDIA embeddings happy (batch <= 2).

Search / verify retrieval (embeds input_type 'query', prints top-k with score):
```
venv/bin/python scripts/rag_query.py --collection Q1.pdf --query "Apple's Q1 2024 revenue" --limit 3
```
A healthy collection returns hits with rising scores and the `content` payload.

## Manual API calls (via rag_common helpers or curl)
- `ensure_collection(name, size=1024, distance="Cosine")` — idempotent create.
- `upsert_points(name, points, batch=16)` — returns total upserted, raises on
  non-`completed` status.
- `search_points(name, vector, limit=3, with_payload=True)` — nearest neighbors.
- `delete_all_points(name)` — wipe a collection (re-ingest from scratch).

## Troubleshooting
- Upsert `missing field ids` => POST used where PUT is required (fix method).
- Search returns 0 hits => confirm points exist (GET collection -> `points_count`),
  then confirm dimension/similarity match; check payload keys.
- `api-key` 401 => wrong/rotated key; check `.env`, never paste into files.
- Store node in n8n reads garbage => payload keys aren't `content`/`metadata`.

## Output contract
Report: collections present + point counts, upsert/search status, scores of the
top hits, and which payload keys each point carries. Never claim a collection is
healthy without a live search round-trip.
