---
name: playwright-modern-automation
description: "Modern web automation with Playwright distilled. Use when writing Playwright tests, auto-waiting locators, fixtures, trace viewer debugging, sharding in CI."
---

# Playwright Modern Automation

## Purpose

Build fast reliable web E2E with Microsoft Playwright: role-based locators, auto-waiting, fixtures, tracing, sharding.

## When to use

Use when the user says 'Playwright', 'web E2E', 'locator', 'auto-wait', 'trace viewer', 'sharding', 'flaky UI test'.

## Steps

1. Locate by role/label (getByRole, getByLabel), never brittle CSS/XPath.
2. Rely on auto-waiting assertions (toBeVisible, toHaveText); add explicit waits only for real async-via-network.
3. Isolate with fixtures: fresh context per test, seeded auth state.
4. Debug with trace viewer + screenshots on failure only.
5. Shard in CI (fullyParallel + shards) and quarantine flakes with retry budget.

## Anti-patterns

- sleep() waits and nth() positional selectors.
- Shared logged-in state across tests.
- Asserting implementation details instead of user-visible outcomes.
- No trace on failure, so flakes are undebuggable.

## Example

```js
test('login shows dashboard', async ({ page }) => {
  await page.goto('/login');
  await page.getByLabel('Email').fill('a@x.com');
  await page.getByRole('button', { name: 'Sign in' }).click();
  await expect(page.getByRole('heading', { name: 'Dashboard' })).toBeVisible();
});
```

Python equivalent uses sync_playwright with the same locator strategy.

## Verification

Zero sleep calls, role locators only, trace on failure, sharded CI green, flake rate tracked.

## Pairs-with

selenium-enterprise-patterns, webapp-testing, end-to-end-workflow-testing, testing-qa-version-control-rpa-v2.
