---
name: cassandra-definitive-guide
description: Applies Eben Hewitt's Cassandra: The Definitive Guide to designing for the distributed wide-column database: the data model (column families, keyspaces, partitions), Cassandra's distribution and replication, consistency levels and tunable consistency, compaction and tombstone behavior, and the operational model of a peer-to-peer ring. Use when the user says 'Cassandra', 'wide column', 'column family', 'keyspace', 'consistency level', 'quorum', 'compaction', 'tombstone', 'partition key', 'Hewitt cassandra', or when designing a write-heavy distributed store.
---

# Cassandra: The Definitive Guide (Eben Hewitt)

Cassandra trades relational comfort for scale and availability. This skill applies its data model and consistency thinking so queries fit the distribution.

## The data model

- Design tables around the queries: the partition key distributes, the clustering key orders within a partition.
- Denormalize deliberately; Cassandra rewards multiple tables that serve different queries.
- Every row is a partition; hot partitions concentrate load and hurt the ring.

## Distribution and consistency

- The ring replicates data by token ranges; each node owns a share.
- Consistency levels (one, quorum, all) trade latency and durability against each other.
- Tunable consistency is a real knob; read quorum plus write quorum gives strong reads.

## Operational behavior

- Compaction merges SSTables in the background; it is normal and must be budgeted.
- Tombstones mark deletes and must be compacted away; a high tombstone ratio slows reads.
- The write path is append-only and fast; the read path is where the design must be right.

## Operations

- Monitor compaction, gossip health, and per-node load for a healthy ring.
- Add nodes with the right token ranges; the ring rebalances by design.
- Backups and repair keep the data consistent; repair is part of normal operation.

## Pairs with
database-replication-consensus, distributed-systems-concepts-design, data-intensive-application-design, database-reliability-engineering, database-internals-engines
