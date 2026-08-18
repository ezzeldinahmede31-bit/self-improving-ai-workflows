---
name: petrov-lsm-storage-compaction
description: "Applies Alex Petrov's Database Internals treatment of log-structured merge (LSM) storage engines to design and troubleshoot write-heavy data layers: the memtable and write-ahead log, sorted string tables (SSTables), bloom filters, and the size-tiered vs leveled compaction strategies with their read/write/space amplification trade-offs. Use when the user says 'LSM tree', 'compaction', 'memtable', 'SSTable', 'write amplification', 'read amplification', 'space amplification', 'bloom filter', 'leveled compaction', 'size-tiered', 'why does my database write so much', 'RocksDB', 'LevelDB', 'LSM tuning', or when a write-heavy workload needs a storage engine that stays fast under inserts. Pairs with: database-internals-engines, database-transaction-isolation, data-intensive-application-design, readings-in-database-systems, systems-performance-profiling."
---

# LSM Storage and Compaction

The LSM (log-structured merge) design trades a little read cost for very fast
writes. It is the engine behind RocksDB, LevelDB, Cassandra, and many
time-series stores. Understanding compaction is understanding why the engine
behaves the way it does.

## When to use

- A workload is write-heavy (inserts/updates dominate reads).
- Explaining why a database writes far more to disk than the data size.
- Tuning compaction strategy or diagnosing read/write amplification spikes.

## The write path

1. A write appends to the **write-ahead log (WAL)** for durability.
2. The value lands in the **memtable** — an in-memory sorted structure.
3. When the memtable fills, it flushes as an immutable **SSTable** on disk.

SSTables on disk are sorted and immutable; new data only ever appends. This is
what makes writes cheap — there is no in-place update to find.

## The read path and bloom filters

- A read probes the memtable first, then the newest SSTables in order.
- Every SSTable carries a **bloom filter**: a probabilistic structure that says
  "this key is definitely not here" or "possibly here". A negative answer skips
  the file entirely.
- Without bloom filters, a read would check every level in the worst case.

## Compaction strategies

1. **Size-tiered** — merge SSTables of similar size into a larger one. Writes
   are cheap and infrequent merges are big; read cost rises because many
   overlapping files may hold the same key.
2. **Leveled** — the data is split into levels (L0, L1, L2, ...); compaction
   pushes data down one level at a time, keeping files mostly non-overlapping.
   Reads are stable and predictable; writes pay more because a key may be
   rewritten across levels.

## The three amplifications

- **Write amplification** — the number of times the engine writes each byte of
  incoming data to disk. Driven by how frequently and how far data is compacted.
- **Read amplification** — the number of files a read must examine. Grows when many
  overlapping SSTables hold candidate keys.
- **Space amplification** — how much disk the engine uses beyond the logical
  data size. Driven by unreclaimed deleted/updated versions awaiting
  compaction.

Tuning means picking the trade-off your workload prefers: transactional writes
want leveled stability, bulk insert floods often want size-tiered simplicity.

Pairs with: database-internals-engines (the full storage picture),
database-transaction-isolation (MVCC on top of the engine),
data-intensive-application-design, readings-in-database-systems,
systems-performance-profiling (measure the amplification you actually have).
