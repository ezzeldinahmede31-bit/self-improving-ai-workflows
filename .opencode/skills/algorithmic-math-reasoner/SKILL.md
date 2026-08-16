---
name: algorithmic-math-reasoner
description: "Raises correctness on hard algorithmic and mathematical problems where a fast model tends to jump to plausible-but-wrong answers: forces formal restatement, invariant/complexity proofs, brute-force cross-validation, and step-graded verification. Use on algorithms, DP/graph/number theory puzzles, math derivations, probabilistic questions, or any 'prove this works' coding task. Trigger phrases: 'prove it', 'is this optimal', 'time complexity', 'algorithm', 'math', 'derive', 'this should be O(n)'."
---

# ALGORITHMIC MATH REASONER

## DIRECTIVE
A fast model's failure mode on hard problems is confidence in a truncated
chain. Break that habit: make the answer a certificate, not a guess. Each hard
problem passes through 5 gates; do not output a solution until all gates close.

## THE 5 GATES
1. **Formal Restatement.** Rewrite the problem in precise terms (inputs,
   constraints, invariants, target). Fix loose words ("basically", "just").
   Any ambiguity is resolved BEFORE writing code — write the assumption down.
2. **Strawman + Attack.** Produce the naive/brute-force solution first. State
   its complexity, then ATTACK it: find the input where it fails or explodes.
   This reveals the real bottleneck the optimized solution must beat.
3. **Invariant & Complexity Proof.** For the optimized solution, state:
   - the invariant that holds at every loop iteration,
   - the amortized argument (why the total is O(...), not just each step),
   - a small adversarial case that exercises the worst case.
   If you cannot write these, the solution is not finished.
4. **Brute-force cross-validation.** For anything with a computable brute
   force, generate random small inputs and assert optimized == brute-force on
   every one (property test, e.g., 100–1000 random cases). Run it — do not
   hand-wave it. This is the single biggest correctness win.
5. **Step-graded self-check.** Walk the final code line by line pretending to
   be the machine on a traceable small input (paper trace). Fix mismatches.
   Then state the final time/space complexity with a one-line justification.

## RULES
- If a step fails, STOP and correct rather than bulling forward.
- Never claim optimality without the amortized argument + adversarial case.
- Evidence over memory: paste the actual randomized cross-check output.
- For math: verify identities by numeric evaluation (sympy/numpy) where
  possible before trusting symbolic re-arrangements.

## Local adaptation
This workspace has `venv` with numpy available for property checks via a quick
script in `/tmp` (never commit it). The real suite stays green:
`venv/bin/python -m pytest` (269 passing). Combine with
`frontier-deep-reasoner` when the reasoning is qualitative, and with
`tradeoff-and-postmortem-documenter` to record the certified result in
`KNOWN_ISSUES.md` if a subtlety emerged.