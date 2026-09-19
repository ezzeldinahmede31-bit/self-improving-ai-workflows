---
name: ai-powered-testing-patterns
description: "AI-powered testing distilled. Use when generating tests with AI, self-healing locators, visual regression, flaky triage, LLM-as-judge for oracles."
---

# AI-Powered Testing Patterns

## Purpose

Use AI where it beats hand-code: test generation from stories, self-healing locators, visual regression, flake triage, oracle assistance — with human verification gates.

## When to use

Use when the user says 'AI testing', 'self-healing', 'visual regression', 'generate tests', 'flaky triage', 'LLM oracle', 'AI QA'.

## Steps

1. Generate candidate tests from user stories/code diffs; human approves before merge.
2. Apply self-healing locators with pinned fallback chain (role -> label -> test-id).
3. Add visual regression with tight masks (dynamic regions ignored) + pixel-diff budget.
4. Triage flakes with AI clustering; fix root cause, never auto-mute twice.
5. Use LLM-as-judge only as a second oracle with deterministic checks primary.

## Anti-patterns

- Merging AI-generated tests without review.
- Self-healing that silently follows the wrong element.
- Full-page visual diffs on dynamic content.
- LLM verdict as the only assertion.

## Example

```python
# deterministic primary + LLM secondary
assert resp.status_code == 200
verdict = llm_judge("Does this order total match the story?", resp.json())
assert verdict["match"] is True
```

## Verification

AI tests reviewed, healing events logged, visual baselines versioned, primary assertions deterministic.

## Pairs-with

evaluating-llms-benchmarks-metrics, evaluating-rag-faithfulness-metrics, playwright-modern-automation, test-smells-catalog.
