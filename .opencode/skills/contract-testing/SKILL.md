---
name: contract-testing
description: "Contract testing skill (pinned input/output schemas, error taxonomy, latency ceiling, version pin). Use when an integration may have moved under you, when a provider change must break CI first, or when replay probes need shape checks. Trigger phrases: 'contract test', 'provider changed', 'pin the API', 'اختبار العقد'."
---

# Contract Testing (Catch Provider Moves in CI)

Code: `contract_test.py` (stdlib only, separate JSON store).
`declare()` pins input/output schemas, error set, timeout, auth,
version; `verify()` runs a live-or-replay probe and names breaches
(shape, unknown error, latency, version drift).

## Verification

- `tests/test_p2a_contract_schema.py` contract half green (green +
  five breach classes + persistence).
- Every external integration owns a contract; version drift pages.

## Pairs with

`api-monitor` (runtime side), `n8n-e2e-test-runner` (live path),
`deploy-signoff-governance`, `build-gates-pipeline`.
