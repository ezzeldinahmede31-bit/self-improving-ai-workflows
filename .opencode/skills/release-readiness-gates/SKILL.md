---
name: release-readiness-gates
description: "Release readiness gating distilled. Use when deciding ship or no-ship, exit criteria, go-live checklists, rollback readiness, sign-off."
---

# Release Readiness Gates

## Purpose

Decide ship with evidence: exit criteria checked, quality signals green, rollback rehearsed, ownership signed.

## When to use

Use when the user says 'release readiness', 'go no-go', 'exit criteria', 'go-live checklist', 'sign-off', 'rollback plan'.

## Steps

1. Check exit criteria: functional, performance, security signals all green.
2. Confirm rollback path rehearsed for this exact release shape.
3. Verify observability: dashboards plus alerts live for new paths.
4. Collect sign-off from quality, security, and product owners.
5. Record the decision with evidence links for audit.

## Anti-patterns

- Ship pressure overriding red signals.
- Rollback assumed without rehearsal.
- Sign-off by chat emoji instead of recorded decision.
- Post-release verification skipped.

## Example

Gate card: criteria checklist with links to suite run, perf report, scan report, rollback drill log.

## Verification

Criteria evidenced, rollback rehearsed, sign-off recorded, decision auditable.

## Pairs-with

test-plan-writing, quality-metrics-dashboard, risk-based-prioritization, n8n-delivery-verification-gate.
