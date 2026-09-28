---
name: prompt-regression-gate
description: "Prompt regression gate skill (versioned prompts, frozen goldens, blocking old-vs-new compare). Use when a prompt changes, when a model swaps under a prompt, or when deploy must stop on quality loss. Trigger phrases: 'prompt regression', 'golden set', 'block deploy', 'انحدار البرومبت'."
---

# Prompt Regression Gate (Goldens Block Deploys)

Code: `prompt_regression.py` (stdlib only). Versions hold template +
model fn; goldens hold frozen inputs + checkers; `compare(old, new)`
reports rates, delta, regression/fix lists, and blocked (any lost case
or delta beyond tolerance stops the rollout).

## Verification

- `tests/test_p1a_regression_behavior.py` regression half green
  (blocking loss, stable pass).
- Threshold changes are reviewed; goldens edited only via PR rationale.

## Pairs with

`promptfoo-eval-redteam-adapter` (scale + security), `model-drift-watch`,
`evaluation`, `build-gates-pipeline`.
