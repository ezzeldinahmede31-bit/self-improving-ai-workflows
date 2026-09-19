---
name: espresso-xcuitest-mobile
description: "Native mobile testing with Espresso and XCUITest distilled. Use when writing Android Espresso or iOS XCUITest suites, idling resources, launch args."
---

# Espresso and XCUITest

## Purpose

Test native mobile apps at the platform level: Espresso synchronization on Android, XCUITest launch arguments and page modeling on iOS.

## When to use

Use when the user says 'Espresso', 'XCUITest', 'Android test', 'iOS UI test', 'idling resource', 'launch arguments'.

## Steps

1. Prefer Espresso for Android UI and XCUITest for iOS UI; use Appium for cross-platform breadth.
2. Register idling resources for background work instead of sleeps.
3. Drive variants with launch arguments and mocked backends.
4. Model screens as page objects with accessibility identifiers.
5. Run on CI simulators plus a physical-device sample for hardware paths.

## Anti-patterns

- Sleeps around animations and network.
- Tests requiring manual backend state.
- Accessibility identifiers missing, forcing fragile queries.
- Simulator-only runs for camera, GPS, and push paths.

## Example

```swift
let app = XCUIApplication()
app.launchArguments = ["-mockBackend"]
app.buttons["SignIn"].tap()
XCTAssertTrue(app.staticTexts["HomeTitle"].waitForExistence(timeout: 5))
```

## Verification

Idling resources registered, backends mocked via launch args, identifiers present, hardware paths on devices.

## Pairs-with

appium-mobile-patterns, test-data-management, flaky-test-elimination, api-testing-contract-patterns.
