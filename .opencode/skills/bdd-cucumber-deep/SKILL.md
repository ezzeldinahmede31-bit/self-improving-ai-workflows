---
name: bdd-cucumber-deep
description: "Deep BDD with Cucumber distilled. Use when writing feature files, step definitions, data tables, scenario outlines, living docs pipeline."
---

# BDD Cucumber Deep

## Purpose

Run BDD with Cucumber properly: declarative features, reusable steps, data tables, tagged selective runs, living documentation out of CI.

## When to use

Use when the user says 'Cucumber', 'feature file', 'step definition', 'scenario outline', 'data table', 'BDD automation'.

## Steps

1. Write features with the trio; keep steps declarative and domain-worded.
2. Build a small step library; parametrize with data tables and outlines.
3. Tag by area and speed; run fast tags per commit, full set nightly.
4. Publish HTML living docs from every CI run.
5. Retire or rewrite steps that leak UI mechanics into feature text.

## Anti-patterns

- One-off steps per scenario duplicating the same action.
- Scenario outlines exploding across irrelevant value mixes.
- Feature files edited only by automation engineers.
- UI locators embedded in step text.

## Example

```gherkin
Scenario Outline: Discount tiers
  Given a <tier> customer
  When checkout completes
  Then discount equals <pct> percent
  Examples:
    | tier   | pct |
    | silver | 5   |
    | gold   | 10  |
```

## Verification

Steps reused across features, tags gate CI stages, living docs published, no locators in feature text.

## Pairs-with

adzic-specification-by-example, example-mapping-workshops, acceptance-test-driven, bdd-trio-collaboration.
