---
name: security-operations
description: "Security operations skill (5-step containment runbook, alert correlation, nightly red-team to golden cases). Use on suspected leak/injection, when alerts may be one incident, or when scheduling continuous adversarial runs. Trigger phrases: 'incident response', 'correlate alerts', 'nightly redteam', 'عمليات أمنية'."
---

# Security Operations (Contain, Correlate, Keep Testing)

Code: `incident.py` (stdlib only). `IncidentResponse` runs
kill-session → revoke-token → quarantine-workflow → alert-human →
preserve-evidence with per-action honesty (half-contained stays
visible). `correlate()` fuses 3+ distinct signals per agent/session
window into one incident (lonely alerts stay open, never dropped).
`RedTeamLoop` runs attack cycles on schedule and converts fresh
failures into golden-corpus cases (deduped by id).

## Verification

- `tests/test_p2c_incident.py` green (full/partial containment,
  fusion, golden feed).
- Runbooks name handlers; unbound steps fail loudly, never silently.

## Pairs with

`golden-corpus` (failure home), `adversarial-suite` (attack shape),
`immutable-audit-log` (evidence), `sre-incident-response`,
`build-gates-pipeline`.
