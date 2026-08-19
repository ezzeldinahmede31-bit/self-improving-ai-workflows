---
name: programming-pearls
description: Applies Jon Bentley's Programming Pearls to practical algorithm and program design: get the problem statement exactly right, use bit-level and space-efficient tricks, choose the right data structure and sort/search, prove correctness with tests, and tune performance with profiling. Use when the user says 'programming pearls', 'Bentley', 'get the problem right', 'bit vector', 'column 1', 'profiling', 'case study', 'binary search again', 'select the right structure', or when a real engineering problem needs the clean, proven solution rather than a clever new one.
---

# Programming Pearls (Jon Bentley)

Programming Pearls collects the lessons that turn good programmers into precise ones: understand the problem, then choose the simplest correct solution. This skill applies its case-study method.

## Understand the problem first

- Re-state the problem in your own words and confirm the input domain and the exact required output before designing.
- Bentley's rule: a precise statement of the problem is often half the solution.
- Challenge the specification: ask what data is really present and what answer is really needed.

## Space and time techniques

- Represent a set of integers with a bit vector when the universe is small; it compresses storage and makes membership a single test.
- Sorting is the workhorse: many problems collapse once the data is ordered.
- Time the program with a profiler before optimizing; guessing the hotspot is usually wrong.

## Correctness by proof and test

- Write the invariants that the loop preserves and check them by hand on small inputs.
- Combine formal reasoning with randomized testing across a wide input domain.
- When a case study fails, revert to the smallest reproducing input and trace it line by line.

## The case-study habit

- Study how a real program was designed and tuned end to end, then reuse that shape on the next problem.
- Record what worked and what misled; the pearl is the lesson, not the code.

## Pairs with
clrs-algorithm-mastery, algorithm-design-manual-war-stories, evidence-over-memory, systems-performance-profiling, code-execution-guided-swemaster
