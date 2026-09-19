---
name: pairwise-advanced-constraints
description: "Advanced pairwise testing with constraints distilled. Use when pairwise arrays need forbidden combos, seeding, mixed strength, real config models."
---

# Pairwise With Advanced Constraints

## Purpose

Make pairwise practical on real systems: forbid impossible combos, seed must-test cases, mix strengths per subsystem.

## When to use

Use when the user says 'pairwise constraints', 'forbidden combination', 'seed test', 'mixed strength', 'PICT constraints'.

## Steps

1. Model factors honestly, including dependent ones.
2. Encode IF-THEN constraints for impossible combos.
3. Seed high-value cases that must appear regardless of optimization.
4. Use higher strength locally for risky subsystems, pairs elsewhere.
5. Validate the generated set: constraints hold, seeds present, size sane.

## Anti-patterns

- Pairwise without constraints producing impossible-case failures.
- Seeds fighting constraints (over-constrained model, empty output).
- Same strength everywhere, wasting budget on low-risk areas.
- Regenerating without versioning the model file.

## Example

PICT with constraint:

```
OS: Win, Linux
Mode: Admin, Guest
IF [OS] = "Linux" THEN NOT [Mode] = "Admin";
```

## Verification

No impossible combos in output, seeds present, model versioned, failures mapped to real interactions.

## Pairs-with

copeland-pairwise-testing, combinatorial-testing-t-way, classification-tree-testing, test-data-management.
