---
name: mutation-score-gates
description: "Mutation score gating distilled. Use when enforcing fault-detection bars, diff-scoped mutation, trend gates, equivalent mutant triage."
---

# Mutation Score Gates

## Purpose

Gate on fault detection, not lines: diff-scoped mutation runs, trend-based bars, triaged survivors, all wired into CI.

## When to use

Use when the user says 'mutation gate', 'mutation score', 'kill ratio gate', 'Stryker dashboard', 'fault detection bar'.

## Steps

1. Run mutation scoped to changed code per pull request.
2. Bar the trend: no new surviving mutants without triage notes.
3. Triage survivors as test-added or equivalent with reason.
4. Publish score trends per service over releases.
5. Expand scope gradually from diff to module to service.

## Anti-patterns

- Whole-codebase mutation blocking every merge.
- Equivalent mutants fought with brittle tests.
- Scores gamed by deleting hard-to-kill code paths.
- Mutation results visible nowhere in review.

## Example

Stryker sketch: `mutation score >= previous release score` as the merge bar.

## Verification

Diff-scoped runs per PR, survivors triaged, trends published, scope expanding deliberately.

## Pairs-with

mutation-testing-pit, code-coverage-mastery, quality-metrics-dashboard, release-readiness-gates.
