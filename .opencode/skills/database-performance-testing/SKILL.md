---
name: database-performance-testing
description: "Database performance testing distilled. Use when testing query plans, indexes, locks, pool sizing, slow queries, migration impact."
---

# Database Performance Testing

## Purpose

Prove the data layer under load: plan analysis, index proof, lock behavior, pool sizing, migration timing on production-shaped data.

## When to use

Use when the user says 'database performance', 'slow query', 'EXPLAIN', 'index test', 'lock contention', 'pool sizing', 'migration timing'.

## Steps

1. Test on production-shaped volumes, never toy datasets.
2. Read plans (EXPLAIN) for hot queries; prove index usage, not hope.
3. Measure lock waits and deadlocks under concurrent writes.
4. Size pools from measured concurrency plus queue depth.
5. Time migrations on copies; verify rollback before promoting.

## Anti-patterns

- Optimizing from averages instead of worst realistic shapes.
- Missing indexes discovered in production.
- Migrations run unmeasured with no rollback rehearsal.
- Pool sized by default and never revisited.

## Example

```sql
EXPLAIN ANALYZE SELECT * FROM orders WHERE user_id = 7 AND status = 'OPEN';
```

Python check: assert plan uses `idx_orders_user_status`.

## Verification

Plans reviewed for hot paths, locks measured, pools sized from data, migrations timed with rollback proven.

## Pairs-with

mysql-query-optimization-indexing, postgresql-up-and-running, soak-endurance-testing, test-data-management.
