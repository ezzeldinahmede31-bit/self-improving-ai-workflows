---
name: quality-metrics-dashboard
description: "Quality metrics dashboard distilled. Use when tracking escape rate, flake rate, lead time, MTTR, coverage trends, DORA quality signals."
---

# Quality Metrics Dashboard

## Purpose

 Steer quality with honest signals: escape rate, flake rate, coverage and mutation trends, lead time, recovery time, all on one dashboard.

## When to use

Use when the user says 'quality metrics', 'escape rate', 'DORA metrics', 'quality dashboard', 'MTTR', 'lead time', 'test health'.

## Steps

1. Track escaped defects per release as the headline metric.
2. Track suite health: flake rate, duration, quarantine size.
3. Track prevention: review coverage, static findings fixed, mutation trend.
4. Track flow: lead time plus recovery time alongside quality.
5. Review monthly with owners; attach actions to every red signal.

## Anti-patterns

- Vanity metrics (raw test totals) steering nothing.
- Dashboards nobody opens during planning.
- Metrics without owners or actions.
- Gaming signals by deleting tests instead of fixing causes.

## Example

Dashboard rows: escapes per release / flake rate / p95 suite duration / mutation trend / MTTR.

## Verification

Dashboard live, owners assigned, red signals actioned, trends reviewed on cadence.

## Pairs-with

accelerate-dora-metrics, flaky-test-elimination, defect-triage-rootcause, release-readiness-gates.
