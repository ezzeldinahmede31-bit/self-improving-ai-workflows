---
name: distributed-systems-field-manual
description: "Practical distributed-systems survival rules: timeouts, retries, clocks, quorums. Use when the user says 'retry storm', 'clock skew', 'split brain', 'quorum', 'idempotency', 'distributed lock', 'two generals', or needs field rules that keep multi-node systems alive."
---

# Distributed Systems Field Manual

Distilled from Vitillo *Understanding Distributed Systems*, Hellerstein
*Distributed Systems for Fun and Profit*, Burns *Designing Distributed
Systems*, *Distributed Systems: Principles and Paradigms*, plus the
practical core of Coulouris/van Steen. Theory compressed into rules you
apply before lunch.

## The field rules (violations page at 3am)

1. **Timeouts everywhere, budgets end-to-end.** No unbounded call. Every
   hop gets a deadline; the edge owns the total budget and propagates
   it. A missing timeout is a distributed deadlock waiting for load.
2. **Retries with backoff + jitter + budget.** Same retry, same time =
   thundering herd. Exponential backoff, full jitter, per-dependency
   retry budgets, idempotency keys on every mutating retry
   (`idempotency-key-design`).
3. **Clocks lie.** Never order events by wall clock across nodes;
   use logical clocks / versions / fencing tokens. Lease + fence beats   lock-without-fence (split-brain writes lose to the fenced loser).
4. **Quorums for truth.** R + W > N for overlap; leader for writes,
   followers for reads when lag is tolerable. Name the consistency per
   operation (`database-transaction-isolation`).
5. **Failure detection is a guess.** Phi-accrual style suspicion, not
   binary alive/dead; flap dampening before failover. Most 'network
   partitions' are slow processes — fail over on suspicion, reconcile
   on return.
6. **Small writes, versioned reads.** Compare-and-swap on versions,
   CRDTs where merge beats coordination, outbox for cross-system
   atomicity (saga/outbox in `scalability-distributed-systems`).
7. **Backpressure over buffering.** Bounded queues + load shedding at
   the edge. An unbounded queue turns a slowdown into an outage with
   interest.

## Verification

Multi-node design ships with: deadline budget per hop, retry policy +
idempotency, clock/fencing story, quorum math (R/W/N), failure
suspicion + dampening, bounded queues with shed policy. Each rule
violated gets a written acceptance, not silence.

## Pairs with

- `ddia-replication-partitioning` (mechanics),
  `database-transaction-isolation` (consistency),
  `idempotency-key-design` (safe retries),
  `scalability-distributed-systems` (saga/outbox),
  `system-type-distributed` (pattern catalog),
  `chaos-resilience-practice` (prove it).
