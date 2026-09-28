---
name: spec-docs-drift
description: "Spec and docs drift skill (pinned promises vs live probes, code symbols vs doc mentions). Use when behavior may have moved silently, when docs name missing symbols, or when symbols lack docs. Trigger phrases: 'spec drift', 'docs drift', 'promise moved', 'انحراف المواصفة'."
---

# Spec + Docs Drift (Promises Match Reality)

Code: `spec_drift.py` (stdlib only, ast for code side). `SpecDrift`
pins statement hashes, binds behavior probes, and files findings when
observed text moves (reminder 24h → 12h is the canonical trip);
`DocsDrift` reports undocumented symbols AND phantom doc names (neither
direction trusted blindly).

## Verification

- `tests/test_p2b_advanced_spec.py` drift third green (pin/move,
  both directions, broken syntax safe).
- Drift findings carry pinned-vs-observed evidence.

## Pairs with

`traceability-links` (promise registry), `provenance-lineage`
(change chain), `test-documentation-living`, `build-gates-pipeline`.
