---
name: kaner-lessons-testing
description: "Tests context-driven: adapt technique to mission, product, and constraints. Use when the user says 'context-driven testing', 'Lessons Learned', 'Kaner Bach Bret', 'test strategy', 'bug advocacy', 'oracle problem', 'test documentation', or when boilerplate process must yield to judgment."
---

# Kaner Lessons Learned Testing

Distilled from Kaner/Bach/Pettichord *Lessons Learned in Software Testing*
(293 lessons) and the context-driven school: practices serve the MISSION —
there are no best practices, only practices valuable IN a context. Judgment
over ceremony, always.

## Purpose

Build test strategy from context (mission, product risks, constraints), argue
bugs so they get fixed, and document exactly enough — never more, never less.

## The principles that steer (the load-bearing lessons)

1. **Context drives choice.** Every technique's value depends on mission,
   product type, lifecycle stage, and team skill. Anyone selling a practice
   without asking context is selling, not advising. State YOUR context
   before adopting anything (including this skill).
2. **Test for the mission.** Identify what matters most (the risks that
   would sink the release), aim testing there first, and SAY what you are
   NOT covering (coverage claims without scope are fiction). Strategy =
   allocation of finite testing against infinite possibilities.
3. **Bug advocacy: report so it gets fixed.** A bug report is a sales
   document: replicate steps minimal, impact stated in stakeholder terms
   (money/users/data, not "it crashes"), severity argued not asserted.
   Follow up on fixes (regression + surrounding area). Unfixed critical bugs
   are management decisions — make them explicit, in writing.
4. **Oracles are the hard problem.** "How do you know it is wrong?" —
   consistency heuristics answer: history (past versions), image (brand
   promise), comparable products, claims (docs/marketing), user expectations,
   statutes, purpose. No oracle = no test, only execution. Name the oracle
   per test.
5. **Document to the context.** Lightweight (charters, session notes,
   annotated screenshots) for exploration; heavier (plans, traceability)
   where regulation/contracts demand. Documentation serves future testing
   and accountability — write for those readers, delete the rest.
6. **Automate with intent.** Automation checks (machine-verifiable facts),
   humans test (judgment, exploration). Automate for regression economics
   (run often, stable oracle, high cost of manual repeat); never automate
   to "replace testers" — it replaces repetition.

## Verification

Strategy review: context stated, mission + top risks named, oracle per test
approach, automation ROI argued per suite, bug reports sampled for advocacy
quality. Process without context justification is ritual.

## Pairs with

- `hendrickson-explore-it` (exploratory execution),
  `black-risk-based-testing` (risk management),
  `crispin-agile-testing` (agile context),
  `tradeoff-and-postmortem-documenter` (context records).
