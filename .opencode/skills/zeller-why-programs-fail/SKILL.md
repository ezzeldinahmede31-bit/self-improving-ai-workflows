---
name: zeller-why-programs-fail
description: "Debugs systematically like a scientist: reproduce, hypothesize, predict, experiment. Use when the user says 'it fails', 'find the bug', 'why does this crash', 'bisect the failure', 'delta debugging', 'reproduce', 'intermittent bug', 'Zeller', or when any defect needs a cause rather than a guess."
---

# Zeller Why Programs Fail

Distilled from Andreas Zeller's *Why Programs Fail*: debugging is the
scientific method applied to code — and most time is wasted on steps the
method would have skipped.

## Purpose

Replace guessing with a cause-effect chain: from failure circumstances to the
defect, with each link backed by an experiment.

## The process (never skip or reorder)

1. **REPRODUCE first.** No repro = no debugging. Capture the exact input,
   environment, and schedule. Make it deterministic (seed RNGs, fix thread
   interleavings where possible, shrink the input while the failure persists).
2. **HYPOTHESIZE one cause.** State it falsifiably: "the crash happens
   BECAUSE x is null when y runs before z" — not "maybe it's the database".
3. **PREDICT an observation.** "If my hypothesis holds, then changing X will
   change the failure in way W." A hypothesis with no testable prediction is
   a guess wearing a lab coat.
4. **EXPERIMENT minimally.** Change one variable. Binary-search the input
   (delta debugging: ddmin halves the failing input while preserving the
   failure). Bisect the code (`git bisect`), the config, the data.
5. **OBSERVE and update.** Confirmed -> trace the cause-effect chain one link
   deeper (infection chain: defect -> infection -> failure). Refuted ->
   discard completely and form a NEW hypothesis. Never patch the symptom and
   declare victory.

## Tooling per stage

- Repro: minimal failing test, recorded inputs, containerized env.
- Isolation: delta debugging (input), bisect (history), feature flags (code).
- Observation: assertions as executable hypotheses, watchpoints, tracing,
  cause-effect logging (what value, where born, where observed).
- Prevention: the found chain becomes a regression test + an assertion at the
  infection point, not just at the crash site.

## Verification

Deliverable per bug: repro steps, the confirmed chain (defect -> infection ->
failure), the fix at the DEFECT (not the failure site), and a regression
test. If any link is "probably", the job is not done.

## Pairs with

- `code-execution-guided-swemaster` (REPRO-first execution loop),
  `root-cause-post-mortem-analyzer` (post-fix analysis),
  `tdd-sandbox-proof-engine` (regression tests), `xunit-test-patterns`.
