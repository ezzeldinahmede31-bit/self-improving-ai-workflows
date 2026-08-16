---
name: elite-verifier-delegation
description: "When a fast model must reach frontier-level certainty, delegate VERIFICATION (not generation) to a stronger model: generate cheap here, then have the strongest available model judge, attack, or certify the result. Exploits the research finding that a good verifier beats a good generator — the flash model generates fast/free, the elite model only reads and adjudicates. Use when 'get a second opinion', 'have a stronger model review this', 'certify this is right', 'I want an expert check'. Trigger phrases: 'second opinion', 'expert review', 'verify with a stronger model', 'certify', 'adversarial review'."
---

# ELITE VERIFIER DELEGATION

## DIRECTIVE
You do not need to BE the smartest model — you need to WIRE to the smartest
available one at the one place it matters: verification. Generation is cheap
here (fast, free, parallel); verification is where frontier depth pays.
Generate broadly yourself, then hand the FINAL answer to a stronger judge.

## WHEN
- The answer is checked but you lack an executor (no tests, no brute force,
  pure reasoning/design/architecture).
- Candidates disagree and you must break the tie.
- High-stakes output (production security, financial, published content).
- User explicitly asks for a stronger model's review.

## PROTOCOL
1. **Prepare the submission** — compress the question + your candidate(s) +
   your reasoning + the specific doubt, so the judge spends its depth on the
   hard 20%, not restating the problem.
2. **Ask for adversarial verdicts, not praise:** instruct the reviewer to
   ATTACK the answer (find the counterexample, the edge case, the flaw) and
   to answer 'correct / incorrect / correct-with-caveats' before any prose.
3. **Route to the best available verifier:**
   - If the environment has a stronger model available (Claude/Opus-class via
     API, a local bigger model, another agent): use it.
   - If none is reachable, use the structural verifiers from
     `test-time-compute-scaling` (execution, brute-force, self-consistency) and
     say so honestly — never pretend an external expert checked it.
4. **Reconcile:** if the verifier finds a flaw, fix the candidate, then
   re-submit only the changed part (don't burn the judge on unchanged work).

## RULES
- The elite model is a VERIFIER, not the author: do the generation yourself so
  the strong model's budget is spent on checking, not writing.
- Never claim 'verified by X' unless X actually ran — evidence over memory.
- If no stronger verifier exists, deliver the self-checked result and label
  the confidence explicitly (e.g., 'execution-verified' vs 'unverified').

## Local adaptation
This workspace currently has ONLY the fast/free model — so the default path
here is execution/brute-force/self-consistency verification. Keep this skill
ready: the moment the user connects a stronger model (API key, provider in
`opencode.jsonc`), the same protocol upgrades from internal checks to a real
frontier judge without changing the workflow. Pair with
`test-time-compute-scaling` (generation side) and `multi-agent-consensus-engine`
(when 2+ cheap judges beat one expensive one).