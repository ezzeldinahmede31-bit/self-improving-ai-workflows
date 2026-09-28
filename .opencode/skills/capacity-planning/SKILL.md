---
name: capacity-planning
description: "Capacity planning skill (fleet snapshots, green/tight/over headroom, first-breaker forecast). Use when asking if today handles 10x, when naming the binding resource, or when latency growth needs a number. Trigger phrases: 'headroom check', 'forecast load', 'binding resource', 'تخطيط السعة'."
---

# Capacity Planning (Numbers Before Hope)

Code: `capacity.py` (stdlib only; callers sample the OS). `snapshot()`
records workers/in-flight/queue/CPU/RAM/API headroom; `headroom()`
verdicts green/tight/over with the binding resource; `forecast()`
scales by a multiple and names the first breaker plus an approximate
latency multiplier (labeled approximate, M/M/1 shape).

## Verification

- `tests/test_p1d_capacity_health.py` capacity half green (headroom,
  forecast, bad fractions, empty store).
- Scaling decisions cite the binding resource + multiple.

## Pairs with

`deployment-controller` (scale/shift arm), `slo-engine` (target
source), `observability.py` (metric source), `build-gates-pipeline`.
