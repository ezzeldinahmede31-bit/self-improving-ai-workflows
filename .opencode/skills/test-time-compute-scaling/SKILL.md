---
name: test-time-compute-scaling
description: "Brings frontier-level accuracy to a fast/cheap model on HARD problems only, using test-time scaling: generate multiple independent solution paths in parallel, then select via verifiers (execution-based check, step-level self-verify, self-consistency vote) instead of trusting one pass. Use ONLY when a problem demonstrably exceeds single-pass reliability (deep algorithms, tricky math, system-level design, subtle bugs that survive one attempt). Trigger phrases: 'this needs deep reasoning', 'be very careful with this algorithm', 'double-check the math', 'I keep getting this wrong'."
---

# TEST-TIME COMPUTE SCALING

## PRINCIPLE (evidence-backed)
OpenAI/DeepSeek research show accuracy scales with test-time compute ONLY when
paired with a reward/verifier — pure imitation or best-effort one-pass does not
turn extra tokens into correctness. Multi-path sampling pays off ONLY on
problems past the model's single-pass ceiling; on easy problems it adds noise
and cost. This skill therefore: (1) gates on difficulty, (2) samples in
parallel, (3) picks with a VERIFIER, never by vibes.

## GATE FIRST: is this a hard problem?
Route to this skill ONLY if: multi-step with several plausible-looking wrong
paths · subtle math/algorithm/invariant · a bug that survived one attempt ·
data/structure errors possible. For routine edits, auto-format, or trivia:
STOP — do a normal single pass (scaling easy tasks is the documented
diminishing-returns trap).

## PROTOCOL
1. **Decouple generation from selection.** Generate 3–5 INDEPENDENT candidate
   solutions (restart reasoning each time; vary framing: code-first vs
   proof-first vs example-driven). Keep each candidate self-contained.
2. **Verify with ground truth when possible (strongest):**
   - Code → run against test cases / brute-force cross-check on random inputs
     (property tests). Execution is the most reliable verifier there is.
   - Math → numeric/symbolic check (numpy/sympy) of the result.
3. **Where no executor exists, verify by structure (self-consistent vote):**
   majority answer over the candidates beats any single chain. Also apply
   step-level self-verify (ReVISE-style): for the WINNING candidate, replay
   each step, flag any step you cannot justify, correct, re-run only that step.
4. **Escalate, don't fake:** if candidates disagree and no executor can decide,
   hand to `elite-verifier-delegation` (a stronger judge) or state the tie
   honestly instead of picking by confidence-feel.

## COST RULES
- 3 paths max on medium-hard, 5 on genuinely hard; never 20 (the paper shows
  >15 paths "adds noise not signal").
- Stop as soon as the verifier confirms one candidate (early exit).
- This is a scalpel: it must not slow the 90% of easy daily work.

## Local adaptation
Run the 3–5 generations as parallel `task` sub-agents (isolated context) or as
one scripted loop over a prompt template — both keep the main context lean.
Use `venv` (numpy available) for property checks. When the subject is
workflow/code in this repo, final gate = `venv/bin/python -m pytest`.
Companion skill: `algorithmic-math-reasoner` supplies the gates; this skill
supplies the multi-path scaling + verifier selection around them.