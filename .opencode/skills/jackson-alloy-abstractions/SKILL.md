---
name: jackson-alloy-abstractions
description: "Models software with lightweight formal abstractions: signatures, facts, and automated checks. Use when the user says 'Alloy', 'software abstractions', 'model checking', 'formal specification', 'assertions', 'counterexample', 'Daniel Jackson', or when a design must be verified before it is built."
---

# Jackson Alloy Software Abstractions

Distilled from Daniel Jackson's *Software Abstractions*: most design flaws
are conceptual, not coding — and concepts can be checked by a machine in
minutes, before a line of implementation exists.

## Purpose

Write down what the software is ABOUT (its core concepts and rules) in a
form the Alloy analyzer can attack — and fix what it breaks, while fixing
is still cheap.

## The method

1. **Find the concepts.** The deep ideas users manipulate (not the UI, not
   the code): e.g. "reservation", "label", "trash". One concept per purpose;
   if two purposes share a concept, split or merge deliberately.
2. **Model signatures and relations.** `sig File { link: lone File }` style:
   sets of atoms + relations among them. State = collection of relations;
   operations = predicates transforming state. Keep it minimal — model the
   concept, not the system.
3. **Assert the properties.** Invariants ("no dangling links"), safety
   ("trash is empty after emptying"), idempotence, reversibility. Write the
   assertion BEFORE running: the assertion is the requirement made checkable.
4. **Let the analyzer attack.** `check` within a scope: Alloy searches all
   small instances exhaustively (small-scope hypothesis: most flaws show up
   tiny). A counterexample is a gift — a concrete scenario your intuition
   missed.
5. **Grow scope and refine.** Fix the model (strengthen facts, correct the
   operation), re-check, widen scope. Uncheckable sprawl means the concept
   is muddy — simplify the idea, not the analysis.

## What Alloy is (and is not)

- IS: a design-time bug finder for structural/logic flaws, fully automatic
  within scope, brutally honest about edge cases.
- IS NOT: a code verifier, a tester of implementations, or proof of
  absence beyond the checked scope. Pair with tests for the code itself.

## Verification

Design review ships with: concept list with purposes, Alloy model + checked
assertions, counterexamples found and fixed (the log IS the value), scope
used per check. A design with unchecked core concepts is a hypothesis, not
a design.

## Pairs with

- `domain-driven-design-strategic` (concept discovery),
  `formal-math-logic-verification-engine` (proof mechanics),
  `proactive-spec-expander` (requirement capture),
  `tdd-sandbox-proof-engine` (implementation-side checks).
