---
name: ammann-offutt-criteria
description: "Applies rigorous coverage: RIP model, logic/input/graph/syntax criteria. Use when the user says 'test coverage criteria', 'RIP model', 'MCDC', 'mutation testing', 'input space partitioning', 'graph coverage', 'Ammann Offutt', or when 'tested' must mean something provable."
---

# Ammann & Offutt Test Criteria

Distilled from Ammann & Offutt *Introduction to Software Testing* (the
university standard): testing = executing with coverage criteria derived
from software structures — Reachability, Infection, Propagation (RIP) decide
whether a test CAN detect a fault; criteria decide whether it WILL.

## Purpose

Replace coverage percentages with criteria subsumption: choose the criterion
each structure demands, and know what weaker criteria miss.

## The RIP model (why tests fail to fail)

A fault is detected only if the test: REACHES the faulty location, INFECTS
program state (wrong intermediate value), PROPAGATES to observable output.
Design reviews ask all three per important fault — a test missing any leg
executes without testing.

## The four structures + their criteria (strongest practical each)

1. **Input space → Input Space Partitioning.** Characteristics (inputs +
   preconditions) partitioned into blocks (valid/invalid/edge); Base Choice
   (one base + vary one dimension — the economical default) vs Pairwise/
   Complete (stronger, costlier). Reuse the partitioning skills for values;
   this skill owns the METHOD selection.
2. **Logic → Logic coverage.** Predicate coverage < clause coverage <
   combinatorial < active clause (each clause determines the predicate
   outcome independently — the avionics-grade MCDC idea). Correlated
   variables need combinatorial; independent ones are served by active
   clause. State the correlation argument or default up.
3. **Graphs → Graph coverage.** Node < edge < edge-pair < prime path (simple
   paths maximal under subsumption — the sweet spot: tours all prime paths
   with few tests; side trips allowed, detours billed). Apply to control
   flow, FSMs, and dataflow (def-use pairs: every definition reaches a use
   tested).
4. **Syntax → Mutation.** Operators that seed realistic faults (statement
   deletion, constant/operator replacement, off-by-one mutations); mutation
   SCORE = killed/(total − equivalent). Equivalent mutants (same semantics)
   identified, not counted. Weak mutation (infection only) for speed,
   strong (full RIP) for critical code.

## Subsumption discipline

Stronger criteria subsume weaker — but cost more tests. Choose per risk:
prime-path + active-clause + strong-mutation for critical logic; base-choice
+ branch for glue. Document the criterion per module (not one suite-wide
percentage) and never compare percentages across different criteria.

## Verification

Coverage plan per module: structure identified, criterion named with its
subsumption argument, RIP walkthrough for key faults, mutation score on
critical paths. "100% line coverage" cited as sufficiency is rejected —
lines are the weakest structure that matters.

## Pairs with

- `copeland-pairwise-testing` (combinatorial method),
  `myers-art-of-testing` (design foundations),
  `beizer-domain-testing` (domain boundaries),
  `claessen-property-testing` (generative coverage).
