---
name: elasticsearch-search-relevance
description: "Builds search that ranks: inverted indexes, analyzers, and relevance tuning. Use when the user says 'Elasticsearch', 'full-text search', 'relevance tuning', 'BM25', 'analyzers', 'shards and replicas', 'search relevance', or when find must mean find-the-right-thing."
---

# Elasticsearch Search & Relevance

Distilled from Gormley/Tong *Elasticsearch: The Definitive Guide* plus
modern BM25 practice: search = tokenize right, distribute safely, score
honestly — then measure relevance like a product metric, not a vibe.

## Purpose

Deliver search users trust: correct analysis per language, resilient
distribution, and ranking tuned against judged queries.

## The stack (in build order)

1. **Analysis decides everything downstream.** Character filters ->
   tokenizer -> token filters (lowercase, stop, stem/snowball, synonyms,
   edge-ngrams for autocomplete). Test EVERY field with the _analyze API
   before indexing a document — wrong tokens can never rank right.
   Language-specific analyzers per field (CJK needs morphological
   tokenizers, not whitespace splitting).
2. **Map deliberately.** Explicit mappings (types, keyword vs text, norms on/
   off, doc_values for sorting/aggs); dynamic mapping disabled or strictly
   templated in production. Reindex strategy ready (aliases point at the
   live index; rebuilds swap atomically).
3. **Distribute for survival.** Shards for parallelism, replicas for
   availability; shard sizing (tens of GB each, not thousands of tiny
   shards — cluster state is the ceiling); dedicated master/data/ingest
   roles at scale; snapshots to remote storage tested by restore.
4. **Score with BM25, tune with judgments.** BM25 (k1 saturation, b length
   normalization) as the sane default; function_score/boosting for business
   signals (recency, popularity) kept SEPARATE from text relevance so each
   is debuggable. Relevance = judged query set + NDCG/MRR tracked per
   release; "feels better" is not a metric.
5. **Operate the hot path.** Slow-log + search profiler for bad queries;
   circuit breakers and queue sizing for spikes; index lifecycle (hot/warm/
   cold) for time-series data; version upgrades via rolling + reindex plan.

## Verification

Search review: _analyze output per field, mapping explicitness confirmed,
judged query set with NDCG trend, snapshot/restore tested, shard sizing
math shown. Shipping search without judged queries is shipping blind.

## Pairs with

- `ir-vector-space-ranking` (ranking theory),
  `hybrid-search-keyword-vector-v2` (BM25 + vectors),
  `sre-workbook-practices` (operating the cluster),
  `monitoring-logging-alerting-distributed` (search observability).
