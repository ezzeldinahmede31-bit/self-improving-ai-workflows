---
name: spike-breakpoint-testing
description: "Spike and breakpoint testing distilled. Use when finding breaking points, sudden surges, recovery behavior, autoscaling limits, backpressure."
---

# Spike Breakpoint Testing

## Purpose

Find where the system breaks and how it recovers: sudden surges past capacity, breakpoint identification, graceful versus cascading failure.

## When to use

Use when the user says 'spike test', 'breakpoint', 'breaking point', 'surge test', 'autoscale test', 'recovery test'.

## Steps

1. Ramp sharply past expected peak to locate the breakpoint.
2. Record which component saturates first with its signal.
3. Verify failure mode: shed load gracefully, never cascade silently.
4. Drop load and measure recovery time to healthy signals.
5. Harden the first bottleneck, then re-probe for the next one.

## Anti-patterns

- Ramping so slowly the test becomes a load test instead.
- Breaking shared environments without notice.
- No recovery measurement after the spike.
- Fixing symptoms (bigger boxes) without finding the saturating component.

## Example

k6 spike sketch:

```js
export const options = { stages: [{ duration: '1m', target: 500 }, { duration: '2m', target: 0 }] };
```

## Verification

Breakpoint named with signal, failure mode graceful, recovery timed, next bottleneck queued.

## Pairs-with

performance-testing-k6-jmeter, chaos-testing-patterns, capacity-planning-slo, queueing-theory-performance.
