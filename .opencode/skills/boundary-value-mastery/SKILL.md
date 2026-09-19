---
name: boundary-value-mastery
description: "Boundary value analysis mastery distilled. Use when testing edges, partitions, limits, min and max values, edge neighborhoods."
---

# Boundary Value Mastery

## Purpose

Hunt the defects that cluster at edges: for each partition, probe the edge values and their immediate neighbors on both sides.

## When to use

Use when the user says 'boundary value', 'BVA', 'equivalence partition', 'edge case', 'off-by-one', 'min max testing'.

## Steps

1. Partition each input into valid and invalid classes.
2. For each edge, test the edge value plus neighbors just inside and just outside.
3. Treat special levels (zero, empty, null, max length) as their own edges.
4. Confirm edge behavior against the spec text, not from memory.
5. Record the partition map so new edges get tests when limits change.

## Anti-patterns

- Testing only mid-range happy values.
- Assuming inclusive versus exclusive without reading the spec.
- Forgetting non-numeric edges (empty string, null, timezone ends).
- Copying limits from UI text instead of the real rule.

## Example

Python (rule: age in range):

```python
@pytest.mark.parametrize("age,valid", [(17, False), (18, True), (65, True), (66, False)])
def test_age_edges(age, valid):
    assert is_eligible(age) is valid
```

JS:

```js
test.each([[17, false], [18, true], [65, true], [66, false]])('age %i -> %s', (a, v) => {
  expect(isEligible(a)).toBe(v);
});
```

## Verification

Partition map exists, each edge has inside/outside probes, special levels covered, spec confirms inclusivity.

## Pairs-with

off-by-one-boundary-guard, beizer-domain-testing, unit-test-boundary-conditions, graham-istqb-foundations.
