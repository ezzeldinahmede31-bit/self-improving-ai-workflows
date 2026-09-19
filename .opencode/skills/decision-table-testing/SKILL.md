---
name: decision-table-testing
description: "Decision table testing distilled. Use when testing business rules, condition combinations, rule coverage, untestable rule gaps."
---

# Decision Table Testing

## Purpose

Turn tangled business rules into a table of conditions versus actions, then test every rule column including the ones that reveal missing requirements.

## When to use

Use when the user says 'decision table', 'business rules', 'condition combination', 'rule coverage', 'discount rules'.

## Steps

1. List conditions (with their value options) and resulting actions.
2. Build columns for each combination; collapse don't-care entries honestly.
3. Mark impossible columns as constraints, not tests.
4. Write one test per live column with a business-readable name.
5. Review blank or contradictory columns with the rule owner.

## Anti-patterns

- Collapsing columns before the owner confirms the don't-cares.
- Testing only the columns that already work.
- Rules living in code comments instead of the table.
- Duplicate columns that hide contradictory actions.

## Example

Python:

```python
@pytest.mark.parametrize("vip,over100,expected", [
    (True, True, 20), (True, False, 10), (False, True, 5), (False, False, 0),
])
def test_discount_rule(vip, over100, expected):
    assert discount(vip, over100) == expected
```

## Verification

Each live column has a named test, impossible columns documented as constraints, owner reviewed contradictions.

## Pairs-with

graham-istqb-foundations, beizer-domain-testing, adzic-specification-by-example, state-transition-testing.
