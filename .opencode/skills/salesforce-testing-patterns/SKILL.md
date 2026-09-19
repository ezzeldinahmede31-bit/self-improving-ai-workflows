---
name: salesforce-testing-patterns
description: "Salesforce testing patterns distilled. Use when testing Apex, flows, validation rules, sandboxes, deployments, governor limits."
---

# Salesforce Testing Patterns

## Purpose

Test Salesforce orgs reliably: Apex unit tests, flow coverage, validation rules, sandbox strategy, safe deployments.

## When to use

Use when the user says 'Salesforce test', 'Apex test', 'flow test', 'validation rule', 'sandbox', 'governor limits', 'SFDX'.

## Steps

1. Write Apex tests with meaningful asserts plus bulk-shape data.
2. Cover flows and validation rules with boundary-shaped records.
3. Prove governor-limit headroom on bulk operations.
4. Promote through sandboxes mirroring production shape.
5. Validate deployments with quick plus full suite per change size.

## Anti-patterns

- SeeAllData tests depending on org residue.
- Assertion-free Apex tests gaming coverage.
- Flows changed directly in production.
- Governor limits discovered during data loads.

## Example

```apex
@IsTest static void discountApplies() {
    Order__c o = TestFactory.orderWithTier('GOLD');
    System.assertEquals(10, Pricing.discount(o), 'gold tier discount');
}
```

## Verification

Asserts meaningful, bulk shapes covered, limits proven, sandboxes mirrored, deploys validated.

## Pairs-with

test-data-management, flaky-test-elimination, release-readiness-gates, regression-strategy-patterns.
