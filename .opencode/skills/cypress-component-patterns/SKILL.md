---
name: cypress-component-patterns
description: "Cypress testing patterns distilled. Use when writing Cypress E2E and component tests, intercepts, real-event simulation, time control."
---

# Cypress Component Patterns

## Purpose

Test web apps with Cypress confidently: component tests for UI units, E2E for flows, intercepts for network control, real events for fidelity.

## When to use

Use when the user says 'Cypress', 'component test', 'cy.intercept', 'Cypress E2E', 'real events', 'Cypress clock'.

## Steps

1. Cover UI units with component tests; reserve E2E for user flows.
2. Stub network with `cy.intercept` using fixtures, plus a few live-contract runs.
3. Query by accessible roles and labels, never test ids alone.
4. Control time with `cy.clock` for debounce and expiry behavior.
5. Record video only on failure to keep CI artifacts lean.

## Anti-patterns

- `cy.wait` with fixed milliseconds.
- Chained `then` pyramids instead of Cypress retry-ability.
- Visiting third-party logins in every test.
- Snapshotting full pages with dynamic content.

## Example

```js
cy.intercept('GET', '/api/cart', { fixture: 'cart.json' });
cy.getByRole('button', { name: 'Checkout' }).click();
cy.getByRole('heading', { name: 'Order confirmed' }).should('be.visible');
```

## Verification

Component plus E2E split sane, intercepts fixtured, accessible queries, time controlled.

## Pairs-with

playwright-modern-automation, visual-regression-deep, flaky-test-elimination, api-testing-contract-patterns.
