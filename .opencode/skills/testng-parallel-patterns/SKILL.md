---
name: testng-parallel-patterns
description: "TestNG parallel patterns distilled. Use when running TestNG suites, XML configuration, data providers, parallel methods, dependency chains."
---

# TestNG Parallel Patterns

## Purpose

Run TestNG suites fast and stable: XML suite design, data providers, parallel methods with thread-safe fixtures, explicit dependencies.

## When to use

Use when the user says 'TestNG', 'testng.xml', 'data provider', 'parallel methods', 'dependsOnMethods', 'TestNG suite'.

## Steps

1. Design suites in XML: smoke, regression, quarantine groups.
2. Feed cases through `@DataProvider`, never copy-pasted test methods.
3. Parallelize at method level with thread-safe fixtures.
4. Declare true dependencies with `dependsOnMethods`; remove false ones.
5. Retry only known-flaky integrations with a strict budget plus owner.

## Anti-patterns

- `dependsOnMethods` chains hiding as sequencing for shared state.
- Data providers returning unreadable object arrays.
- Parallel classes sharing static drivers.
- Retry listeners masking real failures.

## Example

```java
@Test(dataProvider = "tiers")
void discount_applies(String tier, int expected) {
    assertEquals(expected, pricing.discount(tier));
}
```

## Verification

XML suites layered, providers readable, parallel green, retries bounded with owners.

## Pairs-with

junit5-enterprise-patterns, flaky-test-elimination, test-data-management, selenium-enterprise-patterns.
