---
name: static-analysis-testing
description: "Static analysis testing distilled. Use when configuring linters, type checkers, rule tuning, baseline adoption, PR gating."
---

# Static Analysis Testing

## Purpose

Let machines catch the mechanical bugs: linters, type checkers, and rule-based analyzers tuned per repo and gated in CI.

## When to use

Use when the user says 'static analysis', 'lint', 'typecheck', 'mypy', 'eslint', 'ruff', 'rule tuning', 'baseline'.

## Steps

1. Enable linters plus type checkers with repo-tuned rules.
2. Baseline legacy findings; gate new code strictly.
3. Treat analyzer upgrades as events: re-baseline deliberately.
4. Track fix rate; prune rules that never fire usefully.
5. Pair analyzer output with tests, never as a replacement.

## Anti-patterns

- Hundreds of ignored warnings normalized as background.
- Formatting debates blocking meaningful checks.
- Analyzer changes silently re-baselined by automation.
- Static green claimed as tested.

## Example

```bash
ruff check . && ruff format --check .
mypy src --strict
```

## Verification

Rules tuned, baselines versioned, new-code gate strict, fix rate tracked.

## Pairs-with

dast-sast-integration, shift-left-review-patterns, code-smell-detector, code-linter-python-js.
