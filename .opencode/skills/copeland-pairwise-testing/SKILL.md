---
name: copeland-pairwise-testing
description: "Covers input combinations efficiently: pairwise and combinatorial design. Use when the user says 'pairwise testing', 'combinatorial testing', 'all-pairs', 'PICT', 'orthogonal arrays', 'Copeland', or when many parameters interact and exhaustive testing explodes."
---

# Copeland Pairwise Testing

Distilled from Lee Copeland *A Practitioner's Guide to Software Test
Design*: most field failures involve ONE factor or the interaction of TWO —
pairwise (all-pairs) coverage catches them with logarithmically few cases
instead of exponentially many.

## Purpose

Tame combinatorial explosions: cover every pair of parameter values with a
tiny, sufficient test set — and know when pairs are not enough.

## The method

1. **Model parameters + values.** List each input factor with its
   equivalence classes (valid + invalid representatives — reuse the
   partitioning skill). Drop irrelevant factors first (modeling discipline
   beats tool cleverness); constrain impossibilities (if OS=X then browser≠Y
   expressed as constraints, or the tool generates fantasy cases).
2. **Generate all-pairs.** Orthogonal arrays (balanced, mathematical) or
   greedy tools (PICT and equivalents handle constraints + weights). Weight
   high-risk values to appear more (risk-weighted pairs). Typical collapse:
   3^10 = 59,049 exhaustive → ~20 pairwise cases. Verify the tool's output
   covers every required pair (tally the pairs, trust the math).
3. **Know the limits.** Empirical rule: ~70% single-factor, ~25% two-factor,
   few three-factor+ faults. Safety-critical / financial logic escalates to
   3-wise+ on the risky subset (cost grows fast — scope it). Pairwise never
   replaces boundary analysis per factor (combine both: pairs OF boundary
   values).
4. **Oracles per case.** Generated cases still need expected results:
   model-based oracles, metamorphic relations (input transform → predictable
   output transform), or specified outcomes per pair. Cases without oracles
   are executions, not tests.
5. **Execute smart.** Independent cases parallelize; order for early signal
   (risky pairs first); failing pair → isolate the minimal culprit pair by
   bisection (which two values actually interact?).

## Verification

Combinatorial plan ships with: parameter model + constraints, generation
method + pair-coverage proof, oracle per case, boundary values included,
escalation rationale where 2-wise was deemed enough. Exhaustive testing
claims on multi-factor inputs are rejected as infeasible.

## Pairs with

- `myers-art-of-testing` (partitioning inputs),
  `beizer-domain-testing` (boundaries per factor),
  `ammann-offutt-criteria` (coverage theory),
  `okken-pytest-craft` (parametrize the generated matrix).
