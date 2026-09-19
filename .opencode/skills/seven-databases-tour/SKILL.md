---
name: seven-databases-tour
description: "Chooses the right database paradigm: relational, KV, columnar, document, graph. Use when the user says 'which database', 'polyglot persistence', 'seven databases', 'Redis vs Postgres', 'when to use Mongo', 'graph vs relational', 'HBase', 'Riak', or when one database is being forced onto every problem."
---

# Seven Databases Tour

Distilled from Redmond & Wilson *Seven Databases in Seven Weeks*: no single
store fits all — learn each paradigm's data model, strength, and cliff edge,
then assign workloads polyglot-style.

## Purpose

Match each workload to its natural store in one sitting: the model that
makes the queries easy wins; the model that fights them loses regardless of
benchmarks.

## The seven (model → strength → cliff)

1. **PostgreSQL (relational+).** Relations + constraints + extensibility
   (custom types, full-text, JSONB, PostGIS). Strength: correctness-first
   general OLTP with real guarantees. Cliff: horizontal write scale (cite
   sharding pain before promising it).
2. **Redis (data structures server).** Strings/hashes/lists/sets/sorted sets
   in memory with persistence options. Strength: counters, queues, caches,
   leaderboards, rate limits — atomic ops included. Cliff: dataset bigger
   than RAM, complex queries.
3. **Riak (Dynamo-style KV).** Keys + values + vector-clock sibling
   resolution, always writable. Strength: survive partitions with tunable
   R/W quorums. Cliff: you own conflict resolution — siblings must merge in
   APP code.
4. **HBase/Bigtable (wide column).** Sparse maps keyed by (row, column
   family:qualifier, timestamp). Strength: billions of rows, versioned
   cells, sequential scans. Cliff: no joins/transactions; schema design IS
   query design (row-key first).
5. **MongoDB (document).** JSON-ish documents, flexible schema, rich queries
   + aggregation pipeline. Strength: evolving product data, developer
   velocity. Cliff: documents that grow unbounded, multi-document
   consistency needs (use transactions deliberately, not by default).
6. **CouchDB (HTTP + MVCC + sync).** REST-native, master-master replication,
   offline-first sync. Strength: occasionally-connected clients and
   peer sync. Cliff: view-index build times at scale, eventual everything.
7. **Neo4j (property graph).** Nodes + relationships as first-class storage
   (index-free adjacency). Strength: traversals (friends-of-friends,
   fraud rings, recommendations) that JOINs cannot afford. Cliff: sharding
   graphs (relationships cross partitions painfully), global aggregations.

## Selection protocol

- List the queries (not the entities). Score each candidate: query fit,
  consistency need, scale shape, ops maturity on YOUR team. The winner is
  obvious more often than vendors admit.
- Polyglot rule: one primary system of record per bounded context; sync
  explicitly (CDC/outbox), never shared tables across paradigms.

## Verification

Decision record: queries listed, per-candidate scorecard, cliff edges named
with mitigations, sync design for every second store. "We use X for
everything" triggers this skill automatically.

## Pairs with

- `readings-in-database-systems` (why each exists),
  `graph-databases-modeling` (graph depth),
  `redis-in-action`/`mongodb-definitive-guide` (depth per store),
  `domain-driven-design-strategic` (context boundaries for polyglot).
