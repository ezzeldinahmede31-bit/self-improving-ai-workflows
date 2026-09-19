---
name: spinellis-code-reading
description: "Reads code like a reviewer-archaeologist: structure, idioms, and intent recovery. Use when the user says 'read this codebase', 'understand legacy code', 'code walkthrough', 'how does this work', 'Spinellis', 'Code Reading', or when joining unfamiliar code that must be modified safely."
---

# Spinellis Code Reading

Distilled from Diomidis Spinellis *Code Reading* (with *Code Quality* as the
grading lens): reading is a distinct skill from writing — systematic,
layered, hypothesis-driven — and it is how unfamiliar code becomes safely
modifiable.

## Purpose

Build a correct mental model of unknown code fast, then change it without
breaking what you did not yet understand.

## The reading protocol (top-down, then bottom-up to verify)

1. **Reconnaissance pass.** Repository shape, build system, entry points,
   README/docs currency, test presence and health. Answer: what IS this,
   how big, is it alive? Time-box this pass — breadth first.
2. **Architecture pass.** Module map (dependency direction!), layering,
   major data flows, external interfaces. Draw the boxes-and-arrows yourself;
   the drawing IS the understanding. Flag layering violations immediately —
   they predict bug clusters.
3. **Idiom pass.** Learn the codebase's dialect: naming conventions, error
   patterns, resource discipline, framework idioms in use. Read WITH the
   grain first (assume competence) — contempt blinds reviewers to intent.
4. **Hypothesis-driven deep dives.** For each change area: form the hypothesis
   ("auth flows through X into Y"), then verify bottom-up (trace the actual
   calls/data). Disconfirmed hypothesis = progress, not failure — record it.
5. **Quality grading (Spinellis lens).** Readability, structure, efficiency
   honesty, security posture, testability — graded per module to aim the
   refactor budget where reading hurt most.

## Change rules for foreign code

- Characterization tests BEFORE behavior changes (lock current behavior,
  then move). Smallest diff that achieves the goal; no drive-by refactors
  in the same commit. Every assumption discovered becomes an assertion or a
  comment — the next reader starts where you finished.

## Verification

Onboarding/reading deliverable: module map diagram, idiom list, hypothesis
log (confirmed + refuted), quality grades, and the characterization tests
added. "I read it" without artifacts is tourism.

## Pairs with

- `ast-codebase-graph-navigator` (mechanical mapping),
  `codebase-mind-persistence` (persisting the model),
  `legacy-code-characterization` (safe-change discipline),
  `code-smell-detector` (quality signals).
