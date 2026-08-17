---
name: clrs-algorithm-mastery
description: "Enforces the CLRS (Introduction to Algorithms) method on hard algorithmic problems: rigorous asymptotic complexity analysis (Big-O/Theta/Omega) for time and space, proof of correctness via loop invariants, induction and exchange arguments, and the canonical design toolkit (divide-and-conquer, dynamic programming, greedy, amortized analysis, randomized algorithms) matched to the right data structure. Use when the user says 'analyse complexity', 'prove this algorithm correct', 'which data structure fits', 'dynamic programming', 'greedy or DP', 'divide and conquer', 'amortized analysis', 'design an algorithm', 'recurrence', or hands a competitive-programming or interview-style algorithm task that must come with a proof and a complexity argument. Pairs with: algorithmic-math-reasoner, algorithm-design, algorithm-design-manual-war-stories, off-by-one-boundary-guard, self-benchmark-runner."
---

# CLRS Algorithm Mastery

The CLRS bible distills algorithmics into three inseparable obligations: the
right design technique, a correctness proof, and an exact complexity statement.
This skill forces all three before any algorithm is accepted as done.

## When to use

- Any algorithm design or analysis task (competitive programming, interviews,
  hard DP/greedy/graph/number-theory problems).
- Any time a solution must ship with a proof AND a Big-O argument.
- Code review of an existing algorithm where complexity or correctness is in doubt.

## The three obligations (mandatory before "done")

### 1. Design technique — pick from the CLRS toolbox
Walk the problem against these families and commit to one (plus a fallback):
- Divide-and-conquer — recurrences via Master theorem / recursion tree / substitution.
- Dynamic programming — optimal substructure + overlapping subproblems; order by
  state (top-down memoization or bottom-up table); define the DP state, transition,
  base case, and answer before writing loops.
- Greedy — only after proving the exchange argument or matroid-like property;
  otherwise DP is the safe choice.
- Amortized analysis — aggregate, accounting, or potential method for sequences of
  operations where the worst single step is misleading.
- Randomized algorithms — Las Vegas (always correct, random time) vs Monte Carlo
  (probabilistically correct); bound the failure probability.
- Graph algorithms — the right traversal (BFS for unweighted shortest paths, DFS
  for connectivity/cycles/topological order), shortest paths, MST, max-flow via the
  reductions that fit the problem.

Match the data structure to the operation mix (hash for lookup, balanced tree for
ordered ops, heap for max/min extraction, union-find for incremental connectivity,
Fenwick/segment tree for range queries).

### 2. Correctness proof
- Loop invariants: state the invariant, prove initialization, maintenance, termination
  (and that termination plus the invariant implies the answer).
- Induction for recursive/DP correctness; the base case and the step must be explicit.
- Exchange argument for greedy: show an optimal solution can be transformed into the
  greedy choice without losing optimality.
- Reductions: if you reduce problem A to B, prove both directions (A solvable iff B
  solvable) and carry the complexity through.

### 3. Complexity statement
- Give the exact asymptotic class for time AND space, with the worst case stated
  (best/expected only when justified).
- Name the recurrence and the method used to solve it (Master theorem conditions must
  be checked, not assumed — when the Master theorem does not apply, use recursion-tree
  or substitution and say which).
- State what dominates: e.g. O(n log n) time, O(n) space, from the merge step + stack.

## Verification
- Cross-validate against brute force on small inputs (see `algorithmic-math-reasoner`
  gate 4) — the naive enumeration is the ground truth for n ≤ 10.
- When the answer is a numeric value that must match a key, grade it mechanically
  (see `self-benchmark-runner`).
- Check boundary behavior of the algorithm (empty input, single element, already
  sorted, adversarial order) using `off-by-one-boundary-guard` mindset on the ranges.
- Re-state the complexity in one line at the end; if two analyses disagree, resolve
  before shipping.

## Pairs with
- `algorithmic-math-reasoner` — brute-force cross-validation + invariant proofs.
- `algorithm-design` — LaTeX pseudocode + UML for formal writeups.
- `algorithm-design-manual-war-stories` — the practical "which technique fits THIS
  real problem" catalog.
- `off-by-one-boundary-guard` — when the answer is a tally or a range.
- `self-benchmark-runner` — measured head-to-head runs on public problem sets.