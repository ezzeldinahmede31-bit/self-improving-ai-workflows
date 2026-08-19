---
name: data-structures-analysis-cpp
description: Applies Mark Allen Weiss' C++ data structures book to implementing and analyzing fundamental structures correctly: generic containers, lists, stacks, queues, trees (binary, AVL, splay, B-trees), hash tables with collision policies, priority queues, sorting, and graph algorithms — each with a rigorous complexity analysis in C++. Use when the user says 'implement a data structure in C++', 'AVL tree', 'splay tree', 'B-tree', 'hash table C++', 'priority queue', 'binary heap', 'Weiss data structures', 'Big-Oh C++', 'graph algorithm in C++', or when a C++ container must be chosen, implemented, or proven.
---

# Data Structures and Algorithm Analysis in C++ (Mark Allen Weiss)

Weiss pairs each data structure with the C++ implementation and its analysis, so a real program gets both the structure and the proof. This skill applies that pairing.

## Container discipline

- Choose the container by its operation cost: vector for contiguous access, list for splice-heavy work, map and set for ordered lookups.
- Match the iterator and complexity guarantees of the standard containers to the algorithm's requirements.
- Prefer the standard library first; implement a custom structure only when a guarantee is missing.

## Tree structures

- AVL and red-black trees keep lookups logarithmic by bounding the height; implement and test the rotations carefully.
- Splay trees give amortized logarithmic behavior with simpler invariants but a wider per-step spread.
- B-trees match disk block sizes; choose the order from the block, not from memory.

## Hashing and priority queues

- Pick a hash function for the key distribution and a collision policy (separate chaining or open addressing) with a documented load threshold.
- Binary heaps give logarithmic insert and delete-min; the heap invariant is checked after every mutation.
- For a job queue, define the priority order precisely so equal keys resolve deterministically.

## Analysis and testing

- Give the complexity of each operation with the constant when it affects the decision.
- Test each structure with empty, single, duplicate, and adversarial orderings of input.
- Verify structure invariants after every mutating operation during development.

## Pairs with
clrs-data-structures-mastery, clrs-algorithm-mastery, data-structures-analysis-java, systems-performance-profiling, code-execution-guided-swemaster
