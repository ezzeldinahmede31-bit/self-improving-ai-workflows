---
name: flaky-test-elimination
description: "Flaky test elimination distilled. Use when quarantining flakes, root-causing nondeterminism, retry budgets, ordering dependence, seed control."
---

# Flaky Test Elimination

## Purpose

Drive flake rate toward zero: detect with stats, quarantine fast, fix root causes (time, order, shared state, network), never normalize retries.

## When to use

Use when the user says 'flaky test', 'intermittent failure', 'quarantine', 'nondeterministic test', 'flake rate', 'order dependent'.

## Steps

1. Measure flake rate per test from CI history; rank worst first.
2. Quarantine immediately so main stays trustworthy; track quarantine age.
3. Root-cause by family: clock, ordering, shared state, network, resource leak.
4. Fix with determinism (fake clocks, isolation, seeds, hermetic doubles).
5. Keep a strict retry budget as detection, never as the fix.

## Anti-patterns

- Retrying failures into silence.
- Quarantine as a permanent parking lot.
- Shared mutable fixtures across tests.
- Real network and real time in unit scope.

## Example

Python quarantine marker:

```python
@pytest.mark.quarantine(reason="clock-dependent, see QA-118")
def test_billing_midnight_rollover():
    ...
```

## Verification

Flake ranking exists, quarantine list short with owners, fixes remove nondeterminism, retries bounded.

## Pairs-with

async-testing-patterns, concurrency-testing-patterns, test-data-management, quality-metrics-dashboard.
