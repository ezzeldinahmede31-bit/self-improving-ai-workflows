---
name: combinatorial-testing-t-way
description: "Combinatorial t-way testing distilled. Use when covering parameter interactions, pairwise and three-way combos, covering arrays, config explosion."
---

# Combinatorial T-Way Testing

## Purpose

Cover parameter interactions systematically: most faults come from single factors or pairs, so test all pairs (and triples where risk demands) instead of exhaustive combos.

## When to use

Use when the user says 'combinatorial testing', 'pairwise', 't-way', 'covering array', 'parameter interaction', 'config explosion'.

## Steps

1. List factors and their values (keep value counts small and realistic).
2. Choose strength: pairs by default, triples for high-risk integrations.
3. Generate a covering array with a tool (PICT, AllPairs, ACTS).
4. Add seed cases for known-critical combos the array might place awkwardly.
5. Execute and map each failure back to the interacting factors.

## Anti-patterns

- Exhaustive combos that never finish.
- Pairwise over meaningless values nobody configures.
- Ignoring constraints (impossible combos tested as failures).
- Treating the generated set as fixed forever instead of regenerating on change.

## Example

PICT model:

```
OS: Win, Linux, Mac
Browser: Chrome, Firefox
Auth: SSO, Basic
```

Python pairwise spot check:

```python
@pytest.mark.parametrize("os,browser", [("Linux", "Chrome"), ("Win", "Firefox")])
def test_login_matrix(os, browser):
    assert login(os, browser).ok
```

## Verification

Covering array covers the chosen strength, constraints honored, failures mapped to factor interaction.

## Pairs-with

copeland-pairwise-testing, pairwise-advanced-constraints, classification-tree-testing, beizer-domain-testing.
