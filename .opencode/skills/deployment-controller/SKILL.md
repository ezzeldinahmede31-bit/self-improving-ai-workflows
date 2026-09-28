---
name: deployment-controller
description: "Deployment controller skill (1-10-50-100 canary, probe gates, automatic rollback, percentage flags). Use when releasing any workflow/agent version, when a probe breach must revert traffic, or when a flag needs stable per-identity buckets. Trigger phrases: 'canary release', 'auto rollback', 'feature flag', 'إطلاق تدريجي'."
---

# Deployment Controller (Roll Forward, Roll Back Automatically)

Code: `deployment.py` (stdlib only). `FeatureFlags` buckets by stable
identity hash (same identity, same bucket, always). `rollout()`
advances 1→10→50→100 while stage probes pass (error/latency/tool/
cost windows); first breach halts and pins traffic to the previous
version; missing probes halt loudly (never assumed green).

## Verification

- `tests/test_p1c_deploy_trace.py` deployment half green (buckets,
  advance-then-rollback, full green, missing probe).
- No release without probes per stage; rollback path drilled.

## Pairs with

`chaos-drills` (pre-release proof), `deploy-signoff-governance`
(authorization), `slo-engine` (probe source), `build-gates-pipeline`.
