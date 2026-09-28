---
name: distributed-tracing
description: "Distributed tracing skill (trace-id propagation, JSONL spans, latency report). Use when a slow execution needs its seconds located, when hops span services, or when a downstream call must continue the same trace. Trigger phrases: 'trace this run', 'where did time go', 'trace-id', 'تتبع موزع'."
---

# Distributed Tracing (Find the Lost Seconds)

Code: `tracing.py` (stdlib only, context-var isolated). `start_trace()`
opens ingress; `span()` records named hops; `adopt()` continues from
propagated ids downstream; `report()` returns spans + per-span latency
+ total. Context vars keep concurrent traces apart with zero signature
plumbing.

## Verification

- `tests/test_p1c_deploy_trace.py` tracing half green (spans, report,
  adopt-continue).
- Slow-path reviews start from a trace report, not guesses.

## Pairs with

`slo-engine` (latency source), `observability.py` (log sink),
`n8n-delivery-verification-gate` (execution evidence),
`build-gates-pipeline`.
