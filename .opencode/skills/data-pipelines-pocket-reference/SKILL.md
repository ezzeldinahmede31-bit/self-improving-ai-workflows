---
name: data-pipelines-pocket-reference
description: "Applies James Densmore's Data Pipelines Pocket Reference to design, build, test, and operate robust data pipelines: pipeline types and lifecycle, ingestion patterns, transformation responsibilities, orchestration, and the operations layer (monitoring, alerting, testing, CI/CD for data). Use when the user says 'build a data pipeline', 'pipeline design', 'ingestion pattern', 'transformation step', 'pipeline orchestration', 'pipeline testing', 'CI/CD for data', 'data quality monitoring', 'ETL pipeline', or when a pipeline must be run and maintained by a team. Pairs with: fundamentals-of-data-engineering, designing-event-driven-systems, devops-handbook-flow, continuous-delivery-pipeline, sre-reliability-engineering."
---

# Data Pipelines Pocket Reference

The premise: a pipeline is a series of steps that ingest, transform, and serve
data — and the discipline that keeps pipelines alive is design simplicity,
testing, and operations, not cleverness.

## When to use

- Designing a new ingestion or transformation pipeline.
- Making an existing pipeline testable and reliable.
- Setting up orchestration, monitoring, or CI/CD for data.

## Pipeline anatomy

1. **Ingestion** — extract from a source (batch pull or streaming push).
2. **Transformation** — clean, validate, join, aggregate.
3. **Serving / delivery** — load to the target (warehouse, store, app, report).
- Every step should be small, single-purpose, and independently testable.

## Ingestion patterns

- **Push vs pull**: sources that push (webhooks, event streams) vs destinations
  that pull (scheduled batch reads).
- **Full vs incremental**: full loads are simple but costly; incremental loads
  need a reliable cursor (timestamp, offset, watermark).
- **Idempotency**: a re-run of the same step must not duplicate data — dedupe keys
  and clear-and-reload for full loads.
- Handle schema drift explicitly (producer changes shape → validate and alert, do
  not fail silently).

## Transformation responsibilities

- Keep transformations declarative where possible (SQL) and reserve code for
  steps that need it.
- Log the lineage of every output so a result can be traced to its inputs.
- Split large transforms into stages with intermediate storage so failures are
  resumable.

## Orchestration

- Orchestrate by dependency graph, not by fixed schedule (a job runs when its
  inputs are ready).
- Retry with backoff; treat a flaky dependency as a pipeline failure, not a
  nuisance.
- Give every run an ID and persist run metadata (see `state-machine-persistence`).

## Operations and testing

- Test data inputs and outputs, not just code: schema checks, row-volume and
  null-rate guards on every stage.
- Run the pipeline in CI on sample data before it ever reaches production.
- Alert on freshness (a job that did not run) and on quality (a job that ran but
  produced bad data).
- Build a rollback path: keep enough history to reprocess from a prior state.

Pairs with: fundamentals-of-data-engineering (lifecycle),
designing-event-driven-systems (events), devops-handbook-flow (deployment
discipline), continuous-delivery-pipeline (CI/CD), sre-reliability-engineering
(SLOs).