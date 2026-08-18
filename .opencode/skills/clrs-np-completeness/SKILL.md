---
name: clrs-np-completeness
description: "Applies the NP-completeness chapter of CLRS (Introduction to Algorithms) to recognize hard problems and argue hardness rigorously: P versus NP, polynomial-time many-to-one reductions, the Cook-Levin result, and the classic reduction ladder (SAT, 3-CNF-SAT, clique, vertex cover, Hamiltonian cycle, TSP, subset sum) — plus the practical stance: prove hardness, then use exact solvers, approximation, or heuristics instead of pretending polynomial algorithms exist. Use when the user says 'is this NP-complete', 'prove NP-hardness', 'reduction', 'polynomial vs exponential', 'can this be solved efficiently', '3-SAT', 'clique problem', 'TSP', 'subset sum', 'intractable problem', or when a problem looks exponential and needs an honest classification. Pairs with: clrs-algorithm-mastery, algorithmic-math-reasoner, algorithm-design-manual-war-stories, formal-math-logic-verification-engine."
---

# NP-Completeness (CLRS)

The chapter that tells you when to stop looking for a fast exact algorithm and
start proving why none exists.

## When to use

- Classifying a new problem as polynomial or intractable.
- Proving NP-hardness via reductions.
- Choosing the honest approach: exact solvers, approximation, or heuristics.

## P and NP

- P = problems solvable in polynomial time. NP = problems whose solutions can be
  verified in polynomial time.
- Whether P equals NP is open; the working assumption is they differ, and the
  NP-complete class is the boundary case.

## Hardness and completeness

- A problem is NP-hard if every NP problem reduces to it. It is NP-complete if
  it is also in NP itself.
- Reductions are many-to-one polynomial mappings: show your problem is no easier
  than a known hard problem by encoding that known problem into yours.

## The classic ladder

- SAT is NP-complete (Cook-Levin). From SAT reduce to 3-CNF-SAT, then to clique,
  vertex cover, Hamiltonian cycle, traveling-salesman, and subset sum.
- To prove a new problem hard, reduce FROM a known hard problem TO your problem —
  the direction that encodes the known one as a special case of yours.

## Practical stance

- Once hardness is proven, stop promising a fast exact algorithm.
- Exact solutions still work for small instances (branch and bound, SAT solvers,
  dynamic programming on bounded parameters).
- Approximation algorithms and heuristics are the honest tool for large inputs;
  label the guarantees they carry.

Pairs with: clrs-algorithm-mastery, formal-math-logic-verification-engine
(encodings), algorithm-design-manual-war-stories, algorithmic-math-reasoner.
