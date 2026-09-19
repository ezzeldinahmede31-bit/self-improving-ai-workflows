---
name: penetration-test-planning
description: "Penetration test planning distilled. Use when scoping pentests, rules of engagement, evidence handling, remediation verification, retests."
---

# Penetration Test Planning

## Purpose

Get value from pentests: crisp scope, rules of engagement, evidence-grade findings, tracked remediation, verified retests.

## When to use

Use when the user says 'pentest', 'penetration test scope', 'rules of engagement', 'remediation', 'retest', 'red team'.

## Steps

1. Scope targets, accounts, data classes, and off-limits systems in writing.
2. Set rules of engagement: windows, contacts, stop conditions.
3. Require evidence-grade findings: reproduction, impact, affected scope.
4. Track remediation per finding with owners plus due dates.
5. Verify with retests; close only on proof, never on promise.

## Anti-patterns

- Vague scope inviting out-of-bounds testing.
- Findings without reproduction steps.
- Remediation tracked in chat threads.
- Closure without retest evidence.

## Example

Finding record: title, severity, reproduction, impact, scope, owner, due date, retest proof.

## Verification

Scope signed, findings reproducible, remediation tracked, retests evidenced.

## Pairs-with

frontier-red-team-auditor, security-review, auth-session-testing, api-security-owasp-top10.
