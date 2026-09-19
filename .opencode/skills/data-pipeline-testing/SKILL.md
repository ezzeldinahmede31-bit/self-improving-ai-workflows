---
name: data-pipeline-testing
description: "Data pipeline testing distilled. Use when testing ingestion, transforms, schema evolution, data quality checks, pipeline idempotency."
---

# Data Pipeline Testing

## Purpose

Prove data flows correctly: ingestion conformance, transform logic, schema evolution safety, quality checks, rerun-safe idempotency.

## When to use

Use when the user says 'data pipeline test', 'ETL test', 'data quality', 'schema evolution', 'ingestion test', 'dbt test'.

## Steps

1. Test ingestion against malformed, late, and duplicate source records.
2. Unit-test transforms with representative fixtures plus edge rows.
3. Guard schemas: compatibility checks on every change.
4. Add quality checks (nulls, ranges, uniqueness) as pipeline gates.
5. Prove reruns safe: same input twice yields same output once.

## Anti-patterns

- Testing on tiny toy data while production skew breaks logic.
- No schema compatibility check across producer changes.
- Quality checks logged but never gating.
- Reruns duplicating outputs silently.

## Example

Python (pandas transform check):

```python
def test_dedup_keeps_latest():
    out = dedup(rows_with_dupes)
    assert out["id"].is_unique
```

## Verification

Fixtures realistic, schemas guarded, quality gated, reruns idempotent.

## Pairs-with

etl-validation-patterns, data-pipelines-pocket-reference, fundamentals-of-data-engineering, validation-gate-data-quality.
