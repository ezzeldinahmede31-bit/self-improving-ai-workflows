---
name: postgresql-up-and-running
description: Applies Douglas & Obe's PostgreSQL Up and Running to using PostgreSQL productively: installation and configuration, basic and advanced SQL, indexes and query optimization, transactions, functions and procedural language (PL/pgSQL), JSON and full-text search, replication and backup, and the ecosystem of extensions. Use when the user says 'postgres', 'postgresql', 'PL/pgSQL', 'postgres index', 'postgres JSON', 'full text search postgres', 'postgres replication', 'postgres extensions', 'Douglas Obe', or when building or tuning a PostgreSQL-backed service.
---

# PostgreSQL Up and Running (Korry Douglas & Regina Obe)

PostgreSQL Up and Running gets you productive on PostgreSQL with its most powerful features. This skill applies that practical knowledge to schema, query, and operations work.

## Getting productive

- PostgreSQL is configured through postgresql.conf and managed via psql; know where each knob lives.
- Schemas, roles, and privileges form the access model; grant the least privilege each role needs.
- The catalog views describe the system; query them before guessing.

## Schema and queries

- Index types (B-tree, hash, GIN, GiST, BRIN) match different access patterns; choose by the workload.
- Transactions with the standard isolation levels protect concurrent work.
- PostgreSQL's type system is rich: arrays, JSON and JSONB, ranges, and full-text vectors.

## Functions and PL/pgSQL

- PL/pgSQL functions bundle logic in the database; keep them small and tested.
- Triggers fire on events and can enforce rules the application might forget.
- Prefer set-returning functions and proper JOINs over procedural loops.

## Replication and operations

- Streaming replication gives standbys and read scaling; the WAL is the replication stream.
- Backup (base backup plus WAL archive) enables point-in-time recovery; test the restore.
- Extensions (PostGIS, pgvector, and others) extend the core; enable only what you use.

## Pairs with
database-system-concepts, database-internals-engines, database-reliability-engineering, vector-databases-similarity-search, sql-in-ten-minutes
