---
name: observability-execution-monitoring
description: "Watches health via metrics, structured logs, alerts on stall/failure. Use for ops."
---

# Observability and Execution Monitoring

Discover outages from alerts, not user complaints.

## Workflow
1. Record status/duration/tally/error class per execution.
2. Structured logs with correlation IDs.
3. Alerts on failure-rate jumps, stalls, queue growth, zero-item successes.
4. Dashboard: health at a glance per critical flow.

## Core Rules
- Zero-item success -> suspicious by default.

## Pairs with
- `sre-reliability-engineering`, `systems-performance-profiling`, `n8n-delivery-verification-gate`
