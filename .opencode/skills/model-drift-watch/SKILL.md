---
name: model-drift-watch
description: "Model drift watch skill (pinned baselines, windowed verdicts, fallback/rollback actions). Use when a provider may have changed behavior, when success rates slip, or when a rollback decision needs a number. Trigger phrases: 'drift detected', 'model changed', 'success rate drop', 'انحراف النموذج'."
---

# Model Drift Watch (Catch Silent Changes)

Code: `model_drift.py` (stdlib only). Pin per-metric baselines with
absolute + relative bands and a direction (both/drop/rise); observe a
bounded window; `check()` returns ok / warming / drifted with a
fallback-or-rollback action scaled by magnitude.

## Verification

- `tests/test_p1a_bench_drift.py` drift half green (trip + action,
  warming, direction filter).
- Alerts carry baseline vs current values, never vibes.

## Pairs with

`model-benchmark-harness` (baseline source), `model_failover.py`
(fallback arm), `observability.py` (alert sink), `build-gates-pipeline`.
