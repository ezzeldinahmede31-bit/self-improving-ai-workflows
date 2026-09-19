---
name: winand-sql-indexing
description: "Indexes SQL correctly across vendors: B-trees, concatenation order, and execution plans. Use when the user says 'slow query', 'index design', 'composite index', 'covering index', 'execution plan', 'function-based index', 'Use The Index Luke', 'Winand', or when any SQL must be fast on any database."
---

# Winand SQL Indexing

Distilled from Markus Winand's *SQL Performance Explained* (Use The Index,
Luke): indexes are ordered structures and queries are range conditions —
performance comes from matching the two, identically on every major RDBMS.

## Purpose

Make any query fast on any database by designing indexes from access
patterns and verifying with execution plans — vendor-neutral principles,
vendor-specific syntax.

## The principles (work on Oracle/Postgres/SQL Server/MySQL alike)

1. **Think in B-trees.** Leaf nodes chained in order; equality descends,
   ranges scan forward. An index serves a query only if its leading columns
   constrain the search — unindexed leading columns mean full scans no
   matter what follows.
2. **Concatenation order = query order.** Equality columns first (any order
   among them), then ONE range column, then ORDER BY / covering columns.
   A second range column after the first is decoration — the tree cannot use
   it for seeking (filter only). Getting this order right fixes most slow
   queries outright.
3. **Covering indexes end lookups.** INCLUDE/select-list columns make the
   index answer alone (index-only scans); table access per row is the hidden
   cost that covering eliminates. Wide indexes cost writes — cover hot
   reads, not everything.
4. **Functions kill indexes (unless indexed).** `WHERE UPPER(name)=` cannot
   seek a plain index — function-based/expression indexes restore it.
   Implicit conversions (string vs number) do the same damage silently;
   match types exactly.
5. **LIKE, pagination, and top-N.** Prefix LIKE seeks, `%leading` scans
   (trigram/full-text indexes as the escape); keyset pagination beats OFFSET
   (OFFSET re-reads discarded rows every page); top-N needs the ORDER BY
   indexed or the whole set sorts.
6. **Read the plan, trust nothing else.** EXPLAIN shows access path (seek vs
   scan), join order/method, and row estimates vs actuals. Stale statistics
   lie to optimizers — refresh them before redesigning. Hints last, schema
   first.

## Verification

Per slow query: plan captured before AND after, index definition with column
order justified by the equality/range rule, statistics fresh, write-cost
acknowledged. "Added an index" without the before/after plan is superstition.

## Pairs with

- `mysql-query-optimization-indexing` (MySQL specifics),
  `high-performance-mysql` (server tuning),
  `postgresql-up-and-running` (Postgres specifics),
  `karwin-sql-antipatterns` (what not to write).
