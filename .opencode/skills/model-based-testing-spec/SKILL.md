---
name: model-based-testing-spec
description: "Model-based testing distilled. Use when generating tests from models, statecharts, usage models, abstract cases to executable scripts."
---

# Model-Based Testing

## Purpose

Generate tests from an explicit behavior model (statechart, usage flow) so coverage follows the model and gaps in the model become visible requirements work.

## When to use

Use when the user says 'model-based testing', 'MBT', 'test generation', 'usage model', 'statechart testing', 'GraphWalker'.

## Steps

1. Build a small honest model of the behavior under test.
2. Define generation: random walk, coverage of edges, or targeted paths.
3. Map abstract steps to executable adapters once.
4. Generate, execute, and investigate divergences as model-or-code bugs.
5. Keep the model beside the code and review it on behavior changes.

## Anti-patterns

- Modeling the implementation instead of the required behavior.
- Giant models nobody reviews.
- Generated tests checked in as thousands of frozen scripts.
- Adapters so thick they hide real divergences.

## Example

Model edge: idle --login--> active. Adapter:

```python
def step_login(ctx):
    ctx.session = login(ctx.user)
    assert ctx.session.active
```

## Verification

Model reviewed, generation strategy stated, divergences triaged as model or code bugs, adapters thin.

## Pairs-with

state-transition-testing, ammann-offutt-criteria, adzic-specification-by-example, flaky-test-elimination.
