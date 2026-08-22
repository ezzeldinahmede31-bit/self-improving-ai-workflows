---
name: data-intensive-applications
description: Applies Martin Kleppmann's Designing Data-Intensive Applications to automation, storage, and pipeline design: the reliability-scalability-maintainability triangle, data models, storage engines (log-structured vs B-tree), replication (single-leader/multi-leader/leaderless, consistency models), partitioning, and the trade-offs of strong vs eventual consistency. Ensures honest engineering trade-off statements instead of magic 'it scales' claims, and guides choosing the right database and replication strategy per workload. Use when the user says 'DDIA', 'data-intensive', 'replication', 'partitioning', 'consistency model', 'eventual consistency', 'strong consistency', 'CAP', 'storage engine', 'LSM', 'B-tree', 'relational vs NoSQL', 'which database', or when a pipeline must survive load and partial failure. Pairs with: database-internals-engines, qdrant-ops, cloud-native-patterns, agent-arch-system-design.
---

# Data-Intensive Applications (DDIA) Skill

## Core Framework: The Three Concerns

Every data system design decision maps to one of three concerns:

| Concern | Question | Key Metrics |
|---------|----------|-------------|
| **Reliability** | Does it work correctly when things go wrong? | Fault tolerance, data durability, no corruption |
| **Scalability** | Can it handle growth? | Load metrics (req/s, GB/day), p50/p95/p99 latency |
| **Maintainability** | Is it operable and evolvable? | Simplicity, observability, modular boundaries |

**Rule**: Start from requirements, then choose tools — never the reverse.

---

## Data Models & Query Languages (Ch 2)

| Model | Structure | Best For | Trade-offs |
|-------|-----------|----------|------------|
| Relational | Tables, rows, strict schema | Joins, many-to-many, long-term integrity | Normalization overhead, impedance mismatch |
| Document (JSON) | Nested, flexible schema | Hierarchical data, key-based access | Weak joins, many-to-many painful |
| Graph | Nodes, edges, properties | Highly connected data | Specialized, niche |
| Columnar | Columns, compressed | OLAP, analytics scans | Write-optimized via LSM |

**Decision**: Match data shape + access pattern, not favorite DB.

---

## Storage Engines (Ch 3)

| Engine | Write Path | Read Path | Use When |
|--------|------------|-----------|----------|
| **B-Tree** (PostgreSQL, MySQL) | Overwrite pages in-place | Fast, predictable range scans | Mixed read/write, strong consistency |
| **LSM-Tree** (Cassandra, RocksDB, LevelDB) | Append to log + memtable, background compaction | May merge segments, Bloom filters help | High-volume ingest, write-heavy |

**Law**: "Well-chosen indexes speed up reads, but every index slows down writes" (p. 71).

---

## Encoding & Evolution (Ch 4)

| Format | Typing | Evolution | Use Case |
|--------|--------|-----------|----------|
| JSON/XML | None/loose | Flexible, human-readable | Interop, config, low-volume |
| Protobuf/Thrift/Avro | Strong, schema-defined | Forward/backward compatible via field rules | Services, high-volume, polyglot |

**Contracts**: 
- Backward compat: new code reads old data
- Forward compat: old code ignores new fields
- Only add optional fields, never rename/remove required

---

## Replication (Ch 5)

| Topology | Write Model | Consistency | Failure Handling |
|----------|-------------|-------------|------------------|
| **Single-leader** | Leader only | Read-your-writes (sync), eventual (async) | Failover = promote follower, handle lag |
| **Multi-leader** | Multiple leaders | Conflict resolution (LWW, CRDTs, app merge) | Geo-distributed, offline writes |
| **Leaderless** (Dynamo) | Quorum: R + W > N | Tunable via quorum | Highest availability, vector clocks for conflicts |

**Key insight**: "All difficulty in replication lies in handling changes to replicated data" (p. 151).

---

## Partitioning (Ch 6)

| Strategy | Ordering | Hotspot Risk | Secondary Index |
|----------|----------|--------------|-----------------|
| Key range | Preserved | High (celebrity keys) | Local per partition |
| Hash of key | Lost | Low | Global or local |

**Routing**: Fixed partitions, dynamic (consistent hashing), or coordination service (ZooKeeper).

---

## Transactions & Isolation (Ch 7)

| Level | Dirty Reads | Non-repeatable | Lost Updates | Write Skew | Phantoms |
|-------|-------------|----------------|--------------|------------|----------|
| Read Committed | ✓ prevented | ✗ | ✗ | ✗ | ✗ |
| Snapshot Isolation | ✓ | ✓ | ✓ | ✗ (detected by SSI) | ✗ |
| Serializable (2PL) | ✓ | ✓ | ✓ | ✓ | ✓ |
| Serializable (SSI) | ✓ | ✓ | ✓ | ✓ (aborts) | ✓ |

**Reality**: "ACID has become mostly a marketing term" — isolation levels vary by DB.

---

## Distributed Systems Reality (Ch 8)

**The network lies**: unanswered request ≠ failure (could be GC pause, minutes long).

**Clocks lie**: 200 ppm drift = 17 sec/day without sync. Fencing tokens fix this.

**Processes pause**: Stop-the-world GC can exceed lease times.

---

## Consistency & Consensus (Ch 9)

| Concept | Meaning |
|---------|---------|
| **Linearizability** | Illusion of single copy; Alice sees write, Bob after hears sees it |
| **CAP** | Misleading — partition is a fault, not a choice. "CAP is best avoided" |
| **Consensus** | Total order broadcast (Raft, Paxos, Zab) = replicated log |
| **Fencing** | Increasing token verified by storage prevents split-brain |

---

## Derived Data & Dataflow (Ch 10-12)

**Core idea**: "Your application state is the integral of its event stream" (p. 460).

Instead of writing to DB + cache + index (3 writes that contradict):
1. Write to ordered log (Kafka)
2. Derive everything else: indexes, caches, search, analytics
3. Change Data Capture (Debezium) = "database inside-out"

| Pattern | Tool | Latency | Use Case |
|---------|------|---------|----------|
| Batch | MapReduce, Spark | Minutes-hours | Analytics, ML training |
| Stream | Flink, Kafka Streams | Seconds | Real-time dashboards, fraud |
| CDC | Debezium, Materialize | Near-real-time | Sync DB → search/index/cache |

---

## Decision Checklist for Any Pipeline

Before building, answer:
1. What are the **load parameters** (distribution, not averages)?
2. What **consistency** do users actually need (read-your-writes? causal? serializable?)?
3. Can we **derive** views from a log instead of dual-writing?
4. Which **storage engine** matches our read/write ratio?
5. How do we handle **schema evolution** (backward/forward compat)?
6. What happens during **network partition** (availability vs consistency)?
7. Are we measuring **p95/p99 latency**, not averages?

---

## Anti-Patterns to Avoid

- ❌ "We'll just use Cassandra, it scales" (no workload analysis)
- ❌ Dual-write to DB + cache + search without CDC
- ❌ Treating schema as afterthought (no evolution strategy)
- ❌ Assuming linearizable reads come for free
- ❌ Ignoring replication lag in read paths
- ❌ CAP theorem as design constraint (it's not)

---

## Trigger Phrases

`DDIA`, `data-intensive`, `replication`, `partitioning`, `consistency model`, `eventual consistency`, `strong consistency`, `CAP`, `storage engine`, `LSM`, `B-tree`, `relational vs NoSQL`, `which database`, `pipeline must survive load and partial failure`

---

## Pairings

- `database-internals-engines` — deeper engine internals
- `qdrant-ops` — vector DB as derived store
- `cloud-native-patterns` — resilience patterns
- `agent-arch-system-design` — full system architecture