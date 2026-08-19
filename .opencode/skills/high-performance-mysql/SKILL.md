---
name: high-performance-mysql
description: Applies Schwartz, Zaitsev & Tkachov's High Performance MySQL to schema, indexing, and query optimization for MySQL: server architecture and configuration, indexing strategies for different access patterns, query performance and the optimizer, replication, and backups, with benchmark-driven discipline. Use when the user says 'high performance mysql', 'mysql index', 'slow query', 'explain', 'query optimization mysql', 'replication mysql', 'mysql configuration', 'innodb', 'Schwartz', or when a MySQL database must be made fast and reliable.
---

# High Performance MySQL (Schwartz, Zaitsev, Tkachov)

High Performance MySQL is the authoritative practical guide to making MySQL fast. This skill applies its index and optimizer discipline to real schemas and slow queries.

## Indexing strategy

- Indexes serve access patterns; design them for the queries that matter, not for every possible query.
- Composite indexes have a column order; the leading columns are the most valuable.
- Covering indexes answer a query from the index alone, saving table lookups.

## Query performance

- Profile before optimizing: find the queries that actually cost the most.
- Use EXPLAIN to read the plan; the access type and the rows examined tell the story.
- Rewrite for the optimizer's strengths: sargable predicates, correct join order, minimal returned columns.

## Schema and configuration

- Choose column types that match the data; smaller types fit more rows per page.
- The buffer pool is the memory that matters; size it from the working set.
- Change one configuration variable at a time and measure the effect.

## Replication and operations

- Replication provides read scaling and failover; the replication lag is a real consistency signal.
- Backups must be tested by restore; an untested backup is not a backup.
- Monitor the slow query log, the replication status, and the buffer pool to see trouble early.

## Pairs with
database-internals-engines, database-reliability-engineering, database-transaction-isolation, systems-performance-profiling, sql-in-ten-minutes
