---
name: llm-eval-harness
description: "LLM evaluation harness distilled. Use when building eval sets, golden answers, judge calibration, regression suites for prompts and models."
---

# LLM Eval Harness

## Purpose

Evaluate LLM features honestly: versioned eval sets, golden answers, calibrated judges, regression runs per prompt or model change.

## When to use

Use when the user says 'LLM eval', 'eval set', 'golden answers', 'judge calibration', 'prompt regression', 'model comparison'.

## Steps

1. Build eval sets from real user tasks with golden answers plus rubrics.
2. Calibrate judges against human labels before trusting scores.
3. Run evals per prompt, model, and retrieval change as a gate.
4. Track score trends with failure buckets per release.
5. Keep a red-team slice probing safety and refusal behavior.

## Anti-patterns

- Eval sets written by the same prompt being tested.
- Judge scores trusted without human calibration.
- One aggregate score hiding task-family regressions.
- Evals run once and never gated.

## Example

Harness record: task, input, golden, rubric, judge verdict, human spot-check flag.

## Verification

Sets versioned, judges calibrated, gates enforced, trends tracked with buckets.

## Pairs-with

evaluating-llms-benchmarks-metrics, prompt-engineering-llm-apps, rag-eval-faithfulness, prompt-regression-testing.
