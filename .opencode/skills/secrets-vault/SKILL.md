---
name: secrets-vault
description: "Short-lived secrets vault skill (scoped leases, single-use option, revoke/rotate, access log). Use when an agent needs a credential for one job, when a lease must die after use or on incident, or when credential access needs an audit trail. Trigger phrases: 'issue a lease', 'short-lived credential', 'revoke lease', 'تصريح مؤقت'."
---

# Secrets Vault (Leases, Not Loans)

Code: `secrets_vault.py` (stdlib only). Agents never hold long-lived
credentials: `issue(scope, ttl_s, max_uses)` returns a raw token ONCE
(only sha256 stored). `redeem(token, operation)` checks scope, expiry,
use budget, revocation. `revoke(id)` kills instantly; `rotate(id)`
replaces same-scope; `sweep_expired()` purges dead leases;
`events()` exposes the access log (plus optional JSONL sink).

## When to use

- One-job credentials (single-use default: 1).
- Incident response: revoke, then rotate survivors.
- Any flow where a credential's lifetime must be provable.

## Steps

1. One `Vault` per trust domain (optional `log_path` for durability).
2. Issue tight scope + short TTL; redeem per operation.
3. Revoke on task end; sweep on a schedule; ship the event log with
   incident evidence.

## Verification

- `tests/test_p0a_vault.py` green (single-use, scope wall, unknown
  token, revoke/rotate, expiry sweep, raw-never-stored, log).
- `repr(vault)` and logs never contain a raw token (test asserts it).

## Pairs with

`capability-tokens` (grant layer), `credential-secret-handling`,
`secret-scanning-lifecycle-adapter`, `build-gates-pipeline`.
