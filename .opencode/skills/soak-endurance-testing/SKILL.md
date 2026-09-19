---
name: soak-endurance-testing
description: "Soak and endurance testing distilled. Use when detecting leaks, slow degradation, long-run stability, memory growth, connection exhaustion."
---

# Soak Endurance Testing

## Purpose

Catch what short tests miss: leaks and slow degradation under sustained realistic load across extended run windows.

## When to use

Use when the user says 'soak test', 'endurance test', 'memory leak', 'long run', 'degradation', 'connection leak'.

## Steps

1. Run realistic load steadily across an extended window (hours, then overnight).
2. Track memory, handles, pool usage, and latency trends over time.
3. Compare start versus end snapshots; flat lines are the pass signal.
4. Investigate any upward trend as a leak until proven otherwise.
5. Gate releases when trends break historical baselines.

## Anti-patterns

- Short bursts claimed as soak coverage.
- Watching only latency while memory climbs.
- Changing code mid-run and keeping the results.
- No baseline, so every trend looks either fine or alarming.

## Example

k6 soak sketch:

```js
export const options = { vus: 30, duration: '4h', thresholds: { http_req_failed: ['rate<0.01'] } };
```

## Verification

Extended run completed, trend lines flat, baselines stored, leaks filed with evidence.

## Pairs-with

performance-testing-k6-jmeter, observability-test-telemetry, database-performance-testing, capacity-planning-slo.
