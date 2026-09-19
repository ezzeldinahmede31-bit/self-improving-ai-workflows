---
name: defect-triage-rootcause
description: "Defect triage and root cause distilled. Use when triaging bugs, severity versus priority, five whys, reproduction quality, fix verification."
---

# Defect Triage Root Cause

## Purpose

Turn bug queues into decisions: reproducible reports, severity versus priority split, root-cause analysis, verified fixes.

## When to use

Use when the user says 'bug triage', 'defect triage', 'severity priority', 'root cause', 'five whys', 'bug report quality'.

## Steps

1. Require reproduction: steps, data, expected versus actual, environment.
2. Split severity (impact) from priority (order of fix) explicitly.
3. Triage on cadence with product plus engineering ownership.
4. Root-cause systemic bugs with five whys to process fixes.
5. Verify fixes on the original reproduction plus neighbors.

## Anti-patterns

- One-line bug reports nobody can reproduce.
- Severity and priority used interchangeably.
- Triage meetings without decision authority.
- Fixes closed without re-running the reproduction.

## Example

Report skeleton: title, severity, priority, steps, data, expected, actual, environment, logs link.

## Verification

Reports reproducible, severity/priority split recorded, systemic causes actioned, fixes re-proven.

## Pairs-with

thinking-five-whys-plus, root-cause-post-mortem-analyzer, quality-metrics-dashboard, black-risk-based-testing.
