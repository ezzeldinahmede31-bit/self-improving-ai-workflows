---
name: dependency-drift-watch
description: "Dependency drift watch skill (pinned baseline, classified diffs, retest verdicts). Use when packages or images moved, when a major bump needs rescan+retest, or when an unknown addition appears. Trigger phrases: 'dep drift', 'package moved', 'retest demand', 'انحراف الاعتماديات'."
---

# Dependency Drift Watch (Moved Deps Must Re-Prove)

Code: `dep_drift.py` (stdlib only; consumes SBOM shape). `pin()`
freezes versions + image digests; `check()` classifies added/removed/
upgraded/downgraded/images; `verdict()` demands rescan+retest+review
on major moves, removals, additions, image swaps (log-only otherwise).

## Verification

- `tests/test_p2a_drift_monitor.py` drift half green (classify,
  verdict ladder, major bump, removal).
- CI diffs SBOM per change; security-relevant moves block merge.

## Pairs with

`supply-chain-security` (SBOM source), `secret-scanning-lifecycle-adapter`,
`deploy-signoff-governance`, `build-gates-pipeline`.
