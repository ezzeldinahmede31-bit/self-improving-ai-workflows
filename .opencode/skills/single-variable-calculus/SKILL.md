---
name: single-variable-calculus
description: "Uses calculus where computer science actually needs it: growth, optimization, and series. Use when the user says 'derivative', 'gradient descent', 'Taylor series', 'integral', 'convergence', 'rate of change', 'optimize', 'Newton method', 'calculus', or when an algorithm question becomes a math-of-change question."
---

# Single-Variable Calculus for CS

Distilled from MIT 18.01 (single-variable calculus, differentiation /
integration / series): the working subset a computer scientist uses weekly —
rates, optima, and approximations.

## Purpose

Turn "how fast does this change" and "where is the optimum" into computations
with error bounds — the foundation under ML optimization and algorithm
analysis.

## The working subset

1. **Differentiation = local linearity.** Rules (chain/product/quotient) plus
   the meaning: f'(x) is the best linear approximation. Implicit
   differentiation for relations; related rates for linked quantities.
2. **Optimization.** Critical points + first/second derivative tests; global
   optima on closed intervals; constrained intuition (Lagrange idea: gradients
   align at constrained optima). Gradient descent = follow -f' downhill; step
   size trades speed against divergence.
3. **Integration = accumulation.** Fundamental theorem both directions;
   substitution + parts as the two moves. Applications that recur: areas,
   averages/expected values, work/sums-turned-integrals for asymptotics
   (integral test bounds discrete sums — the analysis workhorse).
4. **Series and approximation.** Taylor with REMAINDER (the remainder is the
   result — a series without its error bound is a guess). Geometric, p-series,
   alternating-series tests; radius of convergence. Use: exp/log/trig
   approximations, complexity of iterative refinement, series solutions.
5. **Differential equations, lightly.** Separable/first-order linear;
   qualitative behavior (equilibria, stability) matters more than closed
   forms for modeling (queues, populations, learning curves).

## CS payoffs (why this course earns its place)

- Growth-rate comparisons in algorithm analysis are calculus comparisons.
- Gradient-based learning IS multivariate calculus + chain rule at scale.
- Sums <-> integrals convert hard discrete analysis into routine calculus.

## Verification

Each claim ships with: the derivative/integral/series used, the remainder or
error bound, and a discrete check (small-n computation agreeing). No bound,
no trust.

## Pairs with

- `heath-numerical-methods` (computing what calculus describes),
  `strang-linear-algebra` (multivariate extension),
  `machine-learning-yearning` (optimization decisions),
  `think-stats` (expectation as integration).
