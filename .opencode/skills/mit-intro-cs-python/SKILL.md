---
name: mit-intro-cs-python
description: "Teaches computation from zero the MIT 6.0001 way: state, control flow, decomposition, and growth rates. Use when the user says 'learn programming', 'intro to CS', 'Python basics', 'functions', 'recursion', 'bisection search', 'bubble sort', 'orders of growth', 'classes intro', 'plotting', 'MIT 6.0001', or when anyone starts computer science from scratch."
---

# MIT Intro CS in Python

Distilled from MIT 6.0001 (Guttag): computation = state + control + abstraction.
Five ideas carry the whole introductory course.

## Purpose

Take a beginner from zero to writing, testing, and analyzing small programs —
with the mental models that every later course assumes.

## The five ideas

1. **State and binding.** Variables are names bound to objects; mutation
   aliases. Draw the state diagram before running the code in your head —
   aliasing bugs die here.
2. **Control exhausts cases.** Branching + bounded/unbounded loops. Loop
   discipline: invariant (what stays true), progress (what shrinks), exit
   (why it must terminate). Enumerate-and-check first, optimize later.
3. **Decompose and abstract.** Functions with contracts (pre/post); modules
   hide detail. Top-down design, bottom-up testing. A function longer than
   what fits in your head is two functions.
4. **Growth rates early.** Orders of growth (constant/log/linear/nlog/n²/
   exponential) decide feasibility before code exists. Bisection beats linear
   search; insertion/selection sort teach analysis, not production sorting.
5. **Data + classes + experiments.** Tuples/lists/dicts model the world;
   classes bundle state with behavior (intro to OOP). Testing = break it on
   purpose (edge inputs, not happy paths). Plot results: a picture exposes a
   wrong complexity class instantly.

## Study protocol

- Every concept ships with a 10-line program YOU write, then a prediction of
  its output before running (prediction errors are the lesson).
- Debug by bisection on the code: halve the suspect region with prints or a
  debugger until the wrong state is cornered.

## Verification

Learner can: trace any loop's invariant, state any function's contract, name
the complexity class of their code, and write a failing-then-passing test.
Otherwise the topic is not done.

## Pairs with

- `how-to-design-programs` (design recipes), `tdd-sandbox-proof-engine`
  (testing discipline), `think-stats` (plotting data),
  `zeller-why-programs-fail` (debugging science).
