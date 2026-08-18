---
name: fundamentals-of-data-engineering
description: "Applies Joe Reis & Matt Housley's Fundamentals of Data Engineering to build and operate production data systems: the data engineering lifecycle (generation, ingestion, storage, transformation, serving), choosing storage (OLTP vs OLAP, warehouses, lakes, lakehouses), batch vs streaming architectures, orchestration, and the 'undercurrents' that apply everywhere (security, data management, DataOps, data architecture, orchestration, software engineering). Use when the user says 'design a data pipeline', 'data warehouse vs lake', 'batch vs streaming', 'ELT vs ETL', 'data ingestion', 'data architecture', 'build a data platform', 'lakehouse', 'data orchestration', or when standing up any data infrastructure. Pairs with: data-pipelines-pocket-reference, designing-machine-learning-systems, qdrant-ops, streaming-systems, database-internals-engines."
---

# Fundamentals of Data Engineering

The premise: data engineering is the work of turning raw, messy data into reliable,
usable assets — and it is a lifecycle with explicit stages plus cross-cutting
"undercurrents", not a grab-bag of tools.

## When to use

- Designing or operating any data pipeline, warehouse, lake, or lakehouse.
- Choosing storage for a workload (OLTP vs OLAP, warehouse vs lake).
- Deciding batch vs streaming for ingestion and transformation.
- Standing up the orchestration and governance a data platform needs.

## The lifecycle (the mental model)

1. **Generation** — where the data is born (apps, devices, logs, third parties).
2. **Ingestion** — moving it in: batch (scheduled pulls) vs streaming (event
   streams), with backpressure and idempotency.
3. **Storage** — raw and processed stores (see below).
4. **Transformation** — cleaning, joining, enriching (ETL vs ELT).
5. **Serving** — analytics, ML features, reverse ETL back to operational systems.
6. **Undercurrents** — security, data management, DataOps, data architecture,
   orchestration, software engineering. These apply at every stage; skipping them
   is how data platforms rot.

## Storage choices

- **OLTP**: transactional, row-oriented, low-latency single-row ops (see
  `database-internals-engines`).
- **OLAP**: analytical, column-oriented, scan-heavy (see
  `readings-in-database-systems`).
- **Data warehouse**: curated, modeled, business-facing.
- **Data lake**: raw, cheap, schema-on-read; risk of becoming a swamp without
  governance.
- **Lakehouse**: lake storage plus warehouse features (transactions, ACID on raw
  data).
- Rule: store raw data losslessly, then build curated views on top — never throw
  away the source of truth.

## Batch vs streaming

- **Batch**: simple, exact, cheap to operate; latency of minutes to hours.
- **Streaming**: complex, approximate by nature, low latency; right when freshness
  beats completeness (see `streaming-systems`).
- Choose streaming only when the business truly needs the freshness; otherwise
  batch wins on simplicity and cost.

## Practical rules

- Make ingestion idempotent and replayable (dedupe keys, offsets, watermark
  re-runs).
- Orchestrate dependencies explicitly (see `data-pipelines-pocket-reference`).
- Define data contracts so producers and consumers can change independently.
- Monitor data quality as a first-class signal, not an afterthought.
- Prefer ELT where the warehouse can do the heavy lifting; push transformation to
  the engine that holds the data.

Pairs with: data-pipelines-pocket-reference (pipeline specifics),
designing-machine-learning-systems (ML side), qdrant-ops (vector storage),
streaming-systems (stream semantics), database-internals-engines (engine internals).