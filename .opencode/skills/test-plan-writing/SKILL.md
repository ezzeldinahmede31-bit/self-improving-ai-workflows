---
name: test-plan-writing
description: "Test plan writing distilled. Use when writing test plans, scope, entry and exit rules, schedule, risks, deliverables."
---

# Test Plan Writing

## Purpose

Write test plans that steer work: scope, approach per level, entry plus exit rules, schedule, risks, deliverables.

## When to use

Use when the user says 'test plan', 'test scope', 'entry criteria', 'exit criteria', 'test schedule', 'test deliverables'.

## Steps

1. Define scope in and out with references to requirements.
2. Choose approach per level: techniques, tools, data needs.
3. Set entry rules (ready to start) plus exit rules (ready to ship).
4. Schedule with milestones tied to builds, not dates alone.
5. List risks with mitigations and owners.

## Anti-patterns

- Plans copied across releases with stale scope.
- Exit by calendar with no quality bar.
- Risks listed without owners or mitigations.
- Deliverables nobody consumes.

## Example

Exit rules sketch: all critical tests green, no open blockers, performance SLOs met, security gates passed.

## Verification

Scope current, entry plus exit rules measurable, risks owned, deliverables consumed.

## Pairs-with

graham-istqb-foundations, test-strategy-architecture, release-readiness-gates, risk-based-prioritization.
