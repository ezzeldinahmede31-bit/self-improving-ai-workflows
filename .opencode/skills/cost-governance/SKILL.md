---
name: cost-governance
description: "Cost governance skill (threshold states that degrade, disable, escalate, freeze). Use when spend must trigger model downgrades, when expensive paths need auto-kill, or when freeze must block with escalation. Trigger phrases: 'spend level', 'degrade model', 'freeze spend', 'حوكمة التكلفة'."
---

# Cost Governance (Budgets That Act)

Code: `cost_governor.py` (stdlib only; read-only toward platform
books). Ascending thresholds drive normal → watch (notify) → tight
(cheap-tier reroute) → critical (approval + kill pricey paths +
escalate) → frozen (block + escalate). Every transition journals.

## Verification

- `tests/test_p1d_slo_cost.py` governor half green (full ladder,
  bad config, status).
- No silent over-spend: every level names its actions.

## Pairs with

`multi-tenant-platform` (per-tenant caps), `model-benchmark-harness`
(cheap-tier evidence), `cost_ledger.py` (books), `build-gates-pipeline`.
