---
name: monolith-database-decomposition
description: Applies the database decomposition guidance of Sam Newman's Monolith to Microservices to split a shared data layer safely: identify data ownership boundaries, decompose the schema incrementally, use strangler and data-refactoring patterns, and handle the shared-database hazards (foreign keys, transactions, joins, locking) that block service extraction. Use when the user says 'split the database', 'database per service', 'decompose the schema', 'shared database', 'data ownership', 'strangler pattern for data', 'remove a shared table', 'distributed transaction', 'data migration service-by-service', 'monolith to microservices', or when services are blocked because they share one database. Pairs with: monolith-to-microservices, database-internals-engines, microservices-boundary-design, database-transaction-isolation.
---

# Monolith Database Decomposition

Transfers Sam Newman's database decomposition guidance from Monolith to Microservices to split a shared data layer without breaking the system.

## When to use
- Services share one database and cannot be deployed independently because the schema couples them.
- A team wants to extract a service but the data it needs lives in shared tables.
- The user asks how to move from a shared schema to a database per service.

## Identify data ownership boundaries
- Decide which service owns each piece of data; a datum has exactly one owner, and every other consumer reads it through the owner's interface.
- Draw the boundary by domain (bounded context), not by table name or team habit.
- Where two services genuinely need the same data, choose one owner and give the other a read or copy through an API.
- Data ownership is the precondition for decomposition; without it, splitting the schema just breaks queries.

## Decompose the schema incrementally
- Move one table (or one cluster of owned tables) at a time, never the whole schema at once.
- Prefer database-first or application-first extraction in small steps so each step is verifiable and reversible.
- Duplicate a table into the new service's schema when needed, then switch readers, then delete the original when no reader remains.
- Keep the old schema serving until every consumer has migrated; a cutover that strands a consumer is a failure.

## Strangler and data-refactoring patterns
- Use the strangler pattern for data: build the new ownership path alongside the old one, redirect traffic gradually, and retire the old path when traffic is gone.
- Break the write-path and read-path dependency first; reads can be copied or rerouted before writes move.
- Migrate with an expansion-and-contraction move: add the new field, backfill it, switch readers, then drop the old field.

## Shared-database hazards
- Foreign keys across the boundary couple schemas; replace cross-boundary foreign keys with reference ids validated by the owning service.
- Distributed transactions across services are fragile and slow; prefer compensating actions and idempotent operations.
- Cross-service joins must move into the application or into a read model owned by one service.
- Locking on a shared table serializes independent services; remove shared write locks by moving ownership.
- Do not copy a table into multiple services and write to all copies; one owner, copies read-only.

## Verification discipline
- Enumerate every table, name its owner, and list the consumers still reading through the old path.
- After each incremental move, run the full consumer path and confirm the new owner serves the same data.
- Confirm no foreign key, transaction, or join crosses a service boundary in the final schema.

## Pairs with
monolith-to-microservices, database-internals-engines, microservices-boundary-design, database-transaction-isolation.