---
name: heath-numerical-methods
description: "Computes with floating point honestly: conditioning, stability, and the right algorithm. Use when the user says 'numerical error', 'floating point', 'catastrophic cancellation', 'condition number', 'LU decomposition', 'iterative solver', 'interpolation', 'quadrature', 'ODE solver', 'Runge-Kutta', 'Heath', 'numerical methods', or when numbers come out wrong and algebra says they should be right."
---

# Heath Scientific Computing

Distilled from Heath's *Scientific Computing: An Introductory Survey*: every
numerical answer has TWO errors (problem sensitivity x algorithm damage) — a
trustworthy computation bounds both.

## Purpose

Pick algorithms whose error you can state, and distrust any number whose error
you cannot.

## The discipline

1. **Separate conditioning from stability.** Conditioning = the PROBLEM's
   sensitivity (condition number: small input change -> large output change
   means ill-conditioned, no algorithm saves you). Stability = the
   ALGORITHM's damage (backward-stable = exact answer to a nearby problem).
   Diagnose which one bites before "fixing" anything.
2. **Floating point hygiene.** Catastrophic cancellation (subtracting nearly
   equal numbers) is the #1 killer: reformulate (rationalize, use `expm1`/
   `log1p`, sum small-to-large, Kahan when it matters). Never test `==` on
   floats; compare with scaled tolerances.
3. **Linear systems that deserve trust.** Dense: LU with partial pivoting
   (never explicit inverse — solve, don't invert). Least squares: QR, not
   normal equations. Large/sparse: iterative (CG for SPD, GMRES otherwise)
   with a preconditioner; monitor the residual, not the iteration tally.
4. **Interpolation without tears.** High-degree global polynomials oscillate
   (Runge) — use piecewise (cubic splines) or Chebyshev nodes. Extrapolation
   is guessing; say so.
5. **Integrate and differentiate carefully.** Quadrature: Gauss rules for
   smooth, adaptive for rough. Differentiation AMPLIFIES noise — differentiate
   analytic forms when possible, use higher-order stencils otherwise, and
   never difference noisy data without smoothing.
6. **ODEs: match solver to stiffness.** Non-stiff: explicit Runge-Kutta with
   adaptive steps. Stiff (chemical kinetics, circuits): implicit methods
   (backward Euler/BDF) or the step total explodes. Symplectic/conservative
   integrators for long-time physics.

## Verification

Every numerical result ships with: the condition estimate, the algorithm +
why stable here, and an independent check (refined mesh/step, alternative
method, or conservation law). Disagreement beyond tolerance = open problem,
not a rounding artifact.

## Pairs with

- `strang-linear-algebra` (the matrix theory underneath),
  `formal-math-logic-verification-engine` (sympy cross-checks),
  `experiment-code` (convergence studies), `think-stats` (noisy data).
