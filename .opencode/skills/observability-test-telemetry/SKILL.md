---
name: observability-test-telemetry
description: "Test telemetry and observability distilled. Use when asserting logs, metrics, traces in tests, SLO signals, alert drills, test-owned dashboards."
---

# Observability Test Telemetry

## Purpose

Test what you operate: assert logs, metrics, and traces inside tests; drill alerts; keep test-owned dashboards proving health.

## When to use

Use when the user says 'observability test', 'assert metrics', 'trace test', 'alert drill', 'telemetry', 'SLO test'.

## Steps

1. Assert key business events emit structured logs with correlation ids.
2. Assert metrics move (counters, histograms) on the paths under test.
3. Verify traces connect frontend action to backend spans.
4. Drill alerts against staged failures; confirm pages route correctly.
5. Keep a test-owned dashboard showing suite health plus flake trends.

## Anti-patterns

- Logs asserted as raw strings instead of structured fields.
- Metrics tested nowhere, then missing during incidents.
- Alerts never fired before the real outage.
- Trace sampling dropping exactly the failing paths.

## Example

Python:

```python
checkout()
assert metric_delta("checkout_completed_total") == 1
assert last_span("payment.charge").status == "ok"
```

## Verification

Structured events asserted, metric deltas checked, traces linked, alert drills passing.

## Pairs-with

observability-execution-monitoring, capacity-planning-slo, quality-metrics-dashboard, sre-workbook.
