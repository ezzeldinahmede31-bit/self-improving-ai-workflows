---
name: formal-math-logic-verification-engine
description: "Deterministic, mechanical verification for math and logic answers using real solver tooling installed in this workspace's venv — math-verify (HuggingFace: parse LaTeX/expressions, prove equivalence, sets/intervals/matrices, the same grader behind the Open LLM Leaderboard and AIME24 evaluation), Z3 (SMT: prove theorems by showing the negation is unsatisfiable, solve constraint systems, verify invariants), python-sat/PySAT (SAT/MaxSAT encodings for combinatorial counting and logic puzzles), and sympy (symbolic algebra, simplification, canonical forms). Turns 'I think the answer is X' into 'X is mechanically equivalent to the required form / the negation is UNSAT / the model satisfies all constraints'. Use whenever a math problem yields a numeric/Latex answer to grade, whenever a logic or constraint question ('can it be done', 'is it possible', 'how many ways', scheduling, packing) can be encoded, or whenever a counting/olympiad answer needs independent proof. Trigger phrases: 'verify the answer', 'prove it with a solver', 'is this possible', 'check equivalence', 'encode this in Z3', 'SAT encoding'. Pairs with math-olympiad, algorithmic-math-reasoner, off-by-one-boundary-guard, self-benchmark-runner."
---

# Formal Math-Logic Verification Engine

Goal: make every quantitative claim mechanically checkable instead of "trusted
reasoning". Installed engines (all in `venv/bin/python`):

| Engine | Import | Proves |
|---|---|---|
| math-verify | `from math_verify import parse, verify, LatexExtractionConfig, ExprExtractionConfig` | answer equivalence (numbers, fractions `1/3` vs `0.333..`, LaTeX, sets, intervals, matrices, relations `a<2 == 2>a`) |
| Z3 | `from z3 import *` | SMT — satisfiability, theorem-by-contradiction, constraints, integer/rational/bitvector reasoning |
| PySAT | `from pysat.formula import CNF` + `from pysat.solvers import Glucose4` | pure Boolean logic, combinatorial counting encoded as SAT, MaxSAT optimization |
| sympy | `import sympy` | symbolic simplification, canonical forms, series, roots, factorizing |

Provenance: math-verify is the HuggingFace grader used for the Open LLM
Leaderboard math rerun and AIME24-style evaluation; Z3 is Microsoft Research's
SMT solver; both are deterministic — no model judgment involved.

## Workflow (run every gate that applies)

1. **Formal restatement** — write the target in canonical form: the exact
   answer expression, or the assertion to prove (P), or the constraint
   system. State which gate will certify it.
2. **GATE A — equivalence grading** (numeric/symbolic answers):
   ```python
   from math_verify import parse, verify, LatexExtractionConfig, ExprExtractionConfig
   gold = parse(r"<required form e.g. 1/3 or \$\\frac{1}{3}\$>", extraction_config=[LatexExtractionConfig()])
   pred = parse(r"<my answer>", extraction_config=[ExprExtractionConfig(), LatexExtractionConfig()])
   assert verify(gold, pred)  # True = mechanically equal
   ```
   Handles intervals `{1,3}∪{2,4} == {1,2,3,4}`, sets, relations, matrices,
   floats vs exact. If parse fails, re-express without `\boxed` clutter first.
3. **GATE B — SMT proof/certification** (theorems, "impossible?" questions):
   ```python
   from z3 import *
   # to prove P: assert Not(P) and expect UNSAT
   # to find x: solve([...constraints...]) → model
   # invariants: encode the step and prove step preserves P
   ```
   Report SAT→counterexample model, UNSAT→P proven.
4. **GATE C — SAT encoding** (counting/possibility logic):
   ```python
   from pysat.formula import CNF
   from pysat.solvers import Glucose4
   # one Boolean per decision; clauses encode constraints; count models by
   # enumerating solutions with assumptions, or use enumerate_models()
   ```
   For MaxSAT-style optimization use `pysat.examples.rc2`.
5. **GATE D — independent re-derivation** (always for olympiad answers):
   solve again with a DIFFERENT representation (brute force, closed form,
   Pigeonhole-style counting). If two methods disagree by exactly 1 →
   boundary/off-by-one bug first (see off-by-one-boundary-guard).
6. **Honest verdict** — label each claim: `PROVEN (gate A/B/C)` vs
   `HEURISTIC (unverified)` vs `DISAGREEMENT: ...`. Never call an answer
   "confirmed" unless at least one mechanical gate passed.

## When to escalate

- Answer needs a formal PROOF (not just the number) → GATE B with full
  invariant encoding; if Z3 is too weak (real analysis, limits), say so —
  do not fake a proof.
- Problem is from IMO/Putnam/USAMO/AIME → pair with `math-olympiad` skill
  (adversarial proof checking) + GATE A to grade the final answer
  mechanically.
- Counting problems with open/closed intervals → `off-by-one-boundary-guard`
  before GATE A.
- Self-benchmark runs → GATE A for all grading (replace hand grading with
  `verify()`).

## Known limits (honest)

- math-verify is not fully symmetric for interval-vs-inequality forms
  (by design); put the required form as `gold`.
- Z3 is undecidable for some theories (nonlinear real arithmetic); fall back
  to specific strategies (NLSat via `set_option`) or note the limit.
- These engines verify what was ENCODED — a wrong encoding yields a wrong
  but confident verdict. Always encode the formal restatement from the
  problem text, never from your own paraphrase of it.