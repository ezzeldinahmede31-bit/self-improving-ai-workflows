---
name: data-intensive-application-design
description: "Applies Martin Kleppmann's Designing Data-Intensive Applications (DDIA) to automation, storage, and pipeline design: the reliability-scalability-maintainability triangle, data models, storage engines (log-structured vs B-tree), replication (single-leader/multi-leader/leaderless, consistency models), partitioning, and the trade-offs of strong vs eventual consistency. Ensures honest engineering trade-off statements instead of magic 'it scales' claims, and guides choosing the right database and replication strategy per workload. Use when the user says 'DDIA', 'data-intensive', 'replication', 'partitioning', 'consistency model', 'eventual consistency', 'strong consistency', 'CAP', 'storage engine', 'LSM', 'B-tree', 'relational vs NoSQL', 'which database', or when a pipeline must survive load and partial failure. Pairs with: database-internals-engines, qdrant-ops, cloud-native-patterns, agent-arch-system-design."
---
# Data-Intensive Application Design (DDIA - Kleppmann)

Kleppmann's foundation: every data system is judged on three properties - Reliability (works despite faults), Scalability (grows with load), Maintainability (humans can work on it). Every design decision is a TRADE-OFF, and honest engineering states the trade-off.

## The Three Pillars

1. **Reliability**: the system keeps working even when things go wrong (hardware, software, human faults). Faults are expected - design for them.
2. **Scalability**: defined only relative to a workload. 'Scales' is meaningless without: load parameters (requests/sec, data size, read:write ratio) and performance targets (latency percentiles).
3. **Maintainability**: operability (easy ops), simplicity (manageable complexity), evolvability (easy to change). Code that nobody can maintain is a liability even if fast.

## Storage Engine Selection (log-structured vs B-tree)

| Engine | Write pattern | Read pattern | When to choose |
|---|---|---|---|
| B-tree (traditional RDBMS) | Random updates in place | Point lookups, ranges | General OLTP, strong transactional guarantees |
| LSM-tree (RocksDB, Cassandra, HBase) | Append-only, batched | Slightly slower point reads | Write-heavy, high write throughput |
| Columnar | Bulk analytics scans | Aggregations over big tables | OLAP / reporting |

## Replication Strategies (the consistency spectrum)

- **Single-leader**: one writer, many read replicas. Strong ordering, but a single point for writes.
- **Multi-leader**: writes in several places, conflicts to resolve. Availability + latency, but conflict resolution is YOUR job.
- **Leaderless (Dynamo-style)**: any node accepts writes, quorum reads. Max availability, weakest ordering guarantees.

### Consistency models (what each really promises)
- **Strong (linearizable)**: reads see the latest committed write - expensive, limited by leader.
- **Read-your-writes**: the user always sees their own recent writes - the minimum for good UX in most apps.
- **Eventual**: replicas converge eventually - fine for caches, counters, feeds; wrong for balances, inventory, unique constraints.

### How to think about CAP
- CAP is a lens, not a theorem you 'satisfy'. During a partition you choose: availability (keep serving, risk stale reads) or consistency (block, return errors). Choose PER OPERATION, and say which you chose.

## Partitioning (sharding) rules

- Partition by key range or by hash. Hash partitioning spreads load evenly but loses range scans.
- Skew (hot spots) kills hash partitioning - a single hot key still lands on one node.
- Rebalancing must not stop the system (avoid naive mod-N resharding: N changes move almost everything).

## Design Checklist (honest engineering)

- [ ] Load parameters named (requests/sec, data size, read:write ratio) before any scaling claim
- [ ] Reliability: fault injection considered (node dies, disk full, duplicate delivery)
- [ ] Consistency model chosen PER OPERATION and documented
- [ ] Replication strategy matches the consistency requirement (eventual vs read-your-writes vs strong)
- [ ] Partitioning accounts for hot keys
- [ ] Maintainability: a new engineer can trace a write end-to-end in one session

## Violations (severity)

- **V1 - 'It scales' with no load parameters** (HIGH): Scaling claims without workload definition. Fix: state load params and targets.
- **V2 - Strong consistency everywhere** (HIGH): Paying for linearizability on caches/feeds that only need eventual. Fix: choose per operation.
- **V3 - Conflict resolution ignored** (HIGH): Multi-leader chosen without a conflict-resolution plan. Fix: pick a resolution rule (LWW, CRDT, explicit merge).
- **V4 - Hot key ignored** (MEDIUM): Hash partitioning assumed even though one key dominates. Fix: split hot keys.
- **V5 - Faults treated as impossible** (MEDIUM): No retry/idempotency/backpressure design. Fix: design for duplicate and missing messages.

## Verification

For any pipeline claiming scale or consistency: produce a one-paragraph trade-off statement (reliability/scalability/maintainability + consistency choice) and run the build gates to READY_FOR_DEPLOYMENT.
