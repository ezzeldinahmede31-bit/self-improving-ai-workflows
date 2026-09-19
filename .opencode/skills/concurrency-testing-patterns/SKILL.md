---
name: concurrency-testing-patterns
description: "Concurrency testing patterns distilled. Use when testing threads, races, deadlocks, thread pools, parallel access, shared state."
---

# Concurrency Testing Patterns

## Purpose

Expose threading defects deterministically where possible: stress plus targeted interleaving, timeouts, and invariant checks under parallel load.

## When to use

Use when the user says 'concurrency test', 'race condition', 'deadlock', 'thread safety', 'parallel test', 'shared state'.

## Steps

1. State the invariant that must hold under any interleaving.
2. Stress with parallel workers while asserting the invariant continuously.
3. Force interleavings at known preemption points (latches, barriers).
4. Bound every wait with timeouts so deadlocks fail loudly.
5. Repeat runs with varied seeds; quarantine ordering-dependent cases.

## Anti-patterns

- Single-threaded tests as proof of thread safety.
- Sleeps used as synchronization in tests.
- Shared fixtures mutated across parallel tests.
- Deadlock surfacing as a hung CI job with no diagnostics.

## Example

Python:

```python
def test_parallel_deposits_keep_balance():
    acct = Account(100)
    run_parallel([lambda: acct.deposit(10)] * 20)
    assert acct.balance == 300
```

## Verification

Invariant asserted under parallelism, waits bounded, interleavings forced at seams, repeats stable.

## Pairs-with

multiprocessor-concurrency, concurrent-lock-free-structures, async-testing-patterns, flaky-test-elimination.
