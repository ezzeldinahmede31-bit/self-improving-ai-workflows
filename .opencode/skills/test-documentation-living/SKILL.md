---
name: test-documentation-living
description: "Living test documentation distilled. Use when keeping test docs current, generated docs, traceability, audit-ready evidence, runbooks."
---

# Living Test Documentation

## Purpose

Keep test knowledge alive: docs generated from specs and runs, traceability maintained by tooling, evidence ready for audit.

## When to use

Use when the user says 'test documentation', 'living docs', 'traceability', 'audit evidence', 'test report', 'runbook'.

## Steps

1. Generate docs from executable specs, not hand-written mirrors.
2. Maintain traceability requirement to test to run via tooling.
3. Publish run evidence per release: scope, results, signals, decisions.
4. Keep runbooks beside the suites they rescue.
5. Prune stale pages on the same cadence as suite gardening.

## Anti-patterns

- Hand-maintained matrices rotting after one release.
- Screenshots of dashboards as audit evidence.
- Runbooks in chat history instead of versioned docs.
- Documentation sprints producing paper nobody reads.

## Example

Release evidence pack: scope link, suite run link, perf report link, scan report link, decision record.

## Verification

Docs generated, traceability tooled, evidence per release, stale pages pruned.

## Pairs-with

n8n-autodoc-mermaid, release-readiness-gates, audit-trail-test-evidence, adzic-specification-by-example.
