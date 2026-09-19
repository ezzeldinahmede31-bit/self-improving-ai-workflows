---
name: sipser-theory-of-computation
description: "Reasons about what can be computed at all: automata, decidability, and complexity. Use when the user says 'finite automaton', 'DFA', 'NFA', 'regular expression', 'pumping lemma', 'context-free grammar', 'Turing machine', 'decidable', 'undecidable', 'halting problem', 'reduction', 'mapping reduction', 'P vs NP', 'NP-complete', 'Cook-Levin', 'satisfiability', 'Sipser', or when proving a problem solvable/unsolvable or classifying its hardness."
---

# Sipser Theory of Computation

Distilled from Michael Sipser's *Introduction to the Theory of Computation*:
the three questions every hard problem must answer — what model recognizes it,
whether any algorithm decides it, and how much resource it needs.

## Purpose

Give a decision procedure for claims about computability and complexity:
regular vs context-free vs decidable vs hard, with the proof pattern each
level demands.

## The ladder (apply top-down, stop at the first level that fits)

1. **Regular?** Build a DFA/NFA/regex, or prove non-regular with the pumping
   lemma (pick s = a^p b^p shape; every split xyz with |xy|<=p, |y|>0 must
   pump out). Closure wins: complement/union/intersection of regular stays
   regular — prove via product construction, not by rebuilding.
2. **Context-free?** Give a CFG or PDA. Non-CFL proof: pumping lemma for CFLs
   (uvxyz with |vxy|<=p). Note: intersection of two CFLs can leave the family.
3. **Decidable?** Exhibit a decider (TM that always halts), or reduce FROM a
   known undecidable problem (A_TM, HALT). Direction discipline: to prove B
   undecidable, reduce A_TM <=m B (if B were decidable, A_TM would be).
   Rice's theorem shortcut: any nontrivial semantic property of programs is
   undecidable — quote it instead of re-reducing.
4. **Complexity?** Show membership (verifier = NP; decider with poly bound =
   P; log-space transducer = L) then hardness by poly-time reduction from the
   canonical seed (SAT/Circuit-SAT via Cook-Levin, 3SAT, CLIQUE, VERTEX-COVER,
   HAMPATH, SUBSET-SUM). Gadget rule: the reduction must be computable in
   poly time AND preserve yes/no exactly both directions.

## Proof hygiene (what makes a Sipser-grade answer)

- Reductions get a two-direction correctness argument (=> and <=), never one.
- Distinguish decidable vs recognizable vs co-recognizable explicitly.
- Time hierarchy awareness: more time strictly buys power; never claim "needs
  exponential time" from "no poly algorithm known".

## Verification

After classifying: name the level, the witness (automaton/grammar/decider/
reduction), and the theorem used. If any of the three is missing, the answer
is incomplete — go back and supply it.

## Pairs with

- `clrs-np-completeness` (algorithm-side hardness), `formal-math-logic-verification-engine`
  (mechanical proof), `dragon-book-parsing-techniques` (grammar front-ends),
  `algorithmic-math-reasoner` (proof discipline).
