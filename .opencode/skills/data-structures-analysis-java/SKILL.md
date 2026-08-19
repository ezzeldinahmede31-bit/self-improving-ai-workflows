---
name: data-structures-analysis-java
description: Applies Mark Allen Weiss' Java data structures book to building and analyzing structures in Java: generics and the Collections framework, lists and iterators, stacks and queues, trees (binary, AVL, splay, B-trees), hash tables, priority queues, sorting, and graph algorithms with complexity analysis. Use when the user says 'implement a data structure in Java', 'Java generics', 'Collections framework choice', 'AVL in Java', 'hash map Java', 'priority queue Java', 'Weiss Java', 'Big-Oh Java', 'graph algorithm in Java', or when a Java collection must be selected, built, or proven efficient.
---

# Data Structures and Algorithm Analysis in Java (Mark Allen Weiss)

Weiss' Java edition maps the classic structure-and-analysis treatment onto Java's generics and collections. This skill applies that mapping.

## Generics and the framework

- Use generic types so one structure implementation serves many element types with compile-time safety.
- Choose the framework type by contract: ArrayList versus LinkedList, HashMap versus TreeMap, and the concurrency-safe variants.
- Document the guarantees each choice provides; the wrong default causes subtle performance bugs.

## Building structures

- Implement each structure with a clear invariant and check it after every operation.
- For self-balancing trees, test the rotations with a sequence that forces every rotation shape.
- Keep amortized structures honest: the per-operation worst case can be large even when the average is small.

## Hashing and queues

- Hash tables need a good hashCode plus a collision policy; equals and hashCode must agree exactly.
- Priority queues via binary heap give efficient job scheduling; define the comparator and its tie-breaking rule.
- Bounded structures (bounded queues, ring buffers) need explicit overflow behavior.

## Analysis and verification

- State the complexity of each operation and verify it with a benchmark before trusting it.
- Test with duplicate keys, boundary sizes, and ordering patterns that stress the structure.
- Verify invariants after mutation and run randomized cross-checks against a reference implementation.

## Pairs with
clrs-data-structures-mastery, data-structures-analysis-cpp, clrs-algorithm-mastery, code-execution-guided-swemaster, gof-design-patterns
