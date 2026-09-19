---
name: mainframe-testing-patterns
description: "Mainframe testing patterns distilled. Use when testing COBOL flows, JCL jobs, CICS screens, batch reconciliation, terminal emulation."
---

# Mainframe Testing Patterns

## Purpose

Test mainframe systems with modern discipline: job flows, screen maps, batch reconciliation, terminal automation, change-window safety.

## When to use

Use when the user says 'mainframe test', 'COBOL test', 'JCL', 'CICS', 'batch reconciliation', 'terminal emulation', '3270'.

## Steps

1. Map batch flows: jobs, dependencies, restart points.
2. Automate terminal screens via emulation with field-level assertions.
3. Reconcile batch outputs against source totals per cycle.
4. Test restart and rerun behavior after mid-flow failure.
5. Gate promotions on change-window checklists with backout proven.

## Anti-patterns

- Manual green-screen walkthroughs as the only coverage.
- Batch totals unchecked across cycles.
- Reruns corrupting already-processed records.
- Changes promoted without backout rehearsal.

## Example

Reconciliation check: input totals versus output totals versus reject queue, all three reported per cycle.

## Verification

Flows mapped, screens automated, reconciliation per cycle, restart proven, backout rehearsed.

## Pairs-with

mainframe-terminal-automation-v2, etl-validation-patterns, release-readiness-gates, test-environment-management.
