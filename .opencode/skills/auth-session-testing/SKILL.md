---
name: auth-session-testing
description: "Auth and session testing distilled. Use when testing login, MFA, session fixation, expiry, privilege escalation, OAuth flows."
---

# Auth Session Testing

## Purpose

Prove identity handling: credential flows, MFA, session lifecycle, fixation resistance, privilege boundaries, OAuth correctness.

## When to use

Use when the user says 'auth test', 'session test', 'login test', 'MFA', 'session fixation', 'privilege escalation', 'OAuth test'.

## Steps

1. Test credential flows: valid, invalid, locked, expired credentials.
2. Verify MFA cannot be skipped by direct navigation.
3. Check sessions rotate on login and expire on logout plus timeout.
4. Attempt vertical and horizontal privilege escalation.
5. Validate OAuth redirect URIs, scopes, and code single-use.

## Anti-patterns

- Session ids in URLs or logs.
- Fixation: pre-login session surviving authentication.
- MFA enforced in UI only.
- Wildcard redirect URIs in OAuth clients.

## Example

Python:

```python
sid_before = session_id()
login()
assert session_id() != sid_before  # rotation proven
```

## Verification

Rotation plus expiry proven, escalation blocked, MFA unbypassable, OAuth strict.

## Pairs-with

api-security-owasp-top10, security-testing-owasp-fuzz, xss-csrf-testing, penetration-test-planning.
