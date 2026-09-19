---
name: selenium-enterprise-patterns
description: "Enterprise Selenium WebDriver patterns distilled. Use when maintaining Selenium suites, Page Objects, WebDriverWait, Grid scaling, Java enterprise automation."
---

# Selenium Enterprise Patterns

## Purpose

Keep large Selenium suites sustainable: Page Objects, explicit waits, Grid scaling, stable Java patterns.

## When to use

Use when the user says 'Selenium', 'WebDriver', 'Page Object', 'WebDriverWait', 'Selenium Grid', 'enterprise automation'.

## Steps

1. Encapsulate pages as Page Objects exposing user tasks, not elements.
2. Replace implicit waits with explicit WebDriverWait + ExpectedConditions.
3. Externalize capabilities; run parallel on Selenium Grid with retries isolated.
4. Stabilize data: seeded test users, independent datasets per thread.
5. Migrate new work to Playwright where justified; keep Selenium where enterprise mandates it.

## Anti-patterns

- Thread.sleep and implicit waits mixed together.
- Element locators scattered in test bodies.
- One shared browser session for the whole suite.
- Screenshots for every step bloating storage.

## Example

Python:

```python
wait = WebDriverWait(driver, 10)
wait.until(EC.visibility_of_element_located((By.ROLE, "dashboard")))
```

## Verification

No sleeps, Page Objects cover all flows, Grid parallel run green, failures carry page + console log.

## Pairs-with

playwright-modern-automation, webapp-testing, rate-limit-aware-consumers, observability-execution-monitoring.
