---
name: etl-validation-patterns
description: "ETL validation patterns distilled. Use when reconciling sources to targets, row reconciliation, totals checks, slowly changing dimensions."
---

# ETL Validation Patterns

## Purpose

Reconcile with rigor: source-to-target row matching, totals and hash checks, slowly-changing-dimension logic, reject handling.

## When to use

Use when the user says 'ETL validation', 'reconciliation', 'source target match', 'totals check', 'SCD test', 'reject handling'.

## Steps

1. Reconcile row identity: every source row accounted in target or rejects.
2. Check totals and hashes per partition, not only global sums.
3. Test slowly-changing logic: history preserved, current flagged.
4. Verify rejects land quarantined with reasons, never dropped.
5. Automate the pack per load with trend alerts on drift.

## Anti-patterns

- Global totals matching while partitions silently differ.
- Rejects deleted instead of quarantined.
- SCD overwrites destroying history.
- Manual spreadsheet reconciliation per release.

## Example

Python:

```python
assert target_hash(partition) == source_hash(partition)
assert set(rejects["reason"]).issubset(KNOWN_REASONS)
```

## Verification

Identity reconciled, partitions hashed, history preserved, rejects quarantined with reasons.

## Pairs-with

data-pipeline-testing, fundamentals-of-data-engineering, test-data-management, quality-metrics-dashboard.
