---
name: beizer-domain-testing
description: "Tests input domains ruthlessly: boundaries, closures, and multidimensional edges. Use when the user says 'domain testing', 'boundary analysis', 'Beizer', 'closure of boundaries', 'onn/off points', 'multidimensional domain', or when numeric/string inputs need exhaustive edge coverage."
---

# Beizer Domain Testing

Distilled from Boris Beizer's domain-testing strategy (*Black-Box Testing*,
*Software Testing Techniques*): bugs live ON domain boundaries — test every
boundary point from both sides, in every dimension that matters.

## Purpose

Cover input domains so thoroughly that boundary bugs have nowhere to hide:
on/off points per boundary, closure discipline, and dimensional expansion.

## The method

1. **Map the domain.** For each input variable: type, valid range(s),
   discrete vs continuous, dependencies on other inputs (coupled domains
   multiply — model the PRODUCT space, not each axis alone).
2. **On/off points per boundary.** For every boundary: ON point (exactly on
   it) + OFF point (closest neighbor outside, per the domain's granularity:
   ±1 for integers, epsilon for floats). Closed boundaries (in-point valid)
   vs open (out-point valid) — test the closure YOU implemented, which may
   differ from the spec (that difference IS the bug class).
3. **1×1 domain testing (the sweet spot).** One ON + one OFF per boundary:
   catches shifts and tilts of the implemented boundary vs specified.
   2×2 (both sides doubled) where the cost of escape justifies it.
4. **Multidimensional expansion.** Boundaries in N variables form surfaces:
   test vertices and edge midpoints of the domain (not just per-axis
   extremes — the bug hides at the CORNER where two boundaries meet).
   Dependent variables get joint partitions, never independent ones.
5. **Domain closure audit.** Every boundary in code traced to a spec
   boundary (extra code boundaries = unrequested behavior; missing ones =
   unchecked inputs). Inequality direction reviewed character by character
   (`<` vs `<=` is the most expensive single character in software).

## Verification

Per input domain: boundary list with on/off points executed, closure
(open/closed) asserted per boundary, corner cases in coupled dimensions run.
A numeric input without on/off triples is untested at exactly the points
that fail.

## Pairs with

- `myers-art-of-testing` (partitioning foundation),
  `off-by-one-boundary-guard` (the ±1 discipline),
  `copeland-pairwise-testing` (multi-variable combinations),
  `ammann-offutt-criteria` (input-space partitioning theory).
