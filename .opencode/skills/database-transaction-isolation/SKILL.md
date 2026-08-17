---
name: database-transaction-isolation
description: Applies the transaction and isolation chapter of Alex Petrov's Database Internals: how ACID is really implemented — write-ahead logging, isolation levels and their anomaly guarantees, MVCC as the mechanism behind snapshot isolation, and locking (2PL) as the mechanism behind serializability. Use when the user says 'transaction isolation', 'ACID', 'MVCC', 'snapshot isolation', 'serializable', 'read committed', 'read uncommitted', 'repeatable read', 'write skew', 'dirty read', 'phantom', 'two-phase locking', '2PL', 'write-ahead log', 'deadlock', 'lock granularity', 'why is my transaction not working', or when designing a storage layer that must preserve invariants under concurrency. Pairs with: database-internals-engines, database-replication-consensus, state-machine-persistence, multiprocessor-concurrency.
---

# Database Transaction and Isolation Internals

Transfers the transaction internals of Database Internals (Petrov) to real systems: understand what each isolation level actually guarantees, which anomalies it prevents, and the two mechanisms — MVCC and 2PL — that implement the guarantees.

## When to use
- Choosing an isolation level for a workload and defending the choice.
- Debugging concurrency anomalies (stale reads, write skew, phantoms).
- Designing a storage engine or a long-running transactional job.

## The isolation ladder and its anomalies
- Read uncommitted: may see uncommitted writes (dirty reads).
- Read committed: only committed data; different queries may see different snapshots.
- Repeatable read: a row read twice stays stable; phantoms remain possible in many engines.
- Snapshot isolation: a consistent snapshot per transaction; write skew remains possible.
- Serializable: the strongest level — executions equivalent to some serial order; usually via 2PL or SSI.

## MVCC mechanics
- Each row version carries creation/deletion metadata so a transaction sees one consistent snapshot.
- Garbage collection of old versions is a background concern; runaway version accumulation degrades read performance.

## Locking (2PL) mechanics
- Shared and exclusive locks with the two-phase rule: acquire during the growing phase, release only after the shrinking phase begins.
- Deadlock requires a detection/avoidance strategy; document the victim selection policy.
- Lock granularity trades concurrency for overhead; escalating granularity under contention is a known practice.

## Verification discipline
- Write a concurrency test that provokes the anomaly the chosen level claims to prevent; assert it is actually prevented.
- Instrument the engine (or the ORM) to confirm which mechanism is active.

## Pairs with
database-internals-engines, database-replication-consensus, state-machine-persistence, multiprocessor-concurrency.