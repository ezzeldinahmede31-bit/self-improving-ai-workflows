---
name: refactoring-principles-fowler
description: "Applies Fowler Refactoring to improve design safely via behavior-preserving steps. Use when cleaning code, smells, or preparing for change."
---

# Refactoring Principles (Fowler)

Small behavior-preserving steps beat big rewrites.

## Workflow
1. Name the smell (long method, duplicated logic, tangled condition).
2. Pick the catalog recipe (extract method/variable, move, inline, replace conditional with polymorphism).
3. Apply one mechanical step, run tests.
4. Repeat until design reads clearly.

## Core Rules
- Tests green before and after each step.
- One transformation at a time.

## Pairs with
- `refactoring-improving-design`, `refactoring-catalog-recipes`, `clean-code`
