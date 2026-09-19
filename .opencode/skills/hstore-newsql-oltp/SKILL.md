---
name: hstore-newsql-oltp
description: "Runs OLTP at memory speed the H-Store/VoltDB way: partitioning, determinism, and stored procedures. Use when the user says 'NewSQL', 'H-Store', 'VoltDB', 'main-memory database', 'deterministic execution', 'single-threaded partitions', or when OLTP throughput must scale without giving up transactions."
---

# H-Store NewSQL OLTP

Distilled from Stonebraker et al.'s H-Store/VoltDB lineage: traditional
RDBMS spend ~90% of time on overhead (locking, latching, logging, buffer
management) — remove disk from the hot path and transactions get two orders
of magnitude faster.

## Purpose

Serve high-rate transactional workloads with full ACID by executing
serially per partition in memory — coordination eliminated by design, not
by tuning.

## The design (each piece removes a classic overhead)

1. **Partition everything.** Tables hash-partitioned across sites; each
   partition single-threaded (no locks, no latches — serial execution IS
   the concurrency control). Schema design = partition design: the
   partition key must make the hot transactions single-sited.
2. **Procedures, not ad-hoc SQL.** Transactions arrive as STORED PROCEDURES
   (Java/SQL): all logic known up front, no interactive round-trips
   mid-transaction. Ad-hoc queries go to replicas or the OLAP side —
   never into the latency-critical path.
3. **Deterministic ordering.** Same input order + deterministic procedures =
   same state on every replica (active-active without 2PC). Nondeterminism
   banned inside procedures (no wall-clock, no random) — or logged and
   replayed.
4. **Durability without the disk tax.** Command logging (log the procedure
   + parameters, tiny) instead of ARIES row logging; periodic snapshots +
   replay for recovery; k-safety (each partition on k+1 nodes) for
   availability. Group commit batches the fsync cost.
5. **Multi-partition honestly.** Cross-partition transactions need
   coordination (speculative execution + 2PC fallback): minimize them by
   schema design, measure their share, and never let them dominate —
   a NewSQL system running mostly distributed transactions is a slow,
   expensive distributed system.

## When NOT NewSQL

- Ad-hoc analytics (use columnar), huge data past memory (use disk-based +
  caching tiers), or unpartitionable hot spots (single-partition writes cap
  at one core — replicate reads, split the keyspace, or admit the limit).

## Verification

Design review: partition map with hot-transaction locality proven,
procedure catalog (no ad-hoc in hot path), determinism audit per procedure,
k-safety + snapshot/replay tested by kill-and-recover, multi-partition
share measured. Throughput claimed without the partition math is marketing.

## Pairs with

- `spanner-calvin-commit` (deterministic cousin),
  `database-transaction-isolation` (correctness semantics),
  `redbook-db-architecture` (engine anatomy),
  `systems-performance-profiling` (proving the throughput).
