---
name: immutable-audit-log
description: "Immutable audit log skill (append-only hash-chained SQLite events, optional HMAC, replay verification). Use when recording deployments, approvals, rotations, or incidents, or when proving a log is intact. Trigger phrases: 'audit this event', 'verify the chain', 'tamper check', 'سجل غير قابل للتعديل'."
---

# Immutable Audit Log (Prove What Happened)

Code: `immutable_audit.py` (stdlib sqlite3). Dedicated store
(`audit_chain.db` — the existing audit.db schema is never migrated by
this subsystem). Each event: timestamp, kind, actor, subject, detail,
previous hash, own hash, optional HMAC. `append()` returns id + hash;
`verify()` replays and names the first break; `tail()` serves
dashboards. No update/delete API exists — correction is a superseding
append.

## When to use

- Deployments, approvals, denials, rotations, revocations, incidents.
- Compliance evidence: export + `verify()` output archived together.
- Scheduled integrity sweeps (alert on first break, preserve the file).

## Verification

- `tests/test_p0b_audit.py` green (append/verify, forgery trap,
  deletion trap, tail view, no-mutator API).
- A broken chain blocks dependent claims until re-anchored by a human.

## Pairs with

`provenance-lineage` (why it happened), `deploy-signoff-governance`,
`agent-control-plane-adapter` (verdict source), `build-gates-pipeline`.
