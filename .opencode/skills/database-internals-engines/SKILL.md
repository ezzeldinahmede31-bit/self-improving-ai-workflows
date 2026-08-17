---
name: database-internals-engines
description: "Applies Alex Petrov's Database Internals knowledge to design and troubleshoot storage-backed systems: how storage engines actually work under the hood (B-Trees vs LSM-Trees, page formats, write-ahead logging, compaction), indexes (primary, secondary, covering), transaction processing (ACID, isolation levels, MVCC, 2PL, locking), replication, and distributed consensus (Raft/Paxos). Use when the user says 'how does this database work internally', 'why is this query slow', 'B-tree or LSM', 'pick a storage engine', 'isolation level', 'MVCC', 'replication lag', 'consensus', 'Raft', 'write amplification', 'compaction', 'distributed database design', or when designing a persistent state store that must survive crashes and scale. Pairs with: state-machine-persistence, qdrant-ops, agent-arch-system-design, zero-trust-modular-decomposer."
---

# Database Internals — Storage Engines & Distributed Data

Petrov's book explains what happens under the hood of a database: the storage
engine, the index, the transaction machinery, and the replication/consensus layer.
Knowing these internals is what turns "the database is slow" into a precise
diagnosis and a correct design choice.

## When to use

- Choosing or designing a storage layer (SQL, key-value, document, vector store).
- Diagnosing write amplification, read amplification, space amplification, or
  replication lag.
- Designing a stateful service that must survive crashes (durability) and scale
  (replication + partitioning).
- Understanding why an index choice or isolation level behaves as it does.

## The engine decision (B-Tree vs LSM)

| Property | B-Tree (Postgres, MySQL/InnoDB) | LSM-Tree (RocksDB, Cassandra, Qdrant, InfluxDB) |
|---|---|---|
| Write path | In-place page update + WAL | Append-only memtable → sorted runs, background compaction |
| Read path | Single indexed lookup | Check memtable + several runs (bloom filters help) |
| Write amplification | Lower | Higher (compaction) |
| Read amplification | Lower | Higher (run merging) |
| Space | Packed pages | Sparse until compaction |

- Choose B-Tree for read-heavy, point-lookup, and strong-consistency workloads.
- Choose LSM for write-heavy, append-mostly workloads where sequential writes win.
- Always confirm which engine the product uses before promising behavior (see
  `evidence-over-memory`).

## Indexes and query shapes
- Primary (clustered) index orders the rows themselves; secondary indexes store the
  key + primary key reference (extra lookup).
- A covering index serves a query without touching the table — use when a hot query
  needs only a few columns.
- Prefix matching only helps leftmost columns of a composite index; confirm the
  planner can use it.

## Durability and transactions
- WAL first: every committed write is in the log before the reply; crash recovery
  replays it.
- Isolation levels map to concrete mechanisms: snapshot isolation/MVCC (readers never
  block writers), 2PL (write locks), and the anomalies each level permits (dirty
  read, non-repeatable read, phantom). Name the anomaly a chosen level allows before
  picking it.
- Distributed transactions add commit coordination (two-phase commit) and its
  availability trade-offs — prefer avoiding cross-partition transactions when the
  workload allows.

## Replication and consensus
- Leader-based replication (single writer, followers apply) vs leaderless
  (quorum reads/writes). Replication lag causes read-your-writes and monotonic read
  anomalies — state which guarantee a feature needs.
- Consensus (Raft/Paxos) gives a safe replicated log for the metadata plane; it is
  expensive — use it for coordination (leader election, config), not for the data
  path.

## Verification
- For any design claim, state the engine, the index structure, and the isolation
  level you are assuming — then verify against the actual product docs (evidence
  over memory).
- Profile the real write/read amplification with the product's metrics before
  tuning anything (see `systems-performance-profiling`).

## Pairs with
- `state-machine-persistence` — durable state design for workflows/agents.
- `qdrant-ops` — LSM-style vector store operations (this workspace's Qdrant).
- `agent-arch-system-design` — choosing storage in the system architecture.
- `zero-trust-modular-decomposer` — isolating the storage layer behind a contract.