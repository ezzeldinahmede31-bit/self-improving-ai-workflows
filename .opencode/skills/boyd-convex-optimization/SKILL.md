---
name: boyd-convex-optimization
description: "Solves optimization the Boyd way: convex formulation, duality, and first-order methods. Use when the user says 'convex optimization', 'Lagrangian duality', 'KKT conditions', 'gradient descent', 'proximal methods', 'ADMM', 'Boyd', 'formulate as convex', or when any fitting/control/resource problem must be solved reliably."
---

# Boyd Convex Optimization

Distilled from Boyd & Vandenberghe *Convex Optimization*: if you can cast it
convex, you can solve it globally and certify the answer. Most of applied ML,
control, and resource allocation is this sentence in disguise.

## Purpose

Formulate problems so a solver (not hope) finishes them: recognize convexity,
exploit structure, and certify optimality with duality.

## The method

1. **Recognize convexity.** Convex set (line segments stay inside) + convex
   function (epigraph convex; Jensen holds). Atoms that preserve it: affine
   maps, norms, max of convex, composition with nondecreasing convex.
   Non-convex sighting? Try change of variables, relaxation (rank -> nuclear
   norm, Boolean -> box), or split into convex subproblems.
2. **Write the standard form.** minimize f0(x) s.t. fi(x)<=0, Ax=b. Read off:
   what is variable, what is data. A clean standard form is half the solution.
3. **Duality certifies.** Lagrangian L, dual function g, weak duality
   (dual <= primal, always — a free lower bound). KKT: stationarity, primal/
   dual feasibility, complementary slackness. Strong duality (equality) holds
   under Slater's condition — then KKT is necessary AND sufficient.
4. **Pick the algorithm by structure.** Smooth unconstrained: gradient/Newton
   (Newton needs Hessians; quasi-Newton when they are dear). Constrained:
   interior-point for medium/dense; first-order (proximal gradient, ADMM)
   for large/structured — ADMM splits separable objectives across agents.
5. **Rates honestly.** Strong convexity + smoothness give linear rates;
   nonsmooth gives sublinear — match expectations to conditioning, precondition
   (scale variables!) before blaming the algorithm.

## Verification

Deliverable per problem: convexity proof sketch (composition rules cited),
dual + duality gap at termination, and KKT residual. A "solution" without a
gap bound is a warm start, not an answer.

## Pairs with

- `strang-linear-algebra` (quadratic forms, conditioning),
  `machine-learning-yearning` (loss/optimization decisions),
  `heath-numerical-methods` (floating-point reality),
  `thinking-probabilistic` (stochastic variants).
