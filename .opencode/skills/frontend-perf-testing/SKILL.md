---
name: frontend-perf-testing
description: "Frontend performance testing distilled. Use when testing Core Web Vitals, bundles, rendering, lazy loading, image weight, interaction latency."
---

# Frontend Performance Testing

## Purpose

Keep pages fast on real devices: Core Web Vitals budgets, bundle discipline, render-path control, interaction latency proof.

## When to use

Use when the user says 'Core Web Vitals', 'LCP', 'CLS', 'INP', 'bundle size', 'frontend performance', 'render blocking'.

## Steps

1. Budget LCP, CLS, and INP per page class; fail CI above budget.
2. Split bundles by route; defer non-critical scripts.
3. Optimize media: modern formats, sizing, lazy loading below fold.
4. Measure on throttled mid-tier devices, not flagship hardware.
5. Track budgets over releases; investigate every regression.

## Anti-patterns

- Lab-only scores with no field data.
- One giant bundle for all routes.
- Unoptimized hero images blocking LCP.
- Animations driving layout thrash on scroll.

## Example

Lighthouse CI assertion:

```json
{ "assertions": { "largest-contentful-paint": ["error", { "maxNumericValue": 2500 }] } }
```

## Verification

Budgets enforced in CI, bundles split, media sized, field data tracked per release.

## Pairs-with

high-performance-browser-networking, visual-regression-deep, cdn-cache-testing, systems-performance-profiling.
