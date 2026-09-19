---
name: scrum-qa-integration
description: "Scrum QA integration distilled. Use when embedding testing in sprints, definition of done, story readiness, sprint test capacity, demos."
---

# Scrum QA Integration

## Purpose

Embed quality inside Scrum: ready stories, tested increments per sprint, strong definition of done, demo-proven acceptance.

## When to use

Use when the user says 'Scrum testing', 'definition of done', 'definition of ready', 'sprint QA', 'story acceptance', 'sprint demo'.

## Steps

1. Gate sprint entry with readiness: clear acceptance plus testable scope.
2. Test inside the sprint; no separate hardening sprints by default.
3. Enforce definition of done covering code, tests, docs, observability.
4. Demo from production-like builds with acceptance replayed live.
5. Carry undone work explicitly; never silently lower done.

## Anti-patterns

- Testing phase after the sprint ends.
- Done meaning merged without tests or docs.
- Readiness skipped, then churn blamed on QA.
- Demos on mocked builds hiding integration gaps.

## Example

DoD card: reviewed, unit plus contract green, exploratory chartered, docs updated, alerts live.

## Verification

Readiness enforced, done evidenced per story, demos live, carryover explicit.

## Pairs-with

agile-testing-quadrants-deep, kanban-qa-flow, acceptance-test-driven, crispin-agile-testing.
