---
name: performance-testing-k6-jmeter
description: "Performance testing with k6 and JMeter distilled. Use when load testing, stress testing, SLOs, percentiles, throughput, saturation, capacity planning."
---

# Performance Testing (k6 + JMeter)

## Purpose

Prove performance with numbers: workloads, percentiles, throughput, saturation, SLOs, using k6 (code) or JMeter (enterprise plans).

## When to use

Use when the user says 'load test', 'stress test', 'k6', 'JMeter', 'p95', 'throughput', 'SLO', 'capacity', 'performance'.

## Steps

1. Define SLOs first: p95 latency, error budget, target RPS.
2. Model workload: virtual users, ramp, steady, spike shapes.
3. Measure p50/p95/p99 + throughput + errors + saturation (CPU, DB pool).
4. Find the knee: raise load until latency bends; record max goodput.
5. Gate releases on SLOs; store baselines for regression.

## Anti-patterns

- Testing from a laptop against production.
- Averages only (hides tail latency).
- No warmup or steady-state window.
- Ignoring downstream saturation (DB, queues).

## Example

k6 (JS):

```js
export const options = { vus: 50, duration: '2m', thresholds: { http_req_duration: ['p(95)<500'] } };
export default function () { http.get(`${__ENV.BASE}/api/orders`); }
```

## Verification

SLO thresholds enforced, p95 reported, bottleneck named with saturation metric, baseline stored.

## Pairs-with

systems-performance-profiling, queueing-theory-performance, sre-workbook, observability-execution-monitoring.
