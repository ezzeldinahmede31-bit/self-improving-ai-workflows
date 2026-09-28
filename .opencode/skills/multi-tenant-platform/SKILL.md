---
name: multi-tenant-platform
description: "Multi-tenant platform skill (isolated namespaces, 5-state budget machine, per-tenant ledger). Use when serving many clients, when spend must degrade then escalate then block, or when cross-tenant reads must be impossible. Trigger phrases: 'tenant budget', 'tenant isolation', 'per-client spend', 'عزل العملاء'."
---

# Multi-Tenant Platform (Isolation + Budget States)

Code: `tenancy.py` (stdlib only, separate JSON store). Namespaces
isolate keys (`t:<id>:<key>`; unknown tenant raises). Budget machine:
ok → warning (notify) → degraded (cheaper model, pricey paths off) →
critical (human escalation) → exceeded (block new spend). Every move
appends to the tenant ledger.

## Verification

- `tests/test_p1c_tenancy_privacy.py` tenancy half green (full state
  walk, isolation, error paths, persistence).
- No shared keys across tenants; no spend without a state.

## Pairs with

`cost-governance` (action arm), `privacy-data-governance` (per-tenant
data), `cost_ledger.py` (platform rollup), `build-gates-pipeline`.
