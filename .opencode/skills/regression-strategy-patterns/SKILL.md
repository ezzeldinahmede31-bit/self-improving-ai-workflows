---
name: regression-strategy-patterns
description: "Regression strategy patterns distilled. Use when selecting regression suites, impact-based selection, smoke versus full, suite pruning."
---

# Regression Strategy Patterns

## Purpose

Keep regression fast and trusted: impact-based selection per change, layered smoke plus full suites, pruning of redundant cases.

## When to use

Use when the user says 'regression suite', 'regression strategy', 'impact analysis', 'smoke test', 'suite pruning', 'selective testing'.

## Steps

1. Map code areas to the tests guarding them.
2. Select per change by impact: touched areas plus neighbors.
3. Layer execution: smoke per commit, selected per PR, full nightly.
4. Prune duplicates and obsolete cases quarterly.
5. Track escape-to-suite mapping to grow coverage where it leaked.

## Anti-patterns

- Full suite on every commit until duration kills feedback.
- Smoke suite bloated into a second full suite.
- Selection by gut feeling with no mapping.
- Deleted coverage with no escape analysis.

## Example

Selection rule: "Change in pricing runs pricing plus checkout suites; full suite nightly."

## Verification

Mapping current, layers timed, pruning cadenced, escapes feeding selection.

## Pairs-with

test-maintenance-refactor, risk-based-prioritization, quality-metrics-dashboard, flaky-test-elimination.
