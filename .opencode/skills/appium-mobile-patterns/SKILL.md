---
name: appium-mobile-patterns
description: "Appium mobile patterns distilled. Use when testing iOS and Android apps, desired capabilities, gestures, device farm, flakiness control."
---

# Appium Mobile Patterns

## Purpose

Automate mobile apps reliably: capability profiles per device, accessibility-id locators, gesture abstractions, device-farm sharding.

## When to use

Use when the user says 'Appium', 'mobile automation', 'desired capabilities', 'iOS test', 'Android test', 'device farm'.

## Steps

1. Define capability profiles per device and OS version under test.
2. Locate by accessibility id first, predicates second, coordinates never.
3. Wrap gestures (swipe, long-press, scroll-to) in named helpers.
4. Reset app state per test; never depend on prior test residue.
5. Shard across a device farm; collect device logs on failure.

## Anti-patterns

- XPath from root on every lookup (slow, brittle).
- Absolute-coordinate taps.
- Tests depending on execution order for logged-in state.
- One flagship device claimed as full coverage.

## Example

Python:

```python
driver.find_element(AppiumBy.ACCESSIBILITY_ID, "SignIn").click()
assert driver.find_element(AppiumBy.ACCESSIBILITY_ID, "HomeTitle").is_displayed()
```

## Verification

Capability profiles versioned, accessibility locators dominant, state reset per test, device logs attached.

## Pairs-with

espresso-xcuitest-mobile, webdriverio-patterns, test-data-management, flaky-test-elimination.
