---
name: retry-backoff-jitter
description: "Configures transient retries with exponential backoff, jitter, budgets, classification. Use for flaky APIs."
---

# Retry with Backoff and Jitter

Tight retries amplify outages.

## Workflow
1. Classify retryable (429, 5xx, timeout) vs permanent (4xx validation).
2. Set base, multiplier, jitter, attempt cap, deadline.
3. Honor Retry-After over computed delay.
4. Chaos-test: force failures, verify spaced retries + loud terminal failure.

## Core Rules
- Cap total wall-clock budget.

## Pairs with
- `cloud-resilience-patterns`, `circuit-breaker-api-calls`, `rate-limit-aware-consumers`
