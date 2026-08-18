---
name: pragmatic-programmer
description: "Applies Hunt & Thomas' The Pragmatic Programmer to everyday engineering craft: DRY (every piece of knowledge has one authoritative expression), orthogonality (changes in one area do not leak into others), reversibility (decisions stay undoable), tracer bullets for learning by working, prototypes, domain languages, deliberate estimation, and the personal discipline of caring about the work. Use when the user says 'DRY', 'orthogonality', 'reversibility', 'tracer bullet', 'prototype', 'domain language', 'estimate this task', 'pragmatic programmer', 'rubber duck', 'technical debt', 'broken window', 'write code that is easy to change', or when improving code craft and maintainability. Pairs with: code-smell-detector, orthogonality-guard, reversibility-engine, professional-conduct-gate, clean-code-alignment-methodology."
---

# The Pragmatic Programmer

The premise: pragmatism is taking responsibility for your work — every artifact
you produce is your signature, and the craft is a set of habits that keep code
easy to change.

## When to use

- Improving maintainability and reducing coupling in a codebase.
- Deciding how to approach an unfamiliar problem (tracer bullet vs prototype vs
  full design).
- Estimating work or explaining technical debt.

## The core principles

1. **DRY** — every piece of knowledge has a single authoritative expression in
   the system; duplication of knowledge (not of code) is the smell. The fix is
   often a new abstraction, not a shared snippet (see `code-smell-detector`).
2. **Orthogonality** — design so a change in one area leaves the others
   untouched; test for it, keep components independent (see `orthogonality-guard`).
3. **Reversibility** — make decisions that can be undone; hide interfaces behind
   seams so a later swap is cheap (see `reversibility-engine`).
4. **Broken window** — fix small defects immediately; one tolerated break invites
   more. The mess is contagious.
5. **DRY for decisions** — a decision (a policy, a default, a constant) expressed
   in one place, so changing it changes the whole system consistently.

## Working methods

- **Tracer bullets**: build a thin vertical slice through the whole system early
  and keep extending it — the shell learns real constraints while delivering
  working increments (see `goos-outside-in-tdd`).
- **Prototypes**: throwaway spikes to learn a specific answer (cost, performance,
  UX); the point is the learning, and a prototype is meant to be discarded, not
  grown.
- **Domain languages**: model the problem in the language of its domain; a small
  DSL beats a pile of configuration (see `sicp-abstraction-and-interpretation`).
- **Rubber duck**: explain the problem aloud to force the diagnosis out of your
  own head before changing code.

## Estimation

- Estimate in units of the deliverable (time, bytes, money), state the confidence
  band, and refine as more is known.
- Break the task down until an estimate is a sum of smaller, known quantities; the
  detail IS the accuracy (see `high-output-management`).

## Personal discipline

- Care about your work: do not ship mediocre code because you were not asked for
  better.
- Keep learning deliberately; refactor early and often; write down what you learn
  (see `durable-experience-consolidator`).

Pairs with: code-smell-detector (DRY/smells), orthogonality-guard (coupling
checks), reversibility-engine (undoable design), professional-conduct-gate (craft
discipline), clean-code-alignment-methodology (skill authoring).