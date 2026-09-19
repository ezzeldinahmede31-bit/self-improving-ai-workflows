---
name: bach-session-exploratory
description: "James Bach session-based exploratory testing distilled. Use when doing exploratory testing, charters, SBTM time-boxing, debriefing, heuristics, rapid test design."
---

# Session-Based Exploratory Testing (Bach)

## Purpose

Run disciplined exploratory testing per James Bach / Rapid Software Testing: chartered time-boxed sessions, heuristics, debriefable evidence.

## When to use

Use when the user says 'exploratory testing', 'charter', 'session-based', 'SBTM', 'heuristics', 'debrief', 'rapid testing', 'Bach'.

## Steps

1. Write a charter: mission + areas + risks + a single uninterrupted timebox.
2. Pick heuristics: SFDPO (Structure, Function, Data, Platform, Operations), Goldilocks, CRUD.
3. Test-design-execute-learn in tight loops; log notes, bugs, questions, coverage.
4. Debrief with PROOF: Past coverage, Results, Obstacles, Outlook, Feelings.
5. Convert repeatable finds into automated checks; keep exploration for the unknown.

## Anti-patterns

- Unchartered random clicking with no mission or notes.
- Sessions interrupted by chat and multitasking.
- No debrief, so findings evaporate.
- Automating everything and starving exploration time.

## Example

Charter: "Explore checkout coupons within one timebox; risks: stacking, expiry, rounding."

```python
# session log entry
log = {"charter": "coupons", "bugs": ["STACK-12: two coupons stack to -5 total"], "questions": ["Is stacking allowed?"]}
```

## Verification

Charter sheet + timebox honored + PROOF debrief filed + fresh risks or bugs captured per session.

## Pairs-with

hendrickson-explore-it, kaner-lessons-testing, myers-art-of-testing, black-risk-based-testing.
