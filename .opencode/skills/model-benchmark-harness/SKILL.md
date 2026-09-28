---
name: model-benchmark-harness
description: "Model benchmark harness skill (shared task set, pass/cost/latency ranking, data-driven router pick). Use when choosing a model on evidence, when a new model must prove itself on the same tasks, or when routing by name needs replacing with routing by numbers. Trigger phrases: 'benchmark models', 'router pick', 'model comparison', 'مقارنة النماذج'."
---

# Model Benchmark Harness (Route by Numbers, Not Names)

Code: `model_bench.py` (stdlib only). Register tasks once with checker
callables (`contains`, `parses_json`, custom); `run_suite()` scores one
model (pass rate, latency, tokens, cost); `compare()` ranks many and
names the pick (pass rate first, cost/latency tie-breaks). Models are
injected callables — no vendor SDKs, no network inside the harness.

## Verification

- `tests/test_p1a_bench_drift.py` bench half green (ranking, pick,
  crash recording).
- Router config cites a dated benchmark report, never an impression.

## Pairs with

`model-drift-watch` (post-deploy), `prompt-regression-gate`,
`litellm-tier-router`, `build-gates-pipeline`.
