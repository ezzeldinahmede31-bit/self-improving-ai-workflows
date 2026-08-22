---
name: timeout-graceful-degradation
description: "Bounds calls with explicit timeouts, defines degraded modes. Use for dependency resilience."
---

# Timeouts and Graceful Degradation

Missing timeouts -> hung workflows.

## Workflow
1. Assign per-call timeout from p99 plus margin.
2. Classify core vs optional deps; degrade optional only.
3. Pre-build degraded modes (cached/reduced/honest notice).
4. Propagate deadlines downstream.

## Core Rules
- Surface degradation visibly.

## Pairs with
- `release-it-production-hardening`, `circuit-breaker-api-calls`, `systems-performance-profiling`
