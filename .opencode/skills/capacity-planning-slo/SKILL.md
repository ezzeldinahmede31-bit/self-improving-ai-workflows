---
name: capacity-planning-slo
description: "Capacity planning with SLOs distilled. Use when sizing systems, headroom policy, error budgets, growth forecasts, saturation alerts."
---

# Capacity Planning With SLOs

## Purpose

Size systems from evidence: SLOs define good, error budgets pace risk, forecasts plus headroom policy decide when to scale.

## When to use

Use when the user says 'capacity planning', 'headroom', 'error budget', 'SLO', 'growth forecast', 'sizing', 'saturation'.

## Steps

1. Define SLOs on user-visible outcomes with explicit windows.
2. Derive error budget policy: who ships, who freezes, at which burn rate.
3. Forecast demand from growth plus seasonal peaks.
4. Hold headroom against the forecast; alert on saturation trends early.
5. Review quarterly: SLOs, budgets, and headroom against reality.

## Anti-patterns

- SLOs nobody reads while pages fire on raw CPU.
- Error budget with no freeze policy attached.
- Planning from peak provision instead of measured demand.
- Headroom consumed silently by adjacent tenants.

## Example

Policy: "Burn above 2x baseline pace freezes non-urgent deploys until budget recovers."

## Verification

SLOs versioned, budget policy enforced, forecast documented, saturation alerts precede incidents.

## Pairs-with

sre-workbook, performance-testing-k6-jmeter, observability-test-telemetry, queueing-theory-performance.
