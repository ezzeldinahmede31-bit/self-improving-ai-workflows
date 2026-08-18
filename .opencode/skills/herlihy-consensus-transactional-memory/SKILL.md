---
name: herlihy-consensus-transactional-memory
description: "Applies the consensus and transaction chapters of Herlihy & Shavit's The Art of Multiprocessor Programming: the consensus hierarchy that ranks synchronization primitives by power, why compare-and-swap sits above registers, the universal construction that builds any concurrent object from consensus, and transactional memory (hardware and software) with its progress guarantees, validation, and conflicts. Use when the user says 'consensus number', 'universal construction', 'transactional memory', 'STM', 'HTM', 'compare-and-swap power', 'synchronization primitive hierarchy', 'lock-free and wait-free', 'progress guarantees', 'transactional conflict', 'obstruction-free', 'Herlihy Shavit', or when choosing a primitive or a memory transaction model for a concurrent component. Pairs with: multiprocessor-concurrency, concurrent-lock-free-structures, database-transaction-isolation, algorithmic-math-reasoner, state-machine-persistence."
---

# Consensus and Transactional Memory

Two ideas carry the deep theory of concurrent programming: how powerful a
synchronization primitive really is (consensus), and how to make concurrent
state changes look atomic (transactions).

## When to use

- Choosing which primitive (CAS, register, mutex, or a transactional approach)
  a concurrent component should be built on.
- Proving or explaining why some lock-free constructions exist and others
  cannot.
- Designing a memory transaction system with clear conflict and progress rules.

## The consensus hierarchy

- **Consensus** is the problem of making all threads agree on one value even
  when they disagree about what they observed.
- Herlihy ranked primitives by the largest number of threads they can solve
  consensus for (the **consensus number**):
  - Registers and basic reads/writes: consensus number 1 — they cannot solve
    agreement on their own.
  - Compare-and-swap and test-and-set: consensus number unbounded — a single
    CAS primitive can coordinate any number of threads.
- The practical rule: the power of a primitive is the power of the agreement it
  can reach. A register-only construction cannot be wait-free where more than
  one thread must agree.

## The universal construction

- Any concurrent object can be built from consensus: wrap each method call in a
  proposed update, agree on the next update order via consensus, and apply
  updates in that order.
- This is why lock-free queues, stacks, and hash tables exist for CAS but not
  for plain registers.

## Transactional memory

- **Software transactional memory (STM)**: a transaction reads a snapshot,
  computes, validates, and commits; on conflict the transaction retries.
- **Hardware transactional memory (HTM)**: the CPU detects conflicts and
  aborts transactions in hardware — fast but bounded in footprint.
- Rules that keep STM correct:
  - Validation before commit (the read set must still match).
  - Conflict detection for overlapping write sets.
  - Bounded retries: a transaction that keeps aborting must fall back to a
    lock instead of looping forever.
- Progress guarantees, strongest to weakest: **wait-free** (every thread
  finishes in bounded steps), **lock-free** (some thread always progresses),
  **obstruction-free** (a thread progresses if it runs alone).

Pairs with: multiprocessor-concurrency (the surrounding concurrency model),
concurrent-lock-free-structures (CAS-based objects), database-transaction-
isolation (the same ideas in databases), algorithmic-math-reasoner,
state-machine-persistence.
