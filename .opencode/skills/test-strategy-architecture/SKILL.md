---
name: test-strategy-architecture
description: "Test strategy architecture distilled. Use when defining quality strategy, test pyramid, portfolio balance, tooling choices, team ownership."
---

# Test Strategy Architecture

## Purpose

Set quality direction: pyramid balance, portfolio across levels, tooling standards, ownership, all tied to product risk.

## When to use

Use when the user says 'test strategy', 'test pyramid', 'quality strategy', 'test portfolio', 'tooling standard', 'QA ownership'.

## Steps

1. Anchor strategy in product risks, not tool preferences.
2. Balance the pyramid: many fast unit checks, fewer service tests, thin UI slice.
3. Standardize tooling per layer with escape hatches documented.
4. Assign ownership per area with review rotation.
5. Review strategy quarterly against escaped defects.

## Anti-patterns

- Inverted pyramid: heavy UI suites with thin unit coverage.
- Tool sprawl with no standard per layer.
- Strategy as a static document nobody revisits.
- Ownership by naming nobody accountable.

## Example

Portfolio sketch: unit (fast, per commit) / service (contract plus flows, per PR) / UI (critical journeys, nightly).

## Verification

Pyramid ratios tracked, standards documented, owners named, reviews scheduled from escape data.

## Pairs-with

crispin-agile-testing, black-risk-based-testing, risk-based-prioritization, quality-metrics-dashboard.
