---
name: wiegers-software-requirements
description: "Engineers requirements that survive contact with stakeholders: elicitation, specification, and change control. Use when the user says 'requirements', 'user stories', 'acceptance criteria', 'SRS', 'elicitation', 'scope creep', 'requirements change', 'Wiegers', or when building the wrong thing is the risk."
---

# Wiegers Software Requirements

Distilled from Wiegers & Beatty *Software Requirements*: most project
failures are requirements failures wearing technical costumes. Fix the
requirements process and the technical problems shrink with it.

## Purpose

Produce requirements that are complete, consistent, verifiable, and stable
enough to build against — with change handled as process, not chaos.

## The practice (in project order)

1. **Elicit, don't collect.** Stakeholders state solutions; analysts extract
   needs: interviews with "why" ladders, workshops, observation, prototypes
   as questions. Classes to cover: business requirements (why), user
   requirements (who does what), functional requirements (system behavior),
   quality attributes (how well), constraints (imposed limits). Missing class
   = missing stakeholder found later, expensively.
2. **Specify to be verified.** Every requirement testable: replace vague
   adjectives with measures ("fast" -> "p95 under 300ms at 10x load").
   Shall-statements with unique IDs, traced to source and to design/tests.
   Ambiguity review: a second reader must implement the same thing from the
   same sentence.
3. **Model before building.** Data models, state diagrams, prototypes for
   risky interactions. Models are cheaper than code by an order of magnitude
   and expose contradictions stakeholders nod past in prose.
4. **Baseline and control change.** Versioned baseline + impact analysis per
   change (cost, schedule, ripple) + change board authority. Scope creep is
   not a moral failing — it is an uncontrolled-change process. Control it.
5. **Trace end to end.** Requirement -> design -> code -> test linkage both
   directions. Untraced requirements are unverified; unmapped tests are
   unscoped. Coverage gaps found here, not in production.

## Quality bar (run per requirement)

Necessary, feasible, unambiguous, verifiable, prioritized, traced. Any
requirement failing one attribute is a defect with the same standing as a
code bug — logged, owned, fixed.

## Verification

Requirements review delivers: attribute checklist per requirement,
traceability matrix, change log with impact analyses, and the prioritized
backlog with the current baseline version. Hand-waving about "agreed
understanding" is not an artifact.

## Pairs with

- `patton-story-mapping` (backlog shape), `proactive-spec-expander`
  (implicit requirements), `clarify-before-execute` (discovery loop),
  `cagan-inspired-product` (right-thing validation).
