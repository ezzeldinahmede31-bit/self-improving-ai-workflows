---
name: localization-i18n-testing
description: "Localization and i18n testing distilled. Use when testing translations, locales, RTL, date currency formats, pseudo-localization, encoding."
---

# Localization i18n Testing

## Purpose

Prove the product travels: locale coverage, RTL layouts, date and currency formats, pseudo-localization resilience, encoding safety.

## When to use

Use when the user says 'localization test', 'i18n test', 'RTL', 'translation test', 'pseudo-localization', 'locale format'.

## Steps

1. Externalize every string; fail CI on hardcoded UI text.
2. Pseudo-localize to expose layout breaks early.
3. Verify RTL mirroring, icons, and navigation direction.
4. Check dates, currencies, plurals per locale with native review.
5. Test encoding end to end: input, storage, export, email.

## Anti-patterns

- Concatenated sentences translators cannot reorder.
- Pixels fixed so translations overflow.
- Machine output shipped without native review.
- Dates formatted in server locale for all users.

## Example

Pseudo-locale probe: `[!! Tésţ Štrïng !!]` must render without breakage or truncation.

## Verification

Strings externalized, pseudo runs green, RTL mirrored, native review recorded, encoding round-trips.

## Pairs-with

usability-testing-patterns, visual-regression-deep, playwright-modern-automation, test-data-management.
