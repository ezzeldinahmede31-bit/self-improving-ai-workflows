---
name: webdriverio-patterns
description: "WebdriverIO patterns distilled. Use when writing WebdriverIO tests, page objects, services, multiremote, mobile via Appium service."
---

# WebdriverIO Patterns

## Purpose

Automate browsers with WebdriverIO cleanly: typed page objects, services for reporting and drivers, multiremote where needed, Appium service for mobile.

## When to use

Use when the user says 'WebdriverIO', 'wdio', 'WebdriverIO services', 'multiremote', 'wdio config'.

## Steps

1. Scaffold with the typed config; pin browser versions per run.
2. Write page objects exposing tasks with async commands.
3. Attach services: reporting, visual, Appium for mobile targets.
4. Shard specs across workers with isolated sessions.
5. Collect browser console errors as first-class failures.

## Anti-patterns

- `browser.pause` as synchronization.
- Selectors duplicated across specs.
- Shared browser profile across parallel workers.
- Console errors ignored while UI looks green.

## Example

```js
await LoginPage.open();
await LoginPage.signIn('a@x.com');
await expect(DashboardPage.heading).toBeDisplayed();
```

## Verification

Typed config, task-based page objects, sharded green runs, console errors asserted.

## Pairs-with

selenium-enterprise-patterns, playwright-modern-automation, appium-mobile-patterns, flaky-test-elimination.
