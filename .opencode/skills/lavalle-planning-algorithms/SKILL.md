---
name: lavalle-planning-algorithms
description: "Plans motion and decisions: configuration space, sampling planners, and search. Use when the user says 'motion planning', 'RRT', 'PRM', 'A* search', 'configuration space obstacles', 'LaValle', 'path planning', or when anything must get from start to goal without collision."
---

# LaValle Planning Algorithms

Distilled from Steven LaValle *Planning Algorithms*: everything that moves
or decides lives in a state space with obstacles — plan in that space with
the right algorithm for its structure (combinatorial, sampling, or decision-
theoretic).

## Purpose

Get agents/robots/characters from start to goal safely and efficiently:
model the space, pick the planner, prove the properties you need.

## The toolkit (space structure picks the method)

1. **Model the space.** Configuration/state space + obstacle region +
   free space; explicit (grids, roadmaps) vs implicit (collision checker as
   oracle). Dimensionality decides everything: low-D admits exact methods,
   high-D demands sampling.
2. **Combinatorial planners (low-D, exact).** Visibility graphs, cell
   decomposition, exact roadmaps — complete (find a path iff one exists).
   Use when DOF ≤ 4 and guarantees matter more than generality.
3. **Sampling planners (high-D workhorse).** PRM (learn the roadmap once,
   query many times — multi-query factories), RRT (grow toward the goal,
   single-query friendly), RRT* / informed variants (asymptotic optimality).
   Properties to state: probabilistic completeness (yes), optimality
   (only starred variants, asymptotically). Narrow passages need biased
   sampling — uniform sampling fails where it matters most.
4. **Grid search done right.** A* with admissible heuristics (never
   overestimate — admissibility IS optimality's license), D*/anytime variants
   for dynamic worlds, state lattices for kinodynamic constraints. Heuristic
   quality dominates runtime; design it from the problem, not from Euclidean
   distance by default.
5. **Feedback and information.** Sensor-based planning (bug algorithms as the
   baseline guarantee), belief-space planning under uncertainty, game-
   theoretic planning against adversaries (pursuit-evasion). Partial
   observability changes the SPACE (plan over beliefs), not just the planner.

## Verification

Planner ships with: space model + DOF stated, algorithm + completeness/
optimality properties named, narrow-passage strategy, and benchmarks on
representative scenes (success rate + path cost + time). "RRT found a path
once" is a demo, not a planner.

## Pairs with

- `modern-robotics` (mechanisms that execute plans),
  `thrun-probabilistic-robotics` (planning under uncertainty),
  `clrs-graph-algorithm-design` (search foundations),
  `artificial-intelligence-modern-approach` (agent context).
