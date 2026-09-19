---
name: fitzpatrick-team-geek
description: "Runs engineering teams on Humility, Respect, Trust: review culture and conflict handling. Use when the user says 'code review culture', 'HRT', 'bus factor', 'team conflict', 'review etiquette', 'Team Geek', 'Fitzpatrick', or when the team process, not the code, is the bottleneck."
---

# Fitzpatrick Team Geek

Distilled from Fitzpatrick & Collins-Sussman *Team Geek*: great teams run on
HRT — Humility (you are not the center), Respect (colleagues are smart and
capable), Trust (they will do the right thing). Every practice below is HRT
operationalized.

## Purpose

Make collaboration the default output of the team: reviews that teach,
conflicts that resolve, knowledge that spreads.

## The practices

1. **HRT as law.** Humility: admit mistakes fast, ask for help early, accept
   better ideas regardless of source. Respect: critique work never people,
   assume competence, mind time zones and async colleagues. Trust: delegate
   real ownership, share context by default. Violations named kindly, once —
   patterns escalated.
2. **Review culture that teaches.** Reviews are knowledge transfer first,
   defect-catching second: small diffs, fast turnaround (< 1 day), comments
   as questions/suggestions (never commands), praise for good patterns
   (reinforce what to repeat). Author responds to every thread; unresolved =
   unmerged.
3. **Busy-work elimination.** Automate the toil (formatting, linting,
   trivial checks in bots) so human review spends on design and edge cases.
   If reviewers debate style, the linter is misconfigured — fix the tool,
   not the people.
4. **Conflict protocol.** Disagree on technical merit with data or prototype,
   not seniority. Time-box debates; the decider and the decision date named
   up front; disagree-and-commit recorded with the dissent (revisit triggers
   stated). Personal friction goes private immediately, never in review
   threads.
5. **Bus-factor engineering.** No single-person knowledge silos: rotate
   review areas, pair on critical paths, document the why (decisions log),
   onboard by doing real work week one. Measure: "who else could ship this?"
   — the answer must never be "nobody".

## Verification

Team health check quarterly: review latency stats, HRT incident log (empty
is suspicious — psychological safety means issues surface), bus-factor map
current, toil hours trending down. Culture without metrics is mood.

## Pairs with

- `receiving-code-review`/`requesting-code-review` (review mechanics),
  `weinberg-egoless-systems` (egoless culture),
  `staff-engineer-leadership` (technical influence),
  `team-topologies` (team shapes).
