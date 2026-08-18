---
name: ddia-replication-partitioning
description: "Applies the replication and partitioning chapters of Designing Data-Intensive Applications (Kleppmann) to scale a data system: single-leader, multi-leader, and leaderless replication with their consistency trade-offs and replication lag; partitioning strategies (key range vs key hash), secondary-index partitioning, and rebalancing; and how replication and partitioning compose. Use when the user says 'replicate my database', 'leader election', 'multi-leader', 'leaderless', 'eventual consistency', 'replication lag', 'partition a database', 'sharding', 'rebalance partitions', 'secondary index', 'Kleppmann replication', or when a data store must scale reads, writes, or data volume. Pairs with: database-replication-consensus, database-internals-engines, distributed-systems-concepts-design, data-intensive-application-design, cloud-native-patterns."
---

# Replication and Partitioning (DDIA)

Scaling a data system is two separate moves: replicate for durability and read
capacity, partition for data volume and write capacity.

## When to use

- Choosing a replication topology and its consistency story.
- Sharding a data store that outgrew one node.
- Reasoning about replica lag and stale reads.

## Replication

- **Single-leader**: one node takes writes; followers replicate asynchronously or
  synchronously. Simplest consistency, but the leader is a bottleneck and a
  single point of failure.
- **Multi-leader**: several nodes accept writes (per datacenter, per office);
  write conflicts must be resolved — last-writer-wins, merging, or explicit
  conflict handling. Never free.
- **Leaderless**: clients write to several replicas, read from several, and use
  versioning to reconcile (quorum reads/writes).

## Replication lag

- Asynchronous followers lag the leader; a client may read its own write from a
  stale follower, or observe anomalies in ordering across replicas.
- Mitigations: read-your-writes (route reads for a user to the leader),
  monotonic reads, consistent-prefix reads — each costs something.

## Partitioning

- Partition by key range: keeps ranges together and enables range scans, but hot
  spots form at the edges.
- Partition by hash of the key: spreads writes uniformly, but destroys range
  adjacency. A hybrid: hash then range within a bucket.
- Secondary indexes across partitions are either local (scatter-gather queries)
  or global (write-time fan-out).

## Rebalancing

- Moving partitions as nodes join or leave must avoid excessive data movement.
- Hash partitioning with many small buckets rebalances cheaply; key-range
  partitioning with fixed boundaries does not.

Pairs with: database-replication-consensus (Raft/Paxos mechanics),
database-internals-engines, distributed-systems-concepts-design,
cloud-native-patterns, data-intensive-application-design.
