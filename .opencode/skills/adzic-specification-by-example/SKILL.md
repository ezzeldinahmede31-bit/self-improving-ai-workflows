---
name: adzic-specification-by-example
description: "Gojko Adzic Specification by Example distilled. Use when writing acceptance criteria, BDD scenarios, living documentation, example mapping, executable specifications."
---

# Specification by Example

## Purpose

Turn vague requirements into shared executable examples per Gojko Adzic: derive scope from goals, specify collaboratively with realistic examples, automate without changing specs, living documentation.

## When to use

Use when the user says 'acceptance criteria', 'BDD', 'Gherkin', 'living documentation', 'example mapping', 'specification by example', 'Adzic', 'executable spec'.

## Steps

1. Derive scope from business goals (not feature lists).
2. Run example mapping: story -> rules -> concrete examples -> open questions.
3. Write scenarios declaratively (intent, not UI clicks): Given context, When action, Then business outcome.
4. Automate the specification layer once; keep glue thin and stable.
5. Publish as living documentation reviewed on every change.

## Anti-patterns

- Imperative Gherkin full of click-by-click UI steps (brittle).
- Examples invented solo without business/dev/tester trio.
- Automating before the examples are agreed (locks in confusion).
- Scenarios without a business rule they illustrate.

## Example

```gherkin
Scenario: Free shipping over threshold
  Given a cart totaling 60
  When checkout completes
  Then shipping cost is 0
```

Python glue (pytest-bdd style):

```python
@when('checkout completes')
def _checkout(cart, shipping):
    cart.total = shipping.apply(cart.items)
```

## Verification

Every scenario traces to one rule; trio agrees examples are realistic; suite runs green in CI; docs regenerate from specs.

## Pairs-with

goos-outside-in-tdd, crispin-agile-testing, end-to-end-workflow-testing, beizer-domain-testing.
