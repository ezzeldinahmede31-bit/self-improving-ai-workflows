---
name: hendrickson-explore-it
description: "Explores software skillfully: charters, sessions, and heuristics. Use when the user says 'exploratory testing', 'session-based testing', 'test charter', 'SBTM', 'tour testing', 'Hendrickson', 'Explore It', or when scripted tests pass but users still suffer."
---

# Hendrickson Explore It!

Distilled from Elisabeth Hendrickson *Explore It!*: simultaneous learning,
design, and execution — structured exploration finds what scripts cannot,
because scripts only check what someone already imagined.

## Purpose

Discover unknown unknowns systematically: chartered missions, time-boxed
sessions, and heuristic tours that turn curiosity into coverage.

## The practice

1. **Charter every session.** Mission (what to explore + risks targeted),
   time box (60-120 min), deliverables (bugs, questions, coverage notes).
   Unchartered exploring is wandering; chartered exploring is an experiment.
2. **Tour heuristics (where to look).** Guideword tours: Money (anything
   financial), Landmark (core features), Bad-neighborhood (historical bug
   clusters), Saboteur (try to break it on purpose), All-nighter (soak/long
   runs), Persona (each user type's journey), Supermodel (UI consistency),
   Back-alley (config files, logs, error paths). Pick tours by risk, not
   comfort.
3. **Vary systematically.** Inputs (valid/invalid/empty/massive/unicode),
   environment (slow network, low disk, wrong timezone, dark mode),
   sequence (cancel mid-flow, double-submit, back-button, refresh),
   users (permissions, concurrency, stale sessions). Variation dimensions
   listed per session — randomness without dimensions is luck.
4. **Note as you go.** Session sheet: charter, timeline of actions,
   bugs with repro, QUESTIONS (unanswered = risks), coverage achieved,
   ideas for automation (stable checks discovered become scripts).
   Debrief after every session (5 min): what did we learn, what scares us?
5. **Pair and rotate.** Explore in pairs (driver + recorder/questioner);
   rotate areas so familiarity blindness never settles. Fresh eyes find
   stale bugs — schedule them.

## Verification

Session output: bugs filed with repro, open questions risk-ranked,
automation candidates extracted, charter coverage judged. A session with
zero notes is a break, not testing.

## Pairs with

- `kaner-lessons-testing` (context strategy),
  `myers-art-of-testing` (design techniques for follow-ups),
  `zeller-why-programs-fail` (from bug to cause),
  `tdd-sandbox-proof-engine` (automating the stable discoveries).
