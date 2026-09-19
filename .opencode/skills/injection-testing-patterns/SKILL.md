---
name: injection-testing-patterns
description: "Injection testing patterns distilled. Use when testing SQLi, command injection, LDAP, XPath, template injection, ORM safety."
---

# Injection Testing Patterns

## Purpose

Prove inputs cannot become code: SQL, OS command, LDAP, XPath, and template injection coverage with parameterized-safe baselines.

## When to use

Use when the user says 'SQL injection', 'command injection', 'LDAP injection', 'SSTI', 'XPath injection', 'injection test'.

## Steps

1. Baseline: all queries parameterized or ORM-bound, commands allow-listed.
2. Fire classic payloads per sink and assert neutralization.
3. Test second-order paths: stored input executed later.
4. Review error messages for leakage (stack, dialect, paths).
5. Re-run payload suites on every query or sink change.

## Anti-patterns

- String-built queries with partial escaping.
- Errors returning stack traces to callers.
- Client-side validation as the only defense.
- ORM raw() fragments with interpolated values.

## Example

Python:

```python
r = search("' OR '1'='1")
assert "traceback" not in r.text.lower()
assert r.status_code in (200, 400)
```

## Verification

Payload suites green, errors generic, sinks parameterized, second-order paths covered.

## Pairs-with

security-testing-owasp-fuzz, ssrf-ssti-testing, dast-sast-integration, validation-gate-data-quality.
