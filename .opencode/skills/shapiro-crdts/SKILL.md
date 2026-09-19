---
name: shapiro-crdts
description: "Shares mutable state without coordination: convergent replicated data types. Use when the user says 'CRDT', 'eventual consistency', 'conflict-free', 'collaborative editing', 'offline-first', 'mergeable state', 'LWW', 'G-Counter', 'Shapiro', or when replicas must converge with no leader and no locks."
---

# Shapiro CRDTs

Distilled from Shapiro et al.'s *Comprehensive Study of CRDTs*: replicas
that merge with a join-semilattice (or a commutative effect set) converge by
construction — coordination is a choice, not a requirement.

## Purpose

Design shared state that stays correct under partitions, offline edits, and
concurrent writers — with convergence proved, not hoped for.

## The two families (pick one per datatype)

1. **State-based (CvRDT).** Replicas hold full state; merge = least upper
   bound (join) of a semilattice: idempotent, commutative, associative.
   Delivery can duplicate/reorder — merge absorbs it. Cost: state size
   shipped on sync (delta-state variants send only recent changes).
2. **Operation-based (CmRDT).** Replicas apply commutative effects;
   requires exactly-once causal delivery (vector clocks or a reliable
   broadcast) — smaller messages, stricter transport. Same convergence
   guarantee when the delivery contract holds.

## The catalog (use off-the-shelf types, don't invent)

- **Counters:** G-Counter (grow-only, per-replica slots, merge takes max);
  PN-Counter (two G-Counters, inc/dec). Never a single integer with last-
  writer-wins — increments get lost.
- **Sets:** G-Set (grow-only); 2P-Set (add-wins-once via tombstones, no
  re-add); OR-Set / Observed-Remove (add-wins with unique tags — the default
  for collaborative collections).
- **Registers:** LWW-Register (timestamp + tiebreak; simple, lossy by
  design — use only when loss is acceptable); MV-Register (keep concurrent
  values, let the app resolve).
- **Text/sequences:** RGA / Yjs-style (insert with stable positions +
  tombstones) — collaborative editing solved, use a library.
- **Maps:** recursive merge of CRDT values per key (removed keys need
  tombstone policy stated).

## Design rules

- Convergence requires the merge to be associative+commutative+idempotent —
  prove the three properties for any custom type (three short proofs, no
  hand-waving).
- Causality: concurrent vs causally-ordered updates need different handling;
  attach version vectors where order matters.
- Tombstone/GC policy is part of the design (unbounded growth is the #1
  production CRDT failure); state it with the type.

## Verification

Each shared datatype ships with: family chosen + why, merge operation with
the three properties argued, tombstone/GC policy, and a partition test
(split brain, divergent edits, heal, assert convergence + intent preserved).

## Pairs with

- `distributed-systems-concepts-design` (consistency models),
  `swim-gossip-membership` (dissemination layer),
  `cross-platform-data-sync-conflict-resolution` (sync practice),
  `state-machine-persistence` (durable replicas).
