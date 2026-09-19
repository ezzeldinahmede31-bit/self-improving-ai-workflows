---
name: prompt-regression-testing
description: "Prompt regression testing distilled. Use when versioning prompts, snapshot outputs, diff review, canary rollout, rollback for LLM behavior."
---

# Prompt Regression Testing

## Purpose

Ship prompt changes safely: versioned prompts, snapshot outputs, diff review, canary rollout, instant rollback.

## When to use

Use when the user says 'prompt regression', 'prompt versioning', 'snapshot prompt', 'canary prompt', 'prompt rollback'.

## Steps

1. Version every prompt with its model plus parameters.
2. Snapshot outputs on a fixed probe set per version.
3. Review diffs deliberately; approve meaning changes, reject drift.
4. Roll out new prompts as canaries with guard metrics.
5. Roll back instantly on guard breach with the prior version pinned.

## Anti-patterns

- Prompts edited live with no version history.
- Output changes merged without diff review.
- Full rollout of untested phrasing.
- No pinned prior version to roll back to.

## Example

Probe record: prompt version, model, probe input, output hash, reviewer verdict.

## Verification

Versions pinned, diffs reviewed, canary guarded, rollback proven.

## Pairs-with

llm-eval-harness, prompt-engineering-llm-apps, llmops-production, release-readiness-gates.
