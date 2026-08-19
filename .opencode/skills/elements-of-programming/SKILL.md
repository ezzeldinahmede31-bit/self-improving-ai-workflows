---
name: elements-of-programming
description: Applies Stepanov & McJones' Elements of Programming to write programs as mathematics: programs are expressions of regular, well-defined algorithms over regular types; concepts give an algorithm its precise preconditions; and generic programming decomposes an algorithm into a minimal set of requirements so one implementation serves many types. Use when the user says 'generic programming', 'concepts and axioms', 'regular types', 'iterator requirements', 'program as math', 'preconditions and postconditions', 'Stepanov', 'reusable algorithm', 'type requirements', or when a piece of code should be written once and proven, not patched for every caller.
---

# Elements of Programming (Stepanov & McJones)

Elements of Programming treats programming as a mathematical discipline: an algorithm is correct because it meets the axioms of its concepts. This skill applies that discipline to everyday code.

## Programs as mathematics

- State the algorithm's requirements and guarantees in the language of types and values before writing a line.
- Every operation an algorithm uses must be justified by the concept it requires; do not rely on incidental type features.
- A well-factored algorithm decomposes into smaller algorithms, each with its own concept requirements.

## Regular types and concepts

- A regular type is a type whose objects can be copied, assigned, compared for equality, and used as values.
- Concepts name the requirements an algorithm needs: readable, writable, iterable, associative, and their combinations.
- Write the concept explicitly so a type that satisfies it can be substituted without code changes.

## Generic algorithms and iterators

- Decompose algorithms around iterators: what an algorithm needs from a traversal is a small set of operations.
- Use the minimal iterator category that satisfies the algorithm; requiring more excludes valid types.
- Compose generic algorithms (transform, accumulate, find) instead of hand-writing loops.

## Correctness by construction

- Each generic algorithm comes with a loop invariant and a termination argument; document both.
- Test with the smallest and simplest types that satisfy the concept, then with the real ones.
- Verify the axioms hold for each new type before substituting it.

## Pairs with
sicp-abstraction-and-interpretation, clrs-algorithm-mastery, ctm-concepts-techniques-models, functional-programming-scala, zero-trust-modular-decomposer
