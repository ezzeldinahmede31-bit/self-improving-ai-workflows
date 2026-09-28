---
name: golden-corpus
description: "Golden failure corpus skill (permanent past-failure cases, blocking update gate, uncovered-case alarm). Use when a fixed bug must never return, when an update needs history proof, or when a case lacks a check. Trigger phrases: 'golden corpus', 'never regress', 'failure history', 'المدونة الذهبية'."
---

# Golden Corpus (Past Failures Stay Fixed)

Code: `golden_corpus.py` (stdlib only, separate JSON store).
`add_case()` freezes reproducer + expectation + incident/fix refs;
`gate_update()` runs checks per case — any miss OR any uncovered case
blocks the change. History is append-mostly, never rewritten.

## Verification

- `tests/test_p2b_guards_golden.py` corpus third green (block on
  regress, uncovered alarm, persistence).
- Updates cite corpus verdicts, not just the present suite.

## Pairs with

`promotion-pipeline` (promotion gate), `adversarial-suite` (attack
cases feed the corpus), `root-cause-post-mortem-analyzer`,
`build-gates-pipeline`.
