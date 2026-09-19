---
name: api-security-owasp-top10
description: "API security OWASP Top 10 testing distilled. Use when testing broken object auth, excessive data, rate limits, mass assignment, SSRF in APIs."
---

# API Security OWASP Top 10

## Purpose

Test APIs against the OWASP API Top 10: object-level auth, function-level auth, excessive data, limits, mass assignment, misconfig, SSRF.

## When to use

Use when the user says 'API security', 'OWASP API', 'BOLA', 'broken object auth', 'excessive data exposure', 'mass assignment', 'API rate limit'.

## Steps

1. Probe object access: user A requests user B resources directly.
2. Probe function access: low roles call admin endpoints.
3. Check data minimization: responses carry only needed fields.
4. Test limits: burst calls must throttle, not topple.
5. Review mass assignment: read-only fields rejected on write.

## Anti-patterns

- IDs trusted from the client without ownership checks.
- Admin endpoints hidden but not authorized.
- Full objects returned while UI shows three fields.
- No throttle on auth and search endpoints.

## Example

Python:

```python
r = get("/api/users/2/orders", as_user=1)
assert r.status_code == 403  # BOLA blocked
```

## Verification

Ownership enforced per object, roles enforced per function, payloads minimized, limits proven.

## Pairs-with

security-testing-owasp-fuzz, auth-session-testing, injection-testing-patterns, api-testing-contract-patterns.
