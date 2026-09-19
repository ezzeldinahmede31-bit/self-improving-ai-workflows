---
name: resilience-circuit-testing
description: "Resilience and circuit breaker testing distilled. Use when testing timeouts, retries, breakers, bulkheads, fallbacks, failover drills."
---

# Resilience Circuit Testing

## Purpose

Prove graceful degradation: timeouts bound every call, retries stay budgeted, breakers open fast, bulkheads isolate, fallbacks serve.

## When to use

Use when the user says 'circuit breaker', 'resilience test', 'bulkhead', 'fallback', 'failover', 'retry budget', 'timeout'.

## Steps

1. Bound every dependency call with explicit timeouts.
2. Budget retries with backoff plus jitter; never unbounded.
3. Trip breakers in tests; assert fast failure plus fallback content.
4. Isolate with bulkheads so one slow dependency cannot starve others.
5. Drill failover end to end; measure detection plus recovery time.

## Anti-patterns

- No timeouts on downstream calls.
- Retries amplifying an outage into a storm.
- Breakers configured but never tripped in tests.
- Fallbacks returning success shapes that lie.

## Example

Python:

```python
breaker.force_open()
assert checkout() == degraded_response  # fallback serves honestly
```

## Verification

Timeouts explicit, retries budgeted, breakers tripped in tests, failover drilled with timings.

## Pairs-with

chaos-testing-patterns, cloud-resilience-patterns, release-it-production-hardening, retry-backoff-jitter.
