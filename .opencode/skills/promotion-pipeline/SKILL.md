---
name: promotion-pipeline
description: "Governed promotion pipeline skill (scan-unit-regression-sandbox-eval-approval-promote, halt on first failure, journaled runs). Use when a candidate skill, rule, prompt, or config seeks production trust, when a stage must block silently-bad promotions, or when promotion history needs audit. Trigger phrases: 'promote candidate', 'promotion stages', 'earn trust', 'ترقية محكومة'."
---

# Promotion Pipeline (Trust Is Earned in Stages)

Code: `promotion_pipeline.py` (stdlib only). Self-improvement never
equals uncontrolled self-modification: candidates advance scan →
unit → regression → sandbox → eval → approval → promote. First
failure halts with a full stage report; `promote` refuses without an
approval pass on record; crashes halt (never skipped); every run
journals to JSONL.

## When to use

- Auto-created skills/rules/prompts from any learning loop.
- Manual promotions needing staged evidence.
- Post-incident review: the journal shows exactly where a bad
  candidate stopped — or which stage wrongly passed it.

## Verification

- `tests/test_p0c_promotion.py` green (full pass, first-failure halt,
  approval refusal, missing stage, crash halt, fixed order).
- No production trust without a green approval stage on record.

## Pairs with

`agent-readiness-verifier-adapter` (eval content), `skill-trust-registry`
(registration after promote), `immutable-audit-log` (run archive),
`build-gates-pipeline`.
