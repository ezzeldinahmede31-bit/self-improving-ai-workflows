---
name: visual-regression-deep
description: "Visual regression testing deep distilled. Use when testing UI appearance, screenshots, baselines, masks, diff budgets, cross-browser rendering."
---

# Visual Regression Deep

## Purpose

Catch unintended UI change: versioned baselines, masked dynamic zones, tight diff budgets, per-viewport and theme coverage.

## When to use

Use when the user says 'visual regression', 'screenshot test', 'baseline image', 'Percy', 'Chromatic', 'UI diff', 'pixel diff'.

## Steps

1. Capture baselines per viewport plus dark and light themes.
2. Mask dynamic zones (ads, avatars, timestamps) explicitly.
3. Set a small diff budget; fail above it, review below it.
4. Review every visual change with design ownership.
5. Version baselines with the code that renders them.

## Anti-patterns

- Full-page diffs on dynamic content.
- Auto-accepting baselines to clear the queue.
- One viewport claimed as full coverage.
- Baselines stored outside version control.

## Example

Playwright:

```js
await expect(page.getByRole('dialog')).toHaveScreenshot('dialog.png', { maxDiffPixels: 50 });
```

## Verification

Baselines versioned, masks explicit, diff budget enforced, design reviews recorded.

## Pairs-with

playwright-modern-automation, snapshot-testing-patterns, ai-powered-testing-patterns, frontend-perf-testing.
