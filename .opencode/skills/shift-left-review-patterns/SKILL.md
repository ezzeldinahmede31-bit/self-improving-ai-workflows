---
name: shift-left-review-patterns
description: "Shift-left review patterns distilled. Use when catching defects early, peer reviews, static checks, requirements reviews, preview testing."
---

# Shift-Left Review Patterns

## Purpose

Catch defects where they are cheapest: review requirements and designs, automate static checks early, test preview builds per change.

## When to use

Use when the user says 'shift left', 'peer review', 'requirements review', 'static check', 'preview testing', 'early testing'.

## Steps

1. Review requirements for testability before design starts.
2. Review designs and contracts before implementation.
3. Run static analysis plus fast tests on every change.
4. Test preview builds per pull request, not after merge trains.
5. Measure defect discovery shift: earlier detection trending up.

## Anti-patterns

- Reviews as rubber stamps before merge.
- Static analysis disabled because of noise instead of tuning.
- Testing only after feature freeze.
- No metric proving the shift actually happened.

## Example

PR pipeline sketch: lint plus typecheck, fast unit set, preview deploy with smoke tags.

## Verification

Reviews recorded pre-code, static checks gated, previews tested per change, discovery timing tracked.

## Pairs-with

static-analysis-testing, requesting-code-review, receiving-code-review, dast-sast-integration.
