---
name: slo-engine
description: "SLO engine skill (declared targets, windowed ok/at-risk/breached verdicts, burn evidence). Use when a service needs availability/latency targets, when burn must page with numbers, or when 'it works' needs a measured definition. Trigger phrases: 'SLO check', 'burn alert', 'error budget', 'أهداف الخدمة'."
---

# SLO Engine (Targets the System Watches Itself)

Code: `slo.py` (stdlib only). `add_target()` declares op (>=/<=)
and kind (rate/p95/avg/max); `observe()` feeds windows; `evaluate()`
returns ok / at-risk (within 10% of edge) / breached / warming with
observed vs threshold values.

## Verification

- `tests/test_p1d_slo_cost.py` SLO half green (breach, at-risk band,
  warming, unknown).
- Alerts cite target + window + observed value.

## Pairs with

`distributed-tracing` (latency source), `deployment-controller`
(probe source), `observability.py` (alert sink), `build-gates-pipeline`.
