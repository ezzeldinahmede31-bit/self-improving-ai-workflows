---
name: crispin-agile-testing
description: "Tests inside agile delivery: quadrants, whole-team quality, and automation pyramid. Use when the user says 'agile testing', 'testing quadrants', 'whole team quality', 'test automation pyramid', 'Crispin Gregory', 'Agile Testing quadrants', or when testing lags development every sprint."
---

# Crispin Agile Testing

Distilled from Crispin & Gregory *Agile Testing* (+ *More Agile Testing*):
quality is the WHOLE team's job, built in every day — quadrants organize the
testing, the pyramid funds it, and collaboration replaces handoffs.

## Purpose

Embed testing into agile delivery so each increment ships tested: the right
tests at the right level, owned by the whole team, automated by economics.

## The framework

1. **Quadrants organize (not phases).** Q1 technology-facing, guides dev
   (unit/component); Q2 business-facing, guides dev (functional/story,
   prototypes); Q3 business-facing, critiques product (exploratory, usability,
   UAT); Q4 technology-facing, critiques product (performance, security,
   load). Plan per story: which quadrants does THIS story need? Empty
   quadrants are decisions, not oversights.
2. **Whole-team quality.** Testers embed from story shaping (acceptance
   criteria co-authored, examples agreed BEFORE code); developers test
   (unit + pairing on automation); no QA-phase at sprint end (testing
   continuous, "done" includes all quadrants planned). Handoffs are where
   quality dies — eliminate them.
3. **Automation pyramid funds it.** Many fast unit checks, fewer service/API
   checks, fewest UI E2E (brittle, slow). Invert the pyramid (ice-cream
   cone: all UI tests) and every release melts. Each new automated check
   justifies its maintenance cost or it is deleted.
4. **Testable stories in.** INVEST + testability: acceptance criteria with
   examples (Specification by Example habits), wireframes for UI stories,
   performance budgets as criteria. Untestable stories go BACK to shaping —
   building them builds debt.
5. **Feedback loops shorten relentlessly.** CI per commit, demo per story,
   retro per sprint with testing improvements as first-class actions.
   Release cadence is the quality metric that matters (frequent small
   releases beat rare big bangs on every defect stat).

## Verification

Sprint review: quadrant coverage per story (named, including empties),
pyramid shape measured (counts per level trending right), automation
maintenance cost tracked, retro testing-action closed. Testing "later" is a
lie the board should show.

## Pairs with

- `kaner-lessons-testing` (context judgment),
  `hendrickson-explore-it` (Q3 execution),
  `test-driven-development` (Q1/Q2 automation),
  `n8n-delivery-verification-gate` (done-means-done discipline).
