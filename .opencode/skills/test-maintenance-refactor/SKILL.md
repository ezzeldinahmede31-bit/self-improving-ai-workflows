---
name: test-maintenance-refactor
description: "Test maintenance and refactoring distilled. Use when keeping suites healthy, helper design, locator hygiene, suite gardening, deletion discipline."
---

# Test Maintenance Refactor

## Purpose

Treat tests as production code: refactor helpers, refresh locators, garden suites on cadence, delete with discipline.

## When to use

Use when the user says 'test maintenance', 'suite gardening', 'refactor tests', 'helper design', 'delete obsolete tests'.

## Steps

1. Apply production standards to test code: names, structure, reviews.
2. Centralize helpers and fixtures; remove duplication deliberately.
3. Refresh locators and data with the features they cover.
4. Garden on cadence: quarantine review, duration audit, duplication sweep.
5. Delete obsolete tests with the code they guarded, plus changelog note.

## Anti-patterns

- Test code exempt from review standards.
- Helpers copied per suite instead of shared.
- Dead tests kept for comfort.
- Refactors that change assertions silently.

## Example

Gardening checklist: quarantine age, slowest tests, duplicated helpers, orphaned data.

## Verification

Helpers shared, gardening cadenced, deletions tracked, assertion changes reviewed.

## Pairs-with

regression-strategy-patterns, flaky-test-elimination, test-data-management, xunit-test-patterns.
