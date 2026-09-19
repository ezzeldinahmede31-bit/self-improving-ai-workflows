---
name: mohan-aries-recovery
description: "Recovers databases correctly the ARIES way: WAL discipline, LSNs, and three-pass restart. Use when the user says 'ARIES', 'write-ahead logging', 'LSN', 'steal no-force', 'crash recovery', 'checkpoint', 'fuzzy checkpoint', 'Mohan', or when a storage engine must survive power loss."
---

# Mohan ARIES Recovery

Distilled from Mohan et al.'s *ARIES* (IBM Almaden): the recovery method
behind virtually every serious engine — Write-Ahead Logging with
steal/no-force buffers, LSN-chained records, and a restart that always
converges.

## Purpose

Guarantee atomicity and durability across ANY crash point: the engine
restarts into the last committed state, no matter when power died.

## The protocol (three invariants + three passes)

1. **WAL discipline (the law).** A log record describing a change hits
   stable storage BEFORE the changed page does. Log sequence numbers (LSNs)
   chain every record (per-page PageLSN + per-record PrevLSN); each flushed
   page stamps its PageLSN. Violate WAL once and recovery is fiction.
2. **Steal + no-force (performance without compromise).** Steal: dirty pages
   may flush before commit (needs UNDO info in the log). No-force: committed
   pages need NOT flush at commit (needs REDO info + commit record forced).
   Together they decouple buffer management from transaction fate — the
   reason ARIES scales and naive force-everything does not.
3. **Checkpoints (fuzzy, cheap).** Periodic begin/end checkpoint records
   noting active transactions + dirty pages; fuzzy = taken without stopping
   the world. Restart begins at the last complete checkpoint, never at log
   start.
4. **Restart pass 1 — Analysis.** Scan forward from checkpoint: rebuild the
   dirty-page table and active-transaction table. Know what MIGHT need redo
   and who MIGHT need undo.
5. **Restart pass 2 — Redo (history repeating).** Replay ALL logged actions
   from the oldest dirty-page LSN forward, including losers' actions.
   Idempotent by LSN comparison (skip pages already newer). Ends with the
   exact pre-crash physical state.
6. **Restart pass 3 — Undo (to last committed).** Roll back loser
   transactions in reverse LSN order using compensation log records (CLRs)
   that are themselves redoable and never undone twice. Ends with only
   committed effects visible.

## Implementation honesty

- LSNs must be monotonic and comparable across the log AND pages (torn-page
  protection: checksums or full-page writes on first post-checkpoint touch).
- Media recovery (lost disk) replays archived log onto restored backup —
  archive retention sized from RPO, tested by actual restores.
- Nested top actions (index splits) use dummy CLRs so partial structural
  changes never need logical undo — learn this pattern before implementing
  any concurrent index.

## Verification

Recovery review: WAL ordering asserted in code (not documented), kill -9
tests at commit boundaries (before/during/after force), restart-time
measured against log volume, media restore rehearsed. Untested recovery is
a hope with a log file.

## Pairs with

- `gray-reuter-tp-processing` (the log IS the database),
  `redbook-db-architecture` (recovery layer),
  `database-transaction-isolation` (atomicity semantics),
  `petrov-lsm-storage-compaction` (LSM recovery contrasts).
