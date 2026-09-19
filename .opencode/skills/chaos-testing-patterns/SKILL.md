---
name: chaos-testing-patterns
description: "Chaos testing patterns distilled. Use when injecting failures, game days, blast radius control, steady-state hypothesis, rollback drills."
---

# Chaos Testing Patterns

## Purpose

Prove resilience by injecting controlled failure: hypothesis first, small blast radius, steady-state comparison, automatic halt on surprise.

## When to use

Use when the user says 'chaos testing', 'chaos engineering', 'game day', 'fault injection', 'blast radius', 'steady state'.

## Steps

1. Define steady state with measurable signals before injecting anything.
2. Form a hypothesis: what should stay healthy during this fault.
3. Start tiny: one pod, one zone, short duration; expand on success.
4. Halt automatically when signals leave guardrails.
5. Turn each surprise into a regression test plus a runbook update.

## Anti-patterns

- Chaos in production without guardrails and ownership.
- Injecting faults with no steady-state definition.
- Huge blast radius on the first experiment.
- Findings that never become regression coverage.

## Example

Hypothesis card: "Killing one payment pod keeps checkout success above SLO while latency stays flat."

## Verification

Hypothesis recorded, guardrails enforced, blast radius minimal-first, findings converted to tests.

## Pairs-with

resilience-circuit-testing, spike-breakpoint-testing, observability-test-telemetry, sre-workbook.
