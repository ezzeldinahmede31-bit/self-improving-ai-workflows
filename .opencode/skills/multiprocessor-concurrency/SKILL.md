---
name: multiprocessor-concurrency
description: "Applies Herlihy & Shavit's The Art of Multiprocessor Programming to design correct concurrent systems: lock-based and lock-free concurrent objects, atomicity and linearizability reasoning, consensus and the power of primitives (CAS, read-modify-write), memory models and reordering hazards, and safe concurrent data structure construction. Use when the user says 'thread safety', 'concurrent data structure', 'race condition', 'deadlock', 'linearizability', 'lock-free', 'lock-free queue', 'CAS', 'atomic', 'memory model', 'multithreaded', 'parallel program', 'why does my code deadlock', or when designing anything that multiple threads or processes touch simultaneously. Pairs with: state-machine-persistence, zero-trust-modular-decomposer, agent-arch-system-design, algorithmic-math-reasoner."
---

# Multiprocessor Programming — Concurrency Correctness

Herlihy & Shavit teach concurrency the rigorous way: first define what correct means
(linearizability — every operation appears to take effect at one atomic point in its
interval), then choose the mechanism, then prove it under the memory model. Most
concurrency bugs are design bugs, not code typos.

## When to use

- Designing or reviewing any shared state touched by multiple threads/processes.
- Investigating race conditions, deadlocks, or strange reordering under load.
- Choosing the synchronization mechanism: locks, atomics, lock-free structures,
  or message passing.

## Step 1 — Define correctness before writing code
- State the linearization point for every operation (the exact step where the
  operation takes effect). If you cannot name it, the design is not ready.
- Enumerate invariants the shared structure must preserve and how each operation
  preserves them under interleaving.

## Step 2 — Choose the mechanism by power and cost
- Plain atomic reads/writes for single-word state where ordering does not matter.
- Locking (mutex/RW-lock) when a critical section mutates multiple fields — keep
  the section minimal and consistent to avoid deadlock (always acquire locks in a
  global order; never hold one lock while waiting on another).
- Lock-free structures (compare-and-swap loops, per-thread queues) when lock
  contention is the measured bottleneck — but only after you can reason about the
  retry loop and its linearization point.
- Message passing / actors when ownership can be isolated to one thread — the
  cheapest correct option for many designs.

## Step 3 — Memory-model hygiene
- Shared writes and reads must be synchronized (mutex, volatile/atomic,
  acquire/release) — unsynchronized access is a data race, a defect even if it
  "seems to work" on the test machine.
- Be aware of reordering: the compiler and CPU may reorder independent operations;
  only the synchronization constructs order them. Name the memory ordering you rely
  on (sequentially consistent, acquire/release, relaxed) per variable.

## Step 4 — Verification
- Run the concurrency stress tests with different thread counts and randomized
  interleavings; a race detector (TSan-style) must be clean.
- Check the failure modes under contention: does it degrade (lock) or spin (CAS
  loop)? Bound the retry.

## Pairs with
- `state-machine-persistence` — durable concurrent state for long-running systems.
- `zero-trust-modular-decomposer` — isolate shared state behind narrow modules.
- `agent-arch-system-design` — concurrency in the architecture trade-off matrix.
- `algorithmic-math-reasoner` — proving invariants and linearization points.