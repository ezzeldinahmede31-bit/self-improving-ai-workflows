---
name: compliance-testing-patterns
description: "Compliance testing patterns distilled. Use when proving regulatory conformance, controls mapping, evidence packs, SOC2 ISO HIPAA PCI checks."
---

# Compliance Testing Patterns

## Purpose

Prove conformance systematically: controls mapped to tests, evidence generated per cycle, gaps tracked to remediation.

## When to use

Use when the user says 'compliance test', 'SOC2', 'ISO 27001', 'HIPAA', 'PCI DSS', 'controls testing', 'audit readiness'.

## Steps

1. Map each control to concrete tests plus evidence sources.
2. Automate evidence collection where systems allow it.
3. Test access reviews, encryption, logging, retention on cadence.
4. Track gaps with owners plus dates; retest on closure.
5. Package evidence per audit cycle, versioned and signed.

## Anti-patterns

- Screenshot archaeology the week before audit.
- Controls mapped to intentions instead of tests.
- Gaps tracked informally with no dates.
- Evidence generated manually each cycle.

## Example

Control card: control text, mapped tests, evidence links, last verified date, owner.

## Verification

Controls mapped, evidence automated where possible, gaps dated, packs versioned.

## Pairs-with

audit-trail-test-evidence, test-documentation-living, secrets-scan-testing, dast-sast-integration.
