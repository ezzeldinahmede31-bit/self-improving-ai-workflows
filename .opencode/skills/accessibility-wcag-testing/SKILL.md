---
name: accessibility-wcag-testing
description: "Accessibility WCAG testing distilled. Use when testing keyboard flow, screen readers, contrast, focus order, ARIA,axe scans."
---

# Accessibility WCAG Testing

## Purpose

Prove access for all: keyboard-complete flows, screen-reader sanity, contrast, focus order, honest ARIA, automated scans plus manual passes.

## When to use

Use when the user says 'accessibility test', 'WCAG', 'screen reader', 'keyboard navigation', 'contrast', 'ARIA', 'axe'.

## Steps

1. Drive core flows keyboard-only; every action reachable and visible.
2. Run automated scans (axe) in CI and clear violations per component.
3. Test with a screen reader on critical journeys.
4. Verify focus order, traps in dialogs, and skip links.
5. Check contrast plus zoom plus reduced-motion behavior.

## Anti-patterns

- Scan-green claimed as accessible without manual passes.
- Divs with click handlers instead of real controls.
- Focus lost after dialogs close.
- Motion that cannot be reduced on request.

## Example

Playwright axe check:

```js
const { violations } = await checkA11y(page, { detailedReport: true });
expect(violations).toEqual([]);
```

## Verification

Keyboard flows complete, scans gated, screen-reader journeys verified, focus plus contrast proven.

## Pairs-with

dont-make-me-think, usability-testing-patterns, playwright-modern-automation, visual-regression-deep.
