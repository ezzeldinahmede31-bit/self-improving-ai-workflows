---
name: boundary-value-mastery
description: "Edge value analysis mastery distilled. Use when testing limits, valid and invalid groups, edge neighborhoods, min and max values."
---

# Edge Value Mastery

## Purpose

Hunt the defects that cluster at limits: for each input rule, probe the limit values and their immediate neighbors on both sides.

## When to use

Use when the user says 'edge case', 'BVA', 'equivalence class', 'limit testing', 'min max testing', 'edge values'.

## Steps

1. Split each input into valid and invalid groups.
2. For each limit, probe the limit value plus adjacent values on both sides.
3. Treat special inputs (empty, null, max length) as their own limits.
4. Confirm limit behavior against the spec text, not from memory.
5. Record the limit map so new limits get tests when rules change.

## Anti-patterns

- Testing only mid-range happy values.
- Assuming edge membership without reading the spec.
- Forgetting non-numeric limits (empty string, null, timezone ends).
- Copying limits from UI text instead of the real rule.

## Example

Python (name length rule):

```python
@pytest.mark.parametrize("name,valid", [("J", False), ("Jo", True)])
def test_name_limits(name, valid):
    assert is_valid_name(name) is valid
```

JS:

```js
test.each([['J', false], ['Jo', true]])('name %s -> %s', (n, v) => {
  expect(isValidName(n)).toBe(v);
});
```

## Verification

Limit map exists, each limit has probes on both sides, special inputs covered, spec confirms edge membership.

## Pairs-with

off-by-one-boundary-guard, beizer-domain-testing, unit-test-boundary-conditions, graham-istqb-foundations.
