---
name: refactoring-improving-design
description: Applies Martin Fowler's Refactoring to improve existing code safely: the refactoring catalog (rename, extract, inline, move, replace), the discipline of behavior-preserving transformations, and the test-driven rhythm that keeps every step safe. Use when the user says 'refactoring', 'extract method', 'extract class', 'rename', 'move method', 'improve the design of existing code', 'Fowler refactoring', 'behavior preserving change', or when existing code must be improved without breaking it.
---

# Refactoring: Improving the Design of Existing Code (Martin Fowler)

Fowler's Refactoring catalog turns redesign into a sequence of small, safe steps. This skill applies that rhythm to real codebases.

## The refactoring discipline

- A refactoring changes structure without changing behavior; tests prove the behavior holds.
- Refactor in small steps, running the tests after each one.
- When the tests fail, revert the last step and understand why before proceeding.

## The catalog

- Rename makes intent clear; extract method and extract class break up the large and the tangled.
- Inline undoes an abstraction that no longer earns its keep; move relocates behavior to the right home.
- Replace conditional with polymorphism and other catalog entries remove the smells that complicate.

## Code smells as triggers

- The catalog exists to remove smells: long methods, large classes, duplicate code, switch statements.
- Name the smell, then choose the refactoring that removes it.
- Duplicated code is the most reliable signal that a refactoring is due.

## Working with legacy code

- Without tests, refactor in the safest small steps and add characterization tests first.
- The seams you can see are the seams you can change.
- Refactoring is a daily practice, not a rewrite project; every session leaves the design a little better.

## Pairs with
clean-code, legacy-code-characterization, code-smell-detector, test-driven-development, xunit-test-patterns
