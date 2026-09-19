---
name: forallx-formal-logic
description: "Proves with formal logic: propositional and first-order syntax, semantics, and deduction. Use when the user says 'formal proof', 'natural deduction', 'soundness', 'completeness', 'first-order logic', 'quantifiers', 'validity vs satisfiability', 'for all x', 'forallx', or when an argument needs machine-grade rigor."
---

# forallx Formal Logic

Distilled from P.D. Magnus *forallx* (Open Logic Project tradition):
propositional + first-order logic with natural deduction — the shared
foundation under program verification, databases, and AI knowledge
representation.

## Purpose

Turn informal arguments into checkable proofs, and know exactly what a
formal system can and cannot deliver.

## The system (build in this order)

1. **Propositional logic.** Syntax (connectives, well-formed formulas),
   truth-table semantics, validity vs satisfiability vs entailment. Normal
   forms (CNF/DNF) as the bridge to computation (SAT solvers eat CNF).
2. **Natural deduction.** Introduction/elimination rules per connective;
   assumptions discharged by ->Intro and ¬Intro; proof by contradiction done
   right. Strategy: work backward from the goal connective, forward from the
   premises, meet in the middle.
3. **First-order logic.** Predicates, quantifiers, scope; the four quantifier
   rules (∀Elim/∀Intro with eigenvariable discipline, ∃Intro/∃Elim). Most
   invalid "proofs" die on eigenvariable violations — check every ∀Intro.
4. **Identity and descriptions.** =Elim/=Intro (substitution of identicals);
   definite descriptions as existence+uniqueness claims. Equality reasoning
   is where informal math hides its gaps.
5. **Metatheory (what the system promises).** Soundness (provable -> true in
   all models): trust the rules. Completeness (true in all models ->
   provable): the rules suffice. Compactness and Löwenheim-Skolem as
   orientation: FOL cannot pin down infinite structures uniquely — know this
   before promising a "complete specification".

## Proof discipline

- State the goal's main connective first; it dictates the strategy.
- Flag every discharged assumption with its line range — undischarged
  assumptions are unsoundness waiting to happen.
- Countermodel habit: to show INVALIDITY, build one interpretation where
  premises hold and conclusion fails. One countermodel beats pages of failed
  proof attempts.

## Verification

Each proof ships with: rule cited per line, discharge ranges marked, and (for
invalidity claims) an explicit countermodel. Uncited steps are gaps, not
proofs.

## Pairs with

- `formal-math-logic-verification-engine` (machine-checked proofs),
  `sipser-theory-of-computation` (decidability of fragments),
  `prolog-logic-programming` (logic as execution),
  `mathematics-for-computer-science` (proof methods).
