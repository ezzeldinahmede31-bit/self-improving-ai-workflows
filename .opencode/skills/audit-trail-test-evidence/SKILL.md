---
name: audit-trail-test-evidence
description: "Audit trail test evidence distilled. Use when recording test evidence, immutable logs, sign-off chains, traceability for auditors."
---

# Audit Trail Test Evidence

## Purpose

Make testing auditable: immutable run records, sign-off chains, requirement traceability, tamper-evident evidence stores.

## When to use

Use when the user says 'audit trail', 'test evidence', 'sign-off chain', 'traceability matrix', 'immutable logs', 'auditor evidence'.

## Steps

1. Record every qualifying run immutably: scope, version, results, signals.
2. Chain sign-offs with identity plus timestamp plus decision.
3. Maintain traceability from requirement through test to run.
4. Store evidence where it cannot be silently edited.
5. Rehearse auditor walkthroughs before the real ones.

## Anti-patterns

- Results in editable docs with no history.
- Sign-offs collected verbally.
- Traceability reconstructed under audit pressure.
- Evidence scattered across personal drives.

## Example

Evidence record: run id, code version, scope link, results link, signers, timestamps, store receipt.

## Verification

Runs immutable, sign-offs chained, traceability live, walkthroughs rehearsed.

## Pairs-with

compliance-testing-patterns, audit-trail-compliance, test-documentation-living, release-readiness-gates.
