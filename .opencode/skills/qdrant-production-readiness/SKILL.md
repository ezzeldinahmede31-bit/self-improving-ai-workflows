---
name: qdrant-production-readiness
description: "Triage Qdrant connectivity failures (connection reset, 401/403, TLS) and harden a collection for production: the connectivity ladder (DNS, TLS, api-key header, client lib, egress/region, cluster state), the day-one checklist (scalar quantization, payload indexes before ingest, replication factor 2+, snapshots, optimizer-backlog telemetry). Use when Qdrant refuses connections, upserts fail, filtered search is slow, recall drops silently, or a collection must go from demo to production. Pairs with qdrant-ops, n8n-rag-vector-qa, nvidia-embeddings, vector-databases-similarity-search."
---

# Qdrant Production Readiness

Connectivity triage + the production checklist that demos skip.

## Sources (adopted baselines)

- "Mastering Qdrant for RAG Applications" (Leanpub, 2026, complete): full
  feature/ops reference — collections, HNSW, quantization, sharding,
  replication, monitoring runbooks (Ch. 11 distributed, Ch. 13 operations).
- "Vector Databases in Practice" (2026): infra-first RAG — idempotent ingest,
  acceptance gates, backup/restore drills, upgrade rehearsals.
- Qdrant official "Production Checklist" + "Vector Search in Production" guide:
  quantization, payload indexes, replication, snapshots, telemetry.
- ComputingForGeeks Qdrant series (2026): auth/TLS deployment realities.

## 1. Connectivity ladder (in order, stop at first fix)

1. DNS: does the host resolve? (`sa-east-1-0.aws.cloud.qdrant.io` style).
2. TLS/port: REST 6333, gRPC 6334. Cloud URLs are HTTPS-only; raw HTTP = reset.
3. Auth header: `api-key: <key>` (not `Authorization: Bearer`). 401 = wrong key,
   reset/hang = often TLS or egress, not auth.
4. Client lib: reproduce with official `qdrant-client` (pinned, e.g. 1.19.x),
   not raw urllib — eliminates header bugs as a variable.
5. Egress/region: can this box reach that region at all? Test a second endpoint
   (e.g. Qdrant docs) to separate box-egress failure from cluster failure.
6. Cluster state: paused/deleted cloud cluster also presents as reset. Check the
   Cloud dashboard. If the dashboard is green and 1-5 pass, escalate to Qdrant
   support with timestamps — do not rotate keys blindly.

## Worked case (this workspace, 2026-09-19)

`QdrantClient(url, api_key, timeout=10).get_collections()` →
`ResponseHandlingException [Errno 104] Connection reset by peer`, reproduced
with BOTH raw urllib and official `qdrant-client 1.19.1` (installed this
session). Verdict per ladder: past step 4, stuck at 5/6 — network-side or
cluster-side. Needs owner check of Cloud dashboard/egress; key rotation would
be theater.

## 2. Day-one production checklist (new collections)

- Decide vector size/distance/HNSW/quantization BEFORE ingest; painful after
  millions of points. 1024-dim Cosine for this workspace (NVIDIA nv-embedqa).
- Scalar (int8) quantization from day one past ~100k vectors: ~4x RAM, <2%
  recall loss, rescore shortlist against full precision.
- Create payload indexes on EVERY filtered field BEFORE ingesting (HNSW is only
  filter-aware for indexes that predate the data). Missing index = full scan.
- `on_disk=True` for raw vectors when RAM is the ceiling; quantized stay hot.
- Replication factor ≥ 2 (3-node minimum for real failover); isolate prod from
  dev/staging clusters.
- Snapshots automated (cron → off-node storage) + periodic restore drill.
  Snapshots move data; full backups recover state — know which you have.

## 3. Silent-degradation telemetry (what HTTP 200 hides)

Vector DBs fail quietly: recall drops while status stays 200. Watch in order:
optimizer/segment backlog (degrades FIRST — alert on it, not QPS), memory at
index build (>90% = add capacity), p95 search latency, replica health. Cold
restart = slow first queries (cache rebuild); benchmark warm.

## Verification

`get_collections` OK + a filtered top-k search returns expected recall on a
labeled probe set + snapshot restore drill passes. Record endpoint, client
version, and quantization settings in the skill notes.
