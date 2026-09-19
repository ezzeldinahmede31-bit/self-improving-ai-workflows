---
name: secrets-scan-testing
description: "Secrets scanning testing distilled. Use when preventing leaked credentials, pre-commit hooks, vault references, rotation drills, audit."
---

# Secrets Scan Testing

## Purpose

Keep secrets out of code and logs: pre-commit scanning, CI gates, vault-referenced config, rotation rehearsal, leak response drills.

## When to use

Use when the user says 'secrets scan', 'leaked credential', 'pre-commit hook', 'vault', 'rotation drill', 'gitleaks', 'truffleHog'.

## Steps

1. Scan pre-commit and in CI with maintained rule sets.
2. Reference secrets from vault or env at runtime, never in files.
3. Fail builds on new findings; triage legacy findings with owners.
4. Rehearse rotation: revoke, replace, verify, all without downtime.
5. Drill leak response: scope, revoke, rotate, notify per policy.

## Anti-patterns

- Secrets in tracked config or test fixtures.
- Scanner allow-lists hiding real findings.
- Rotation that has never been rehearsed.
- Logs echoing headers and connection strings.

## Example

CI gate sketch:

```yaml
- run: gitleaks detect --no-git -v
```

Plus a test asserting no fixture file matches secret patterns.

## Verification

Scans green pre-commit plus CI, runtime references only, rotation rehearsed, response drilled.

## Pairs-with

credential-secret-handling, n8n-credential-security-guard, dast-sast-integration, audit-trail-test-evidence.
