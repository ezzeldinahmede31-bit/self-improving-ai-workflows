---
name: algorithm-design-kleinberg-tardos
description: Applies Kleinberg & Tardos' Algorithm Design to designing algorithms by stable problem families: greedy algorithms and exchange arguments, divide and conquer with recurrence analysis, dynamic programming over subproblems, network flow and its applications to matching and cuts, NP-completeness reasoning, and approximation algorithms for hard problems. Use when the user says 'design an algorithm', 'greedy', 'exchange argument', 'divide and conquer', 'dynamic programming', 'network flow', 'max flow min cut', 'NP-complete', 'approximation algorithm', 'Kleinberg Tardos', or when a problem needs a designed-and-proven algorithm rather than a guess.
---

# Algorithm Design (Kleinberg & Tardos)

Kleinberg & Tardos organizes algorithm design around recurring problem families so you recognize the pattern, apply the technique, and prove it. This skill encodes that recognition.

## Greedy and exchange arguments

- For a greedy algorithm, prove optimality with an exchange argument: any solution can be transformed toward the greedy choice without losing quality.
- State the ordering rule and the invariant the greedy maintains.
- Test the greedy rule against brute force on small instances before trusting it.

## Divide and conquer

- Solve by splitting the input, solving each part, and combining; write the recurrence and solve it.
- The combination step is where most bugs live; test it in isolation.
- Prefer the smallest combination step that provably works.

## Dynamic programming

- Define the subproblem precisely, write the recurrence over subproblems, and compute in dependency order.
- The optimal substructure must hold: the best solution for the big problem uses optimal solutions for its subproblems.
- Retain the decision table so the optimal solution is reconstructable, not just its value.

## Flow, NP, and approximation

- Network flow solves matching, assignment, and cut problems via max-flow min-cut reasoning.
- When the problem is NP-hard, prove it with a reduction, then choose approximation, exact solvers for small inputs, or heuristics honestly.
- State the approximation factor and prove the bound instead of asserting good behavior.

## Pairs with
clrs-algorithm-mastery, algorithm-design-manual-war-stories, clrs-graph-algorithm-design, algorithmic-math-reasoner, clrs-np-completeness
