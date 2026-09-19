---
name: compatibility-cross-testing
description: "Compatibility and cross-platform testing distilled. Use when covering browsers, OS versions, devices, screen sizes, graceful degradation."
---

# Compatibility Cross Testing

## Purpose

Cover the matrix that matters: browsers, OS versions, devices, sizes, with graceful degradation where full parity is uneconomic.

## When to use

Use when the user says 'compatibility test', 'cross-browser', 'cross-platform', 'device matrix', 'browser matrix', 'graceful degradation'.

## Steps

1. Define the supported matrix from analytics plus policy.
2. Automate critical journeys across the matrix in the cloud grid.
3. Test degradation explicitly where features cannot parity everywhere.
4. Verify installs, updates, and permissions per OS version.
5. Prune the matrix as usage shifts; announce drops early.

## Anti-patterns

- Testing only the latest flagship builds.
- Matrix by opinion instead of usage data.
- Silent breakage on older versions.
- Infinite matrix growth with no pruning.

## Example

Matrix card: browsers by share, OS floors, device classes, each mapped to smoke depth.

## Verification

Matrix data-driven, journeys green across it, degradation explicit, pruning announced.

## Pairs-with

playwright-modern-automation, appium-mobile-patterns, visual-regression-deep, release-readiness-gates.
