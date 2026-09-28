---
name: capability-tokens
description: "Capability-token skill (scoped expiring revocable grants, HMAC-signed, attenuate-only descent). Use when an agent needs least-privilege access, when a grant must expire or be revoked, or when narrowing a grant for a sub-task. Trigger phrases: 'scoped grant', 'capability token', 'revoke access', 'صلاحية مؤقتة'."
---

# Capability Tokens (Least-Privilege Grants)

Code: `capability.py` (stdlib only). Replaces all-or-nothing access:
`issue(actions, resource, ttl_s)` mints an HMAC-signed token (raw shown
once; only sha256 stored). `verify(token, action, resource)` checks
signature, expiry, revocation, action scope, resource scope.
`attenuate()` mints a NARROWED child (never wider). `revoke(id)` kills
a grant instantly.

## When to use

- Grant an agent exactly the actions it needs, for minutes not months.
- Hand a sub-agent a narrowed child of your own grant.
- Revoke on incident, role change, or task end.

## Steps

1. Create one `CapabilityIssuer` per trust domain (secret 16+ bytes,
   from env/vault — never in code).
2. Issue with tight scope + short TTL; verify every call site.
3. Attenuate (never re-issue wide) for delegation; revoke on done.

## Verification

- `tests/test_p0a_capability.py` green (roundtrip, scope walls,
  tamper reject, expiry, revoke, narrow-only descent).
- Raw tokens appear nowhere in logs, stores, or memory.

## Pairs with

`policy-engine` (verdict layer), `secrets-vault` (short-lived issue),
`credential-secret-handling`, `build-gates-pipeline`.
