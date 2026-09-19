---
name: risk-based-prioritization
description: "Risk-based prioritization distilled. Use when ranking tests by risk, probability times impact, coverage weighting, release focus."
---

# Risk-Based Prioritization

## Purpose

Spend test effort where failure hurts most: risk-rank areas by probability times impact, then weight coverage accordingly.

## When to use

Use when the user says 'risk-based testing', 'test prioritization', 'probability impact', 'risk matrix', 'release focus'.

## Steps

1. List quality risks per area with stakeholders.
2. Score probability and impact openly; multiply for rank.
3. Weight test depth by rank: deep on top risks, light elsewhere.
4. Re-rank when code, usage, or incidents shift the picture.
5. Report coverage against risks, not raw percentages.

## Anti-patterns

- Equal effort everywhere regardless of risk.
- Risk scores set solo without stakeholders.
- Rankings frozen while the product changes.
- Coverage reported without risk mapping.

## Example

Risk card: area, probability, impact, rank, planned depth, owner.

## Verification

Risks ranked with stakeholders, depth follows rank, re-ranking cadenced, reporting risk-mapped.

## Pairs-with

black-risk-based-testing, test-strategy-architecture, release-readiness-gates, quality-metrics-dashboard.
