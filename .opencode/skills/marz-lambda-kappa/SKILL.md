---
name: marz-lambda-kappa
description: "Architects big-data serving: batch, speed, and serving layers. Use when the user says 'lambda architecture', 'kappa architecture', 'batch layer', 'speed layer', 'serving layer', 'Marz', 'recomputation', or when massive data must be both complete and fresh."
---

# Marz Lambda & Kappa Architecture

Distilled from Nathan Marz *Big Data*: human-fault-tolerant big-data
systems separate immutable history (batch) from incremental freshness
(speed), unified at serving — recomputation beats recovery, always.

## Purpose

Serve accurate, low-latency views over unbounded data with a design where
human error is repairable by construction (recompute, don't surgically fix).

## Lambda (the full answer)

1. **Batch layer: the master dataset.** Immutable, append-only raw data
   (timestamps on everything); precomputed batch VIEWS (MapReduce/Spark
   jobs) that are correct but stale (hours). Properties: raw data never
   deleted (human fault-tolerance = recompute from scratch), views
   disposable and rebuildable.
2. **Serving layer: indexed batch.** Batch views loaded into read-optimized
   stores (random-read DBs, search indexes); swappable/bulk-loaded (never
   mutated in place). Serves the accurate-but-stale half of every query.
3. **Speed layer: freshness.** Incremental updates on recent data only
   (streaming: Storm/Flink/Kafka Streams); complex logic allowed BECAUSE the
   data window is small and results expire. Eventually overwritten by the
   batch layer — speed views are temporary by design.
4. **Query = batch view + realtime view merged.** Application merges the
   two (timestamps arbitrate); complexity lives in exactly one place (the
   merge), everything else stays simple and replayable.

## Kappa (the simplification)

- One streaming pipeline for everything; reprocessing = replaying the log
  (Kafka-style retention required: size the log for full-history replays).
  Adopt when: single code path beats dual maintenance AND the log can retain
  history AND reprocessing throughput meets recovery SLAs. Otherwise Lambda's
  redundancy is the feature, not the cost.

## Decision rule

- Need recomputation-from-raw + tolerate dual code paths: Lambda. Log
  retention affordable + team too small for two systems: Kappa. Neither
  fits small data — a database withCDC plus a cache is not a "big data
  architecture", it is good engineering; say so.

## Verification

Data-architecture review: raw immutability proven (append-only + retention),
recompute drill executed (delete views, rebuild, compare), freshness SLA
measured per query class, merge logic tested on overlapping windows.
Unrecomputable pipelines are liabilities with dashboards.

## Pairs with

- `streaming-systems` (speed-layer machinery),
  `fundamentals-of-data-engineering` (platform),
  `data-pipelines-pocket-reference` (batch practice),
  `event-driven-ai-workflows` (log-centric thinking).
