---
name: zeller-fuzzing-book
description: "Fuzzes with structure: mutational, generational, and coverage-guided fuzzing. Use when the user says 'fuzzing', 'AFL', 'libFuzzer', 'grammar fuzzer', 'coverage-guided', 'Fuzzing Book', 'Zeller fuzzing', or when parsers and protocols must survive hostile input."
---

# Zeller Fuzzing Book

Distilled from Zeller et al. *The Fuzzing Book* (fuzzingbook.org): random is
weak, coverage-guided is strong, grammar-aware is strongest. Climb the
ladder deliberately; measure coverage, not crashes-per-hour.

## Purpose

Find robustness bugs automatically in anything that parses input: files,
protocols, APIs, interpreters — with harnesses that run forever in CI.

## The ladder (climb until coverage plateaus)

1. **Blackbox random (baseline).** Random bytes/values at the input: finds
   the shallowest crashes in an afternoon. Value: instant harness + seed
   corpus habit. Limitation: never passes checksums/magic bytes — expect the
   plateau fast.
2. **Mutational with corpus.** Mutate valid seeds (bit flips, splices,
   dictionaries of protocol tokens): passes shallow checks, explores
   neighborhoods. Corpus hygiene: minimize (smallest inputs covering the
   same edges), refresh from production samples periodically.
3. **Coverage-guided (greybox: AFL++/libFuzzer).** Instrument edges; keep
   inputs discovering NEW coverage. Harness rules: fuzz the library entry
   (not main), deterministic (fixed seeds, no wall-clock), fast (thousands
   of execs/sec — profile the harness itself), persistent mode where
   available. Sanitizers ON (ASan+UBSan minimum): coverage finds paths,
   sanitizers find the bugs on them.
4. **Generational/grammar-based.** Grammar describing valid inputs (JSON,
   expressions, protocols): generates deep valid cases greybox never
   reaches; combine (grammar seeds INTO coverage fuzzer = best of both).
   Stateful targets get protocol-state grammars (sequences, sessions).
5. **Differential/oracle layer.** No-crash ≠ correct: differential testing
   (two implementations must agree), metamorphic relations, assertion oracles
   inside the harness. Crashes are the floor of fuzzing value.

## CI integration (fuzzing that lives)

- Short runs per commit (minutes, regression corpus must stay green),
  long runs nightly/weekly (new coverage triaged like test failures),
  crash deduplication (stack-hash bucketing) before human eyes, minimized
  reproducers checked in as regression tests. OSS-Fuzz model for critical
  parsers.

## Verification

Fuzzing review: harness speed + determinism stated, sanitizers enabled,
coverage trend rising (then maintained), corpus minimized, crashes-to-
regression-tests pipeline demonstrated. A fuzzer nobody triages is a space
heater.

## Pairs with

- `alephone-binary-exploitation` (what found bugs cost),
  `zeller-why-programs-fail` (from crash to cause; delta-debug the repro),
  `testing-qa-version-control-rpa-v2` (CI integration),
  `okken-pytest-craft` (Python harnesses via hypothesis/atheris).
