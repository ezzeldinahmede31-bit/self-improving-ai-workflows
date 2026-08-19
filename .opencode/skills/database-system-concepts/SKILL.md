---
name: database-system-concepts
description: Applies Silberschatz, Korth & Sudarshan's Database System Concepts (the standard database textbook) to relational database design and use: the relational model and relational algebra, SQL, database design (ER modeling, normalization, functional dependencies), transactions and concurrency control, recovery, and query processing and optimization. Use when the user says 'database system concepts', 'relational model', 'normalization', 'functional dependency', 'ER diagram', 'transaction', 'concurrency control', 'two phase locking', 'query optimization', 'Silberschatz', or when a relational design or transaction question needs textbook grounding.
---

# Database System Concepts (Silberschatz, Korth, Sudarshan)

This is the canonical reference on how relational databases work. This skill applies its model, algebra, and transaction theory to real schema and query work.

## The relational model

- The relational model is tables of rows and columns with well-defined operations; the algebra is the query core.
- Keys (candidate, primary, foreign) express identity and reference; design them before data.
- Every query is an algebra expression; translating SQL to algebra explains what it does.

## Database design

- ER modeling captures entities and relationships; translate it to a relational schema faithfully.
- Normalization removes redundancy and update anomalies; each normal form removes a specific problem.
- Functional dependencies are the reasoning tool: derive them, then decompose to the form the design needs.

## Transactions and concurrency

- A transaction is atomic, consistent, isolated, durable; isolation levels trade consistency for concurrency.
- Two-phase locking and its variants manage concurrent access; deadlock detection and prevention are part of the design.
- Recovery (undo, redo, checkpoints) restores consistency after failure; the log is the record of truth.

## Query processing

- The optimizer chooses the plan from cost estimates; statistics drive the estimate.
- Indexes and join orders dominate query performance; the access path is the lever.
- Measure the plan, not the guess; the database explains how a query runs.

## Pairs with
database-internals-engines, fundamentals-database-systems, database-management-systems, sql-in-ten-minutes, database-reliability-engineering
