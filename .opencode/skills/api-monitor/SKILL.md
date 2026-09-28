---
name: api-monitor
description: "External API monitor skill (shape/latency/version probes, first-deviation findings). Use when a provider may have changed, when latency creeps, or when version pins need a watcher. Trigger phrases: 'API changed', 'provider watch', 'contract deviation', 'مراقبة API'."
---

# API Monitor (Providers Move; Catch It First)

Code: `api_monitor.py` (stdlib only; probes do the calls). `watch()`
pins expected keys, latency ceiling, known errors, version; `check()`
runs the probe and files a finding on first deviation (shape loss,
latency, version, unknown status, probe crash); green runs refresh
the last-green stamp.

## Verification

- `tests/test_p2a_drift_monitor.py` monitor half green (green run,
  shape finding, unknown status, unwatched api).
- Findings carry before/after evidence, not just alerts.

## Pairs with

`contract-testing` (CI side), `health-probes` (pre-flight side),
`slo-engine` (burn source), `build-gates-pipeline`.
