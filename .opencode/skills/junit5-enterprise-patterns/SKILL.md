---
name: junit5-enterprise-patterns
description: "Enterprise JUnit 5 patterns distilled. Use when writing Java tests, extensions, parameterized tests, nested structure, parallel execution."
---

# JUnit 5 Enterprise Patterns

## Purpose

Write Java tests that scale: nested structure, parameterized cases, extensions for fixtures, parallel execution with isolation.

## When to use

Use when the user says 'JUnit 5', 'Java test', 'parameterized test', 'nested test', 'extension model', 'parallel execution Java'.

## Steps

1. Structure with @Nested classes mirroring behavior areas.
2. Parametrize with @MethodSource for readable case tables.
3. Encapsulate fixtures in extensions, not base classes.
4. Enable parallel execution with isolated state per test.
5. Enforce architecture rules with `@Tag`-gated suites (fast versus slow).

## Anti-patterns

- Deep inheritance hierarchies of test base classes.
- Static mutable state shared across tests.
- Sleeping for async conditions instead of `assertTimeoutPreemptively`.
- All tests in one flat class.

## Example

```java
@ParameterizedTest
@CsvSource({"STANDARD, 0", "GOLD, 10"})
void discount_applies(Tier tier, int expected) {
    assertEquals(expected, pricing.discount(tier));
}
```

## Verification

Nested structure present, cases table-driven, extensions own fixtures, parallel run green.

## Pairs-with

testng-parallel-patterns, khorikov-unit-testing, xunit-test-patterns, test-data-management.
