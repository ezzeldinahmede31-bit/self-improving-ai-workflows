---
name: test-data-management
description: "Test data management distilled. Use when seeding data, factories, fixtures, hermetic datasets, privacy-safe data, parallel isolation."
---

# Test Data Management

## Purpose

Give every test the data it needs without coupling: factories for shape, seed scripts for flows, hermetic datasets per run, privacy-safe values always.

## When to use

Use when the user says 'test data', 'factories', 'fixtures', 'seed data', 'hermetic test', 'data isolation', 'PII in tests'.

## Steps

1. Build data with factories (valid by default, overridable per test).
2. Seed flow-level scenarios with scripts, not UI clicking.
3. Isolate parallel runs: unique namespaces or transactions per worker.
4. Scrub real data: synthetic values for names, ids, and payment fields.
5. Version datasets with the schema migrations they match.

## Anti-patterns

- Shared staging rows mutated by parallel tests.
- Production dumps with real personal data in tests.
- UI-driven setup for every test (slow, brittle).
- Hardcoded ids colliding across suites.

## Example

Python (factory_boy style):

```python
user = UserFactory(admin=True)  # valid default, override per test
```

JS: `faker`-based builders with per-test seeds.

## Verification

Factories default-valid, parallel runs isolated, no real personal data, datasets versioned with migrations.

## Pairs-with

flaky-test-elimination, pairwise-advanced-constraints, test-environment-management, validation-gate-data-quality.
