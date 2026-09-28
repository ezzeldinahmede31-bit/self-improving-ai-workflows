---
name: chaos-drills
description: "Chaos and disaster drill skill (12-fault catalog with inject/assert/recover, restore-to-smoke with RPO/RTO). Use when proving recovery, when a backup has never been restored, or when an unregistered fault must be flagged unproven. Trigger phrases: 'chaos drill', 'restore drill', 'prove recovery', 'تدريب الكوارث'."
---

# Chaos Drills (Prove Recovery, Not Backups)

Code: `chaos_drills.py` (stdlib only, caller-injected faults — safe by
construction). 12-fault catalog (dead redis/postgres/n8n/LLM, timeout,
partition, expired cred, dead worker, dup webhook, bad payload, clock
drift, full disk): inject → assert degraded-safe → recover → assert
healthy. `coverage()` names unregistered faults as unproven.
`DisasterDrill` runs restore-db/creds/workflows/config → smoke with
RTO stamp; missing steps fail loudly.

## Verification

- `tests/test_p1b_idem_chaos.py` chaos half green (full cycle,
  unregistered drill, disaster ready/unready).
- No "production ready" claim without a green drill record.

## Pairs with

`n8n-deployment-ops-guard`, `deploy-signoff-governance`,
`sre-incident-response`, `build-gates-pipeline`.
