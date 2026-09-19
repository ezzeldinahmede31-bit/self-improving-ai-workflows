---
name: claessen-property-testing
description: "Tests properties not examples: generators, invariants, and shrinking. Use when the user says 'property-based testing', 'QuickCheck', 'Hypothesis', 'generators', 'shrinking', 'invariants', 'metamorphic', 'Claessen Hughes', or when examples pass but edge cases lurk."
---

# Claessen Property-Based Testing

Distilled from Claessen & Hughes QuickCheck lineage (and the Hypothesis
practice): stop writing examples — state PROPERTIES (invariants, round-
trips, metamorphic relations) and let the machine generate a thousand
adversarial cases plus the minimal failure.

## Purpose

Cover input spaces no example suite can: properties hold across generated
cases, failures shrink to minimal reproducers automatically.

## The practice

1. **Properties, not examples.** Forms that recur: round-trip (encode;
   decode = identity), idempotence (f(f(x)) = f(x)), invariants (sorted
   stays sorted, balance never negative), metamorphic (transform input →
   predictable output transform), model-based (implementation agrees with a
   simple reference model). One property beats fifty examples where it
   applies.
2. **Generators mirror reality.** Default strategies first, then custom
   generators matching production distributions (sizes, unicode, edge-heavy:
   empty/zero/max/negative). Wrong distribution = tested fantasy. Stateful
   systems get command-sequence generators (model-based state-machine
   testing).
3. **Shrinking is the product.** A failing 200-element blob teaches nothing;
   the shrinker reduces to the minimal failing case automatically. Verify
   shrinking works (write a known bug, confirm minimal repro). Custom types
   need custom shrinkers — budget for them.
4. **Examples + properties, layered.** Examples document and pin regressions
   (readable, in the suite forever); properties explore (hundreds of cases
   per run, in CI with fixed profiles + nightly with bigger budgets).
   Deterministic seeds recorded; failures replayable.
5. **Stateful/model-based for protocols.** Model the expected state machine
   simply; generate command sequences; assert implementation matches after
   every step. Finds the deep state bugs example tests never reach
   (the highest-ROI PBT application).

## Verification

PBT review: properties listed with their form named, generator distribution
justified against production data, shrinking demonstrated on a planted bug,
CI profiles (fast/nightly) configured, stateful coverage where state
exists. Examples-only on complex logic is under-testing.

## Pairs with

- `tdd-sandbox-proof-engine` (properties as executable specs),
  `zeller-fuzzing-book` (generators meet coverage),
  `okken-pytest-craft` (Hypothesis profiles in CI),
  `ammann-offutt-criteria` (coverage theory underneath).
