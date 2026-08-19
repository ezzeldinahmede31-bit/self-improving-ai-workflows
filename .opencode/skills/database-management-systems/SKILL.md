---
name: database-management-systems
description: Applies Ramakrishnan & Gehrke's Database Management Systems to the internals and practice of relational database systems: relational algebra and SQL, disk and file organization, indexing (B-trees, hash indexes), query evaluation and optimization, transactions and concurrency (locking, isolation levels), and crash recovery. Use when the user says 'database management systems', 'B-tree index', 'query evaluation', 'query optimizer', 'concurrency control', 'isolation level', 'log based recovery', 'Ramakrishnan Gehrke', 'database internals', or when understanding or tuning how a database executes.
---

# Database Management Systems (Ramakrishnan & Gehrke)

Ramakrishnan & Gehrke explains how a database actually works from storage up through the query engine. This skill applies that internal knowledge to schema, index, and query decisions.

## Storage and indexing

- Data lives in pages on disk; the access path determines what a query costs.
- B-trees keep ordered data searchable with few disk reads; hash indexes serve point lookups.
- Choose the index for the access pattern: range queries want B-trees, equality lookups want hashing.

## Query evaluation

- Each operator (scan, join, aggregation) has evaluation algorithms with distinct costs.
- Nested-loop, hash join, and sort-merge join trade memory, I/O, and ordering.
- The optimizer picks a plan by estimated cost; update statistics so the estimate is right.

## Transactions and concurrency

- Locking protocols manage concurrent transactions; the isolation level defines the anomalies allowed.
- Read committed versus repeatable read versus serializable differ in what concurrent behavior is permitted.
- Deadlocks are detected and broken; the victim and restart policy is part of the design.

## Recovery

- The log records every change; recovery uses it to redo committed work and undo uncommitted work.
- Checkpoints bound the recovery work after a crash.
- WAL (write-ahead logging) is the rule: the log is durable before the data page is.

## Pairs with
database-system-concepts, database-internals-engines, database-transaction-isolation, sql-in-ten-minutes, database-reliability-engineering
