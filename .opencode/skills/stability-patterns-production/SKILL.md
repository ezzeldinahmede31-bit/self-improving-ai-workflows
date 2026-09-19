---
name: stability-patterns-production
description: "Make n8n systems survive the real world with Nygard stability patterns mapped to workflow nodes: timeouts, circuit breakers, bulkheads, fail fast, shed load, backpressure, steady state — plus the antipatterns that cause cascading failures. Use when a workflow must survive slow APIs, traffic spikes, partial outages, or when one failing lane takes down the rest. Pairs with n8n-error-boundary-architect, n8n-oom-crash-recovery, live-workflow-surgery, rate-limit-and-cost-guard."
---

# Stability Patterns for Production

Eighty percent of lifecycle cost is production. Design for it up front.

## Sources (adopted baselines)

- "Release It! 2e" (Nygard, Pragmatic): stability ANTIPATTERNS (integration
  points, chain reactions, cascading failures, blocked threads, slow responses,
  unbounded result sets, unbalanced capacities) and PATTERNS (timeout, circuit
  breaker, bulkhead, steady state, fail fast, shed load, backpressure, let it
  crash, handshake). Systems fail at integration points — stabilize those.

## 1. Antipattern hunt (map each to your graph)

- Unbounded result sets: any node loading a full list/keyspace with no limit
  (this kills memory AND downstream time). Cap, paginate, or filter at source.
- Slow responses with no timeout: HTTP/Calendar/API nodes waiting forever hold
  a worker slot each — under load this is a self-denial attack.
- Chain reactions: lane A fails → router retries → alert storm → Telegram rate
  limit → everything red. One fault becomes five.
- Unbalanced capacities: fast trigger (every 2 min) feeding slow lanes with no
  queue in the middle. Backlog grows until the crash.
- Missing bulkheads: unlimited concurrency lets one hot workflow starve all
  others on shared workers.

## 2. Pattern mapping (n8n concrete)

- Timeout: explicit timeout on every network node; slow dependency gets a
  ceiling, never a blank cheque.
- Circuit breaker: health-probe nodes (Redis/Calendar ping) feeding If-gates
  that SKIP dependent lanes while red and alert once (marker key prevents
  alert storms). Half-open: re-probe on a cadence, resume automatically.
- Bulkhead: `N8N_CONCURRENCY_PRODUCTION_LIMIT` per worker + queue mode so one
  hot graph cannot sink the fleet. Separate workers for heavy lanes if needed.
- Fail fast: validate inputs at the seam entry (If-gate); reject garbage in
  milliseconds instead of failing expensively ten nodes later.
- Shed load: route-early If discards invalid/low-value payloads BEFORE costly
  AI/API calls. Under overload, degrade (skip offers lane) rather than die.
- Backpressure: Split In Batches with limited batch size; the producer waits
  for the consumer instead of flooding memory.
- Steady state: define normal (executions/hour, p95 latency, heap) and alert
  on drift from it — catches degradation before users do.

## 3. Credit-what-works note (eng-router, read-only 2026-09-19)

The graph ALREADY implements fragments: Redis/Calendar probes + alert markers
(circuit-breaker skeleton), retryOnFail on Redis nodes, route-early time gates.
Gaps: unbounded key listing (antipattern 1), no explicit timeouts visible, no
bulkhead evidence. Fix order: cap the listing, add timeouts, then consider
structural surgery.

## Verification

Chaos-lite proof: slow one dependency (or replay the spike input), confirm
lanes degrade independently, alerts fire once, recovery is automatic, heap
returns to steady state. Record steady-state numbers in the runbook.
