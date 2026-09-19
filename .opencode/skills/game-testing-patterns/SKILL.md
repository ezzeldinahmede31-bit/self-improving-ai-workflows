---
name: game-testing-patterns
description: "Game testing patterns distilled. Use when testing gameplay, physics, balance, save systems, multiplayer sync, platform certification."
---

# Game Testing Patterns

## Purpose

Test games as systems plus feel: functional correctness, physics stability, balance data, saves, multiplayer sync, cert readiness.

## When to use

Use when the user says 'game test', 'playtest', 'game balance', 'multiplayer sync', 'save system', 'certification test', 'physics test'.

## Steps

1. Automate systems: saves, inventories, progression rules, economy math.
2. Stress physics and frame budgets on min-spec hardware.
3. Balance with telemetry: win rates, progression curves, economy sinks.
4. Test multiplayer sync under lag, loss, and host migration.
5. Pre-check platform certification rules before submission.

## Anti-patterns

- Only manual playtests with no automated systems coverage.
- Balance tuned on designer feel without telemetry.
- Save corruption found by players first.
- Cert submission without pre-check runs.

## Example

Economy check: simulated player cohorts keep currency sinks ahead of faucets across progression.

## Verification

Systems automated, budgets met on min-spec, balance telemetered, sync proven, cert pre-checked.

## Pairs-with

performance-testing-k6-jmeter, compatibility-cross-testing, soak-endurance-testing, quality-metrics-dashboard.
