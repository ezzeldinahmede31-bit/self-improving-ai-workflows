---
name: mcconnell-software-estimation
description: "Estimates software honestly: ranges, calibration, and cone of uncertainty. Use when the user says 'how long will this take', 'estimate', 'story points', 'planning poker', 'cone of uncertainty', 'commitment vs estimate', 'McConnell', or when a deadline must survive reality."
---

# McConnell Software Estimation

Distilled from Steve McConnell's *Software Estimation*: estimates are
probability statements about the future, not promises — treat them as ranges
with stated confidence, and narrow them with knowledge, not pressure.

## Purpose

Produce estimates that inform decisions (and get better with feedback)
instead of numbers that become weapons in the next status meeting.

## The discipline

1. **Estimate ranges, never points.** Every estimate ships as
   best-case/likely/worst-case (or explicit percentiles). A point estimate
   without its spread has deleted the information the decision needed.
2. **Respect the Cone of Uncertainty.** Early estimates carry 4x variance;
   convergence comes from decided scope, not from re-estimating harder.
   Commit to dates only as late as the cone allows — committing at 4x
   uncertainty is gambling with extra steps.
3. **Decompose and triangulate.** Break work until pieces are estimable
   (hours-to-days each), estimate bottom-up, then cross-check top-down
   (analogy to past projects, parametric models like COCOMO-style sizing).
   Methods that disagree flag unknown unknowns — investigate the gap.
4. **Calibrate with history.** Track estimated-vs-actual per estimator and
   per task type; apply personal/team correction factors openly. Estimation
   skill is measured, not asserted — keep the ledger.
5. **Separate estimates from commitments.** An estimate informs a plan; a
   commitment adds buffer + negotiation + ownership. Never let a target
   retroactively become "the estimate". Present options
   (scope/date/resources — pick two pressures to relieve) instead of a
   single sacrificial date.
6. **Re-estimate on knowledge, not on calendar.** New information (decided
   scope, prototypes, spikes) triggers re-estimation; the passage of time
   alone does not improve accuracy.

## Verification

Estimate package contains: decomposition, per-piece ranges, method used per
piece, calibration data cited, cone position stated, and the explicit
non-commitment disclaimer until a commitment is negotiated. A naked date is
rejected as an artifact.

## Pairs with

- `high-output-management`/`managerial-leverage-okrs` (planning with
  estimates), `berkun-making-things-happen` (schedule leadership),
  `thinking-probabilistic` (ranges and confidence),
  `risk-management-failure-mode-autonomous` (estimate risks).
