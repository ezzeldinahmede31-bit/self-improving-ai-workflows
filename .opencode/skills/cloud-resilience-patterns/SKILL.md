---
name: cloud-resilience-patterns
description: Applies the resilience patterns of Cornelia Davis' Cloud Native Patterns to applications that must survive partial failure: circuit breakers, retries with backoff and jitter, timeouts and bulkheads, graceful degradation, steady-state behavior, and the observability that proves the system is healing. Use when the user says 'circuit breaker', 'retry with backoff', 'timeout', 'bulkhead', 'graceful degradation', 'resilient design', 'survive a dependency outage', 'cloud resilience', 'self-healing', 'retry storm', 'cascading failure', or when an app must keep serving while an upstream is down. Pairs with: cloud-native-patterns, release-it-production-hardening, rate-limit-and-cost-guard, n8n-error-boundary-architect.
---

# Cloud Resilience Patterns

Transfers the resilience patterns of Cornelia Davis' Cloud Native Patterns to applications that must keep working while their dependencies fail.

## When to use
- An app calls external services that occasionally go down or get slow.
- A failing dependency must not take the whole system down with it.
- You are designing retries, timeouts, or degraded behavior for an automation, service, or workflow.

## Circuit breaker
- Let a failing dependency fail fast after a threshold, instead of hammering it and piling up latency.
- Track the last N calls; when failures cross the threshold, open the circuit and short-circuit further calls.
- Open the circuit again gradually after a cool-down window and a successful probe call.
- Report the open/closed state so operators see the breaker, not just symptoms.

## Retries with backoff and jitter
- Retry only idempotent operations; a retried non-idempotent write can duplicate side effects.
- Use exponential backoff so retries do not pile up exactly when the dependency is weakest.
- Add jitter to the backoff so many clients do not retry in lockstep and create a thundering herd.
- Cap retries; an unbounded retry loop turns a small outage into a long one.

## Timeouts and bulkheads
- Every dependency call needs a timeout; an unbounded wait becomes a hung thread and a saturated pool.
- Give each dependency its own connection pool (bulkhead) so one slow service cannot consume the shared budget.
- A timed-out call should release its resources immediately and fail cleanly.

## Graceful degradation
- When a dependency is down, serve the closest working alternative: cached data, a default value, or a reduced feature set.
- Degrade per-feature, not globally; keep the core path alive while optional features fall back.
- Never hide the degradation: the response and logs must state which capability was reduced and why.

## Observability that proves healing
- Expose breaker state, retry counts, timeout rates, and fallback usage as metrics.
- Alert on the transition into degraded mode, not only on hard failure.
- Verify recovery with a probe call that must succeed before the system reports healthy again.

## Verification discipline
- Simulate a failing dependency and assert the app still serves the core path.
- Test the threshold where the breaker opens and the cool-down where it reopens.
- Assert no retry storm: cap the total retries and confirm backoff plus jitter in logs.

## Pairs with
cloud-native-patterns, release-it-production-hardening, rate-limit-and-cost-guard, n8n-error-boundary-architect.