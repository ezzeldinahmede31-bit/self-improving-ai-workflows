---
name: tdd-advanced-patterns
description: "Advanced TDD patterns distilled. Use when practicing test-driven development, red-green-refactor, triangulation, walking skeleton, test doubles strategy."
---

# Advanced TDD Patterns

## Purpose

Practice TDD beyond the basics: red-green-refactor discipline, triangulation toward generality, walking skeleton first, double strategy per boundary.

## When to use

Use when the user says 'TDD', 'red green refactor', 'triangulation', 'walking skeleton', 'test first', 'test-driven'.

## Steps

1. Start thin: a walking skeleton proves the wiring before any feature logic.
2. Write the failing test first; watch it fail for the right reason.
3. Triangulate: second example forces generality, kills hardcoding.
4. Refactor on green only, keeping behavior fixed.
5. Choose doubles by boundary: stub queries, mock commands, fake infrastructure.

## Anti-patterns

- Tests written after code and labeled TDD.
- Giant red steps covering a whole feature.
- Refactoring on red and mixing behavior change with cleanup.
- Mocking value objects and stable domain logic.

## Example

Python:

```python
def test_empty_receipt():
    assert receipt_total([]) == 0      # red
def test_single_item():
    assert receipt_total([("tea", 5)]) == 5   # triangulation
```

JS (vitest): same two-step rhythm with `expect`.

## Verification

Commit history shows red then green, triangulation visible, refactor steps isolated, suite fast.

## Pairs-with

test-driven-development, goos-outside-in-tdd, test-driven-development-by-example-beck, xunit-test-patterns.
