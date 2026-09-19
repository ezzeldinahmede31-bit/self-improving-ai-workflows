---
name: okken-pytest-craft
description: "Uses pytest professionally: fixtures, parametrize, markers, and plugins. Use when the user says 'pytest', 'fixtures', 'parametrize', 'conftest', 'markers', 'Okken', 'pytest plugins', or when Python tests must scale past a single file."
---

# Okken pytest Craft

Distilled from Brian Okken *Python Testing with pytest*: pytest's power is
fixtures + plain asserts + plugins — write small test functions, compose
context declaratively, and let the runner do the ceremony.

## Purpose

Run this workspace's Python suites (and any Python project) like a pytest
native: expressive, fast, and organized at any scale.

## The craft (in adoption order)

1. **Plain asserts, rich introspection.** `assert a == b` with pytest's
   rewriting (no assertEqual dialect): failure output shows values, diffs,
   and context. Custom messages only where the bare assert misleads.
2. **Fixtures for context.** `@pytest.fixture` over setup/teardown methods:
   narrow-scoped (function default), named by WHAT they provide, composed by
   requesting (fixtures requesting fixtures). `conftest.py` shares across
   directories (nearest wins); `autouse` sparingly (magic context rots
   readability); yield-fixtures for teardown guarantees.
3. **Parametrize the matrix.** `@pytest.mark.parametrize` turns one test
   function into the full input matrix (boundaries + representatives +
   error cases). IDs readable (`ids=` or named tuples) so failures name
   their case. Data-driven, not copy-pasted.
4. **Markers organize runs.** `@pytest.mark.slow/network/db` + `-m` selection
   (fast default suite, full suite on demand); `skip/skipif/xfail` with
   REASONS (unreasoned skips are abandoned tests). This repo's `-m "not e2e"`
   pattern is exactly this discipline.
5. **Plugins, not plumbing.** Coverage (`pytest-cov` with fail-under gates),
   parallelism (`pytest-xdist -n auto` for speed), randomness
   (`pytest-randomly` to catch order dependence), clarity (`-v --tb=short`
   for signal). `pyproject`/ini pins the defaults so every runner agrees.

## Suite hygiene (the Okken rules)

- One behavior per test, names that state it. No logic in tests (no loops/
  branches deciding assertions — parametrize instead). Factories/fakers for
  data (never mystery guests from other tests). Deterministic: seed RNGs,
  freeze time, isolate filesystem (tmp_path), quarantine flakes same-day.

## Verification

Suite check: `pytest -q` green, fast subset identified (`-m`), coverage gate
met on changed code, zero warnings-as-errors ignored without reason, flakes
owned. A red-or-flaky suite blocks its feature — no exceptions.

## Pairs with

- `tdd-sandbox-proof-engine` (this workspace's TDD loop),
  `xunit-test-patterns` (pattern language),
  `test-smells-catalog` (disease diagnosis),
  `terminal-bash-executor-governor` (running suites safely).
