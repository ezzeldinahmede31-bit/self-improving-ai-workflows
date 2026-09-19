---
name: dast-sast-integration
description: "DAST and SAST integration distilled. Use when wiring static and dynamic scanners into CI, triage rules, baseline management, quality gates."
---

# DAST SAST Integration

## Purpose

Wire static and dynamic analysis into delivery: SAST on code, DAST on running apps, triaged findings, baselines, gated releases.

## When to use

Use when the user says 'SAST', 'DAST', 'static analysis', 'dynamic scan', 'Semgrep', 'CodeQL', 'OWASP ZAP', 'scanner CI'.

## Steps

1. Run SAST per pull request on changed code with tuned rules.
2. Run DAST against ephemeral preview environments per release.
3. Triage with owners; suppress only with expiry plus reason.
4. Baseline legacy findings; fail only on new issues first.
5. Gate promotion on critical findings, never on raw warning volume.

## Anti-patterns

- Default rule sets flooding teams into ignoring all output.
- Permanent suppressions with no reason or expiry.
- DAST against production without authorization.
- Scanner green claimed while triage queue rots.

## Example

CI sketch:

```yaml
- run: semgrep ci
- run: zap-baseline.py -t https://preview-$PR.example.com
```

## Verification

Rules tuned, triage owned, baselines versioned, promotion gated on criticals.

## Pairs-with

security-review, injection-testing-patterns, secrets-scan-testing, compliance-testing-patterns.
