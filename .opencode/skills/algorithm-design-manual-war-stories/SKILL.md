---
name: algorithm-design-manual-war-stories
description: "Applies Steven Skiena's Algorithm Design Manual 'war manual' to real-world problems: classify the problem type first, consult the problem catalog for the proven approach (sorting, hashing, search, strings, graph, combinatorial search), then lift a War Story lesson before optimizing. Stops the failure mode of jumping straight to a clever algorithm when the catalog says use the boring one. Use when the user says 'which algorithm fits this problem', 'war story', 'problem catalog', 'this feels like a textbook problem', 'what is the right approach', 'brute force then optimize', or hands a real engineering problem that needs the practical (not theoretical) algorithm choice. Pairs with: clrs-algorithm-mastery, algorithm-design, algorithmic-math-reasoner, code-execution-guided-swemaster."
---

# Algorithm Design Manual — War Stories

Skiena's book is the practical counterpart to CLRS: it teaches you to identify the
problem type, then reach into a catalog of known solutions instead of inventing one.
Its War Stories are the collected mistakes of real programmers — each encodes a
lesson about a technique that looked right and was wrong.

## When to use

- Any real-world (not purely academic) problem that reduces to an algorithm choice.
- "This feels like a known problem but I cannot name it" — the catalog is the cure.
- Code review where a clever algorithm replaced a proven simple one and failed.

## The War Manual method

### Step 1 — Name the problem class (before any code)
Ask in order:
- Is it a search problem (find a thing satisfying constraints)? → backtracking /
  combinatorial search with pruning; if the search space is huge, is it NP-hard?
- Is it a shortest-path / graph problem? → which variant (weights, negative edges,
  all-pairs, single source)?
- Is it a string problem? → exact/approximate matching, substring, longest common
  subsequence.
- Is it a geometry problem? → convex hull, closest pair, range queries.
- Is it a sorting/searching problem in disguise? → most problems are: sort first,
  then the rest is easy.
- Is it a counting / optimization over subsets? → DP if optimal substructure, else
  meet-in-the-middle or approximation.

### Step 2 — Consult the catalog, take the proven technique
For each class Skiena gives the canonical solution and its complexity. The move:
- Take the catalog entry (e.g. "Longest Increasing Subsequence → patience sorting /
  DP", "edit distance → DP O(nm)", "minimum spanning tree → Kruskal or Prim") and
  adapt, never re-derive from zero.
- If two candidate techniques exist, pick the one with the simpler proof of
  correctness — a boring correct solution beats a clever one you cannot verify.

### Step 3 — War Story hygiene
Apply the recurring lessons:
- The wrong model dominates the failure: make the model explicit and attack it first.
- Optimization that fights the algorithm's nature (e.g. bit-packing an already linear
  pass) is wasted effort — measure before micro-tuning.
- A simpler data structure that supports the operation at equal complexity wins.
- Do not optimize what is never the bottleneck; profile or reason about the hot path
  first.

### Step 4 — Brute force first, optimize with evidence
Implement the straightforward version, verify it, then optimize only the measured
hot path (see `code-execution-guided-swemaster` for the execution-evidence loop).
Complexity claims after optimization must be re-derived, not inherited.

## Verification
- State the problem class you chose and the catalog solution you lifted, in one line.
- Prove the chosen complexity and cross-check with a brute-force run on small inputs.
- If the answer is a value, grade it mechanically (see `self-benchmark-runner`).

## Pairs with
- `clrs-algorithm-mastery` — proofs + asymptotic analysis for the chosen technique.
- `algorithm-design` — formal pseudocode and UML for documentation.
- `algorithmic-math-reasoner` — invariant and complexity verification.
- `code-execution-guided-swemaster` — measure the real hot path before optimizing.