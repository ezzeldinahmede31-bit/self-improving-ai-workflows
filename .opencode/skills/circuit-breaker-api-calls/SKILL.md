---
name: circuit-breaker-api-calls
description: "Opens circuits after threshold failures, probes recovery, fails fast. Use for failing deps."
---

# Circuit Breakers for API Calls

Stop hammering a down dependency.

## Workflow
1. Open after N failures in window.
2. While open, fail immediately without network.
3. Half-open probes with limited traffic.
4. Export state as metric.

## Core Rules
- Pair with fallback.

## Pairs with
- `release-it-production-hardening`, `retry-backoff-jitter`, `timeout-graceful-degradation`
