---
name: gray-reuter-tp-processing
description: "Processes transactions at scale the Gray-Reuter way: TP monitors, workflows, and exactly-once effects. Use when the user says 'transaction processing', 'TP monitor', 'exactly-once', 'idempotency', 'sagas', 'long-lived transactions', 'Gray Reuter', or when money or inventory moves across systems."
---

# Gray & Reuter Transaction Processing

Distilled from Gray & Reuter *Transaction Processing: Concepts and
Techniques*: the bible of making distributed actions happen exactly once —
written before the web, valid for every payment/order/booking system since.

## Purpose

Guarantee business actions complete exactly once across failures, restarts,
and retries — the correctness contract behind every system that moves value.

## The canon (still the whole game)

1. **ACID, precisely.** Atomicity (all-or-nothing, via undo/redo logs),
   Consistency (app invariants preserved — the APP's job, not the DB's),
   Isolation (concurrent transactions behave as some serial order),
   Durability (committed = survives crashes, via force-log-at-commit).
   Each letter has a mechanism; name it or the claim is empty.
2. **The log is the database.** Write-ahead logging makes the persistent
   truth; data pages are a cache of it. Commit = log forced. Recovery =
   replay. Any design that treats the log as auxiliary has it backwards.
3. **Exactly-once via idempotency.** At-least-once delivery + idempotent
   receivers (dedupe keys, conditional writes, state-machine transitions
   that tolerate repeats). End-to-end exactly-once is a property of the
   RECEIVER's logic, never of the transport alone.
4. **Long work as sagas.** Transactions that span minutes/hours/services
   cannot hold locks: break into steps with compensating actions, drive with
   a durable orchestrator, make each step idempotent. Forward recovery
   preferred (retry/complete); compensation for the truly undoable.
5. **TP structure.** Requesters, servers, resource managers behind a
   monitor/dispatcher: admission control, load shedding, timeouts with
   teeth. Queues decouple; backpressure protects; duplicate detection sits
   at every boundary.

## Failure drills (run before production)

- Crash after prepare, before commit (2PC recovery path exercised).
- Duplicate delivery storms (idempotency under flood, dedupe store sized).
- Coordinator loss mid-saga (orchestrator state durable, another worker
  resumes). Clock jumps (leases/timeouts re-derived, never trusted blindly).

## Verification

TP review ships with: ACID mechanism per letter, idempotency design per
receiver, saga graph with compensations, drill results for the three
failures, and the duplicate-tolerance proof (same input twice = one
effect, demonstrated). "The queue guarantees it" is rejected as analysis.

## Pairs with

- `idempotency-key-design` (receiver mechanics),
  `saga-compensation-flows` (long transactions),
  `mohan-aries-recovery` (log mechanics),
  `queue-decoupled-workers` (transport structure).
