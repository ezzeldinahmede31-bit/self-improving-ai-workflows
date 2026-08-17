---
name: concurrent-lock-free-structures
description: Applies Herlihy & Shavit's The Art of Multiprocessor Programming to lock-free and wait-free concurrent structures: atomic primitives (CAS, read-modify-write), lock-free queues/stacks/hash tables, the ABA problem and hazard pointers, linearizability reasoning, and memory-model hazards. Use when the user says 'lock-free', 'wait-free', 'CAS', 'compare-and-swap', 'ABA problem', 'hazard pointers', 'linearizability', 'lock-free queue', 'lock-free stack', 'atomic', 'memory model', 'reordering', 'concurrent data structure', 'why is my lock-free code wrong', or when building a highly concurrent component where locks are the bottleneck. Pairs with: multiprocessor-concurrency, state-machine-persistence, clrs-data-structures-mastery, algorithmic-math-reasoner.
---

# Lock-Free Concurrent Structures

Transfers Herlihy & Shavit's rigorous treatment of lock-free and wait-free programming to production components: reason about linearizability, use the right atomic primitives, and neutralize the classic hazards (ABA, memory reordering, memory reclamation).

## When to use
- Building a concurrent queue/stack/hash table under high contention.
- Replacing a lock with an atomic primitive without losing correctness.
- Debugging a lock-free structure that intermittently corrupts or misses updates.

## The correctness lens: linearizability
- Every operation appears to take effect at a single atomic point inside its call interval.
- Prove each method: find the linearization point (the exact atomic step that commits the effect).
- If no point exists, the structure is not linearizable — that is the bug, not a fluke.

## Primitive selection
- CAS enables optimistic retry loops; choose the descriptor layout so a single CAS commits the visible effect.
- Read-modify-write ops (fetch-and-add, etc.) cover counters; avoid ABA-prone pointer swaps without a scheme.

## The classic hazards and their fixes
- ABA: a value flips A→B→A across the gap from read to CAS; fix with a stamped/versioned descriptor or hazard pointers.
- Memory reordering: relaxations on weak memory models reorder loads/stores; insert the required fences or use sequentially-consistent ops where the contract demands.
- Reclamation: freeing a node while another thread still reads it is the reclamation problem; hazard pointers or epoch-based reclamation keep retired nodes alive.

## Verification discipline
- Stress-test with many threads and randomized operations; assert invariants after every phase.
- Run under a memory model sanitizer (TSan) to catch reordering and race violations.
- Brute-force a small sequential reference and compare operation histories for linearizability.

## Pairs with
multiprocessor-concurrency, state-machine-persistence, clrs-data-structures-mastery, algorithmic-math-reasoner.