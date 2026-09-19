---
name: whittaker-google-testing
description: "Tests at Google scale: roles, automation culture, and 10-minute builds. Use when the user says 'How Google Tests', 'SET vs TE', 'test certified', 'Google test culture', 'Whittaker', or when testing must scale across hundreds of engineers."
---

# Whittaker How Google Tests Software

Distilled from Whittaker/Arbon/Carollo *How Google Tests Software*: scale
testing through roles and culture — SWE (build), SET (build testability +
tools), TE (user-focused exploratory + coordination) — with automation as
shared infrastructure and speed as a feature.

## Purpose

Make quality scale with headcount: clear testing roles, common tooling, and
a build/test pipeline fast enough that everyone uses it every time.

## The operating model

1. **Roles that scale.** SWE owns unit tests for their code (non-negotiable,
   reviewed like code). SET builds test frameworks, harnesses, and
   hermetic environments (testing as engineering product). TE coordinates:
   exploratory charters, user scenarios, release sign-off, bug advocacy.
   Everyone tests; specialists multiply.
2. **Test Certified ladder.** Levels 1-5 (from "tests exist" to "released
   multiple times daily with full automation"): teams self-assess and climb
   publicly. Gamified maturity beats mandated process — publish the ladder,
   celebrate climbs.
3. **Automation as infrastructure.** Shared frameworks (one way to write
   tests, not fifteen), hermetic test environments (no shared staging
   flakiness), sharded parallel execution. The 10-minute rule: commit-to-
   signal under ten minutes or engineers bypass the pipeline (and quality
   with it) — speed is a quality control.
4. **Crowd + dogfood + beta.** Internal crowdtesting (googlers breaking
   pre-releases), dogfooding at scale (company runs the build), staged
   rollouts with metrics gates (canary analysis, automatic rollback).
   Production exposure graduated by evidence, never by calendar.
5. **Bug lifecycle at velocity.** One database, reproducible-first triage,
   fix-verified-by-reporter-area, post-mortems blameless with process
   actions. Release decisions from dashboards (crash rates, test health,
   rollout metrics), not meetings.

## Verification

Org testing review: role coverage per team, ladder level current + climbing
plan, pipeline time measured (commit-to-signal), flake rate tracked with
owners, rollout metrics gating releases. Testing that slows shipping gets
engineered faster, never skipped.

## Pairs with

- `continuous-delivery-pipeline` (pipeline mechanics),
  `aniche-effective-testing` (testability),
  `crispin-agile-testing` (team-level agile),
  `sre-devops-automation` (rollout safety).
