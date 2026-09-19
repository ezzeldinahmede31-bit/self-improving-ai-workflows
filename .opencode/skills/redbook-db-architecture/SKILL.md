---
name: redbook-db-architecture
description: "Architects database engines the Red Book way: process models, storage, access paths, and query layers. Use when the user says 'database architecture', 'storage engine', 'access method', 'query processing layers', 'Hellerstein Stonebraker', 'Red Book', or when designing or dissecting a DBMS internals."
---

# Red Book Database Architecture

Distilled from Hellerstein/Stonebraker/Harizopoulos *Architecture of a
Database System*: every DBMS is the same five layers with different choices
at each — name the choices and you understand the engine.

## Purpose

Reason about any database engine structurally: which process model, which
storage layout, which access methods, which concurrency/recovery scheme —
and what workload each combination serves.

## The five layers (choices per layer)

1. **Process model.** Process-per-DBMS (classic, isolation at OS cost) vs
   thread-per-connection vs event-driven/pool (high concurrency, cooperative
   discipline). The model caps connection scale before any tuning matters.
2. **Storage and memory.** Heap files + slotted pages (variable-length
   records, free-space maps); buffer manager (page replacement with DB-aware
   policies — LRU-K, clock — because generic LRU scans poison caches);
   storage above memory is a cache hierarchy, treat it as one.
3. **Access methods.** B+-trees (ordered scans + point lookups, the default);
   hash (equality only); GiST-style extensibility (one framework, many
   types); bitmap/zone maps for analytics pruning. Index choice follows
   query shape — list the queries first.
4. **Query processing.** Parser -> rewriter -> optimizer (cost-based,
   System-R heritage: statistics + selectivity + plan enumeration) ->
   executor (iterator/volcano model vs vectorized/batched). Volcano's
   per-tuple overhead is why analytics engines went columnar+vectorized.
5. **Transactions and recovery.** Concurrency (2PL vs MVCC/OCC per workload)
   + logging (WAL with steal/no-force = ARIES lineage) + checkpoints.
   The layer where correctness lives — never improvised.

## Reading-an-engine protocol

Given any engine, fill the five rows in an hour from docs/code: process
model, page format, index set, executor shape, CC+recovery scheme. Gaps in
the table are the questions to ask maintainers. Two engines with identical
rows differ only in tuning.

## Verification

Architecture review ships the five-row table plus the workload verdict
(OLTP/OLAP/mixed and why this combination fits). Hand-waving about
"performance" without naming the layer responsible is rejected.

## Pairs with

- `database-internals-engines` (mechanism depth),
  `readings-in-database-systems` (foundational papers),
  `mohan-aries-recovery` (recovery half),
  `database-management-systems` (optimizer theory).
