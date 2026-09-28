---
name: adversarial-suite
description: "Adversarial suite skill (11-case attack corpus with expected verdicts, detector grading). Use when grading defenses, when expanding beyond injection-only tests, or when a new attack family needs a regression case. Trigger phrases: 'run adversarial suite', 'grade detector', 'attack corpus', 'مجموعة الهجمات'."
---

# Adversarial Suite (Grade the Defenses)

Code: `adversarial_suite.py` (inert strings, no live exploits).
11 cases across 9 families (direct/indirect injection, tool/data/
context/memory poisoning, malicious URL/file, fake output, conflict,
priv-esc) each with an expected verdict (block/quarantine/flag/
re-verify/escalate). `run_suite(detector_fn)` grades pass/fail;
crashing detectors fail their cases.

## Verification

- `tests/test_p1b_adversarial_saga.py` adversarial half green.
- New families append cases with expectations (never payload-only).

## Pairs with

`promptfoo-eval-redteam-adapter` (scale), `agent-runtime-guard-adapter`
(enforce), `promotion-pipeline` (regression), `build-gates-pipeline`.
