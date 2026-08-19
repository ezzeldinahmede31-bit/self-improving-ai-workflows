---
name: how-to-design-programs
description: Applies the How to Design Programs (HtDP) design recipe to any coding task: turn the problem statement into a data definition, design the function signature with a purpose statement, write examples and tests, develop the template from the data structure, fill it in, and test until the examples pass. Use when the user says 'design recipe', 'data definitions', 'signatures', 'purpose statement', 'systematic program design', 'HtDP', 'program by structure', 'design a function', 'types first', or when a program should be designed from the data up instead of improvised.
---

# How to Design Programs (Felleisen et al.)

HtDP makes programming a repeatable process: data definitions drive function design, and tests are written before the implementation. This skill applies the full recipe to any language or n8n expression logic.

## The design recipe

- Start from the problem statement: extract the kinds of data involved and write a data definition for each.
- Give every function a signature and a purpose statement that says what it computes, not how.
- Write examples (tests) from the purpose statement before implementing; they define success.

## Templates from data

- The structure of the data determines the structure of the code: lists suggest recursion, records suggest field access, unions suggest cases.
- Derive the template mechanically, then fill in the details; the template removes the blank-page problem.
- For recursive data, the template includes the recursive call at exactly the recursive position.

## Systematic testing

- Test representative inputs plus edge cases: empty, single-element, degenerate, and extreme values.
- When a test fails, the design recipe says fix the smallest piece: the data definition, the template, or the step in question.
- Keep the examples small enough to run by hand; hand-trace the failing case before changing code.

## Abstraction

- When two functions share structure, abstract the common pattern into a single higher-order function.
- Refactor only with the tests still green; abstraction is verified by the same suite.

## Pairs with
proactive-spec-expander, writing-plans, tdd-sandbox-proof-engine, goos-outside-in-tdd, domain-modeling-functional
