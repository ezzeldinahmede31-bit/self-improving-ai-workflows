---
name: provenance-lineage
description: "Provenance lineage skill (requirement-to-deploy link chains, gap analysis, JSONL store). Use when a delivery must show its why-chain, when a bug needs its originating decision, or when a stage gap must block delivery. Trigger phrases: 'trace this artifact', 'lineage gaps', 'why was this built', 'تتبع المصدر'."
---

# Provenance Lineage (Every Artifact Explains Itself)

Code: `provenance.py` (stdlib only). Canonical stage order:
requirement → research → decision → task → agent → model → skill →
code → workflow → test → deployment. `link()` accrues refs per stage
into append-only JSONL; `trace()` reads back in order; `gaps()`
lists required stages with zero links — gaps block delivery.

## When to use

- Delivery time: assert zero gaps on required stages first.
- Bug triage: walk the chain to the originating decision/note.
- Self-improvement: failures inherit their chain automatically.

## Verification

- `tests/test_p0b_prov_repro.py` provenance half green (order, gaps,
  bad-stage reject, persistence).
- No READY claim ships with open required-stage gaps.

## Pairs with

`immutable-audit-log` (what happened), `n8n-delivery-verification-gate`
(evidence table), `tradeoff-and-postmortem-documenter`,
`build-gates-pipeline`.
