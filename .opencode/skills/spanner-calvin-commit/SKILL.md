---
name: spanner-calvin-commit
description: "Builds globally-consistent distributed transactions: TrueTime ordering and deterministic scheduling. Use when the user says 'Spanner', 'TrueTime', 'external consistency', 'two-phase commit', 'distributed transactions', 'Calvin', 'deterministic database', 'global snapshot reads', or when writes span machines without losing sanity."
---

# Spanner & Calvin Distributed Commit

Distilled from Google's *Spanner* (Corbett et al., OSDI'12) and *Calvin*
(Thomson et al., SIGMOD'12): two answers to one question — how do
transactions commit across the planet and still look like one machine?

## Purpose

Choose and operate the right global-transaction machinery: order-then-execute
(Spanner) or sequence-then-replay (Calvin), with eyes open about latency and
availability costs.

## Spanner: order with TrueTime, commit with 2PC+Paxos

1. **TrueTime = time with error bars.** TT.now() returns [earliest, latest];
   uncertainty epsilon (~ms, from GPS/atomic clocks) is a FIRST-CLASS input
   to every protocol decision. No synchronized clocks are assumed — only
   bounded uncertainty.
2. **External consistency via commit-wait.** A transaction commits at
   timestamp s only after TT.now() has certainly passed s (wait out epsilon).
   Result: if T2 starts after T1 commits (in absolute time), T2's timestamp
   is larger. Causality becomes timestamp order — the strongest guarantee a
   database can offer.
3. **Read-write: 2PC over Paxos groups.** Shards replicate via Paxos; the
   coordinator runs 2PC across participant groups at the chosen timestamp.
   Snapshot reads at any timestamp are lock-free (MVCC versions retained) —
   reads never block writes.
4. **Cost ledger.** Commit-wait adds ~2×epsilon latency to every write;
   cross-region 2PC pays WAN RTTs; clock masters are new failure domains.
   Single-region deployments should say so and skip the global machinery.

## Calvin: deterministic replay instead of coordination

1. **Sequence first, execute later.** A sequencer orders ALL transaction
   inputs into one global log (the only coordination point); replicas then
   execute deterministically with the same result — no 2PC during execution.
2. **Determinism is the price.** Transaction logic must be deterministic
   given the input log (no wall-clock reads, no random choices inside).
   Reconnaissance runs pre-read data to keep the deterministic phase fast.
3. **Payoff.** No distributed deadlock (locks acquired in log order), no
   2PC latency on the hot path, active-active replicas for free. Cost: the
   sequencer's throughput caps the system; cross-partition transactions need
   care.

## Decision rule

- Need external consistency + SQL + planet scale, can pay write latency:
  Spanner-style. Need max throughput with known workload, can enforce
  determinism: Calvin-style. Else: single-leader + async replicas and stop
  pretending.

## Verification

Design ships with: consistency guarantee named (external/serializable/snapshot),
worst-case commit path in RTTs, clock-failure behavior, and a Jepsen-style
partition test (kill the WAN, then show the invariant holding).

## Pairs with

- `database-transaction-isolation` (isolation semantics),
  `database-replication-consensus` (Paxos/Raft substrate),
  `ddia-replication-partitioning` (replication trade-offs),
  `distributed-control-systems-design` (coordination patterns).
