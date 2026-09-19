---
name: sap-erp-testing
description: "SAP ERP testing distilled. Use when testing SAP transactions, IDocs, batch jobs, transports, regression across modules, cutover rehearsal."
---

# SAP ERP Testing

## Purpose

Test SAP landscapes safely: transaction flows, IDoc integration, job chains, transport sequencing, cutover rehearsal.

## When to use

Use when the user says 'SAP test', 'SAP regression', 'IDoc test', 'transport test', 'cutover', 'SAP batch job', 'T-code'.

## Steps

1. Cover core transaction flows per module in scope.
2. Test IDocs inbound plus outbound with partner profiles.
3. Validate job chains and dependencies in the scheduler.
4. Sequence transports across landscape tiers with regression per tier.
5. Rehearse cutover with data migration timing plus rollback.

## Anti-patterns

- Testing only in development clients.
- Transports rushed without tier regression.
- IDoc failures discovered by business users.
- Cutover rehearsed never, executed once live.

## Example

Tier gate card: dev transactions green, QA regression green, pre-prod cutover rehearsal timed.

## Verification

Flows covered per module, IDocs proven both ways, transports sequenced, cutover rehearsed.

## Pairs-with

etl-validation-patterns, release-readiness-gates, test-environment-management, regression-strategy-patterns.
