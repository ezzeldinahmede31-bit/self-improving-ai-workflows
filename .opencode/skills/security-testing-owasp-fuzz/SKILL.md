---
name: security-testing-owasp-fuzz
description: "Security testing distilled. Use when threat modeling test abuse cases, OWASP checks, fuzzing inputs, injection, auth bypass, security regression."
---

# Security Testing (OWASP + Fuzz)

## Purpose

Test like an attacker within authorized scope: abuse cases, OWASP Top 10 checks, input fuzzing, auth/session verification.

## When to use

Use when the user says 'security testing', 'OWASP', 'fuzzing', 'injection', 'XSS', 'auth bypass', 'penetration test', 'abuse case'.

## Steps

1. Model abuse cases per feature (what should never happen).
2. Run OWASP checks: injection, broken auth, sensitive exposure, access control, SSRF.
3. Fuzz boundaries: empty, huge, unicode, type-confusion payloads (use zeller-fuzzing-book engines where deep).
4. Verify session handling: expiry, rotation, least privilege, direct-object-reference guards.
5. File security defects with impact + reproduction + safe remediation hint.

## Anti-patterns

- Testing production without written authorization.
- Only scanner output with no manual abuse-case reasoning.
- Storing real credentials in test scripts.
- Marking security flakes as noise.

## Example

Python fuzz probe:

```python
for payload in ["' OR '1'='1", "<script>alert(1)</script>", "A" * 10000]:
    r = requests.post(f"{BASE}/search", json={"q": payload}, timeout=10)
    assert r.status_code in (200, 400) and "traceback" not in r.text.lower()
```

## Verification

Abuse cases listed, OWASP checklist signed, fuzz corpus run, auth matrix verified, findings reproducible.

## Pairs-with

security-review, security-and-hardening, zeller-fuzzing-book, frontier-red-team-auditor.
