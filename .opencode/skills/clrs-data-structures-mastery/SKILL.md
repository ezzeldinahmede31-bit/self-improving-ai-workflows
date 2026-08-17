---
name: clrs-data-structures-mastery
description: Applies CLRS (Introduction to Algorithms) data-structure rigor to real engineering: choose and reason about the right data structure for the access pattern — binary heaps and priority queues, balanced search trees (red-black, AVL, B-trees), hash tables under adversarial keys, and the disjoint-set union-find structure with path compression and union by rank. Covers amortized analysis of each structure so complexity claims are honest and proven. Use when the user says 'which data structure fits', 'priority queue', 'hash table', 'balanced tree', 'B-tree', 'union-find', 'disjoint set', 'amortized analysis', 'choose a data structure', 'how does a heap work', 'red-black tree', 'hash collision strategy', or when a system needs the correct structure with a proven complexity argument. Pairs with: clrs-algorithm-mastery, algorithm-design-manual-war-stories, algorithmic-math-reasoner, database-internals-engines, multiprocessor-concurrency.
---

# CLRS Data Structures Mastery

Transfers the data-structure discipline of CLRS (Introduction to Algorithms) onto real system design: pick the structure that provably matches the workload, then justify it with a rigorous complexity argument instead of folklore.

## When to use
- Choosing the structure for a hot access pattern (queue, lookup, ranges, connectivity).
- Justifying a choice with proven worst-case and amortized bounds.
- Handling adversarial or worst-case inputs (hash collisions, tree skew).

## The selection method
1. Name the operations that dominate the workload and their required bounds (insert, delete, lookup, min/max, range, union).
2. Enumerate candidate structures and their proven bounds side by side.
3. Eliminate by the dominant constraint, then by constants and cache behavior.
4. State the amortized argument when the structure relies on it (a heap, a splay tree, union-find).

## Core structures and their proofs
- Binary heap: insert and extract-min in O(log n), build-heap in O(n) via the amortized sink argument.
- Balanced search trees: red-black and AVL guarantee O(log n) worst case through rotation invariants; prove the invariant is restored after each insertion.
- Hash tables: expected O(1) with good hashing; analyze the collision-resolution strategy (chaining vs open addressing) under adversarial keys, and choose a universal hash family to avoid worst-case degradation.
- B-trees: O(log n) with high fan-out; the node-minimum-degree invariant drives the split/merge rules.
- Disjoint sets (union-find): near-constant amortized time per operation via the inverse-Ackermann bound; the proof rests on path compression plus union by rank.

## Verification discipline
- Write the complexity argument (best / average / worst / amortized) before coding.
- Prove correctness with a loop invariant for the core operation (the heap property after extract-min).
- Cross-check with a brute-force reference on randomized inputs (algorithmic-math-reasoner gate).

## Pairs with
clrs-algorithm-mastery, algorithm-design-manual-war-stories, algorithmic-math-reasoner, database-internals-engines, multiprocessor-concurrency.