---
name: philosophy-software-design-ousterhout
description: "Applies Ousterhout deep modules, shallow interfaces, complexity management. Use when designing modules, hiding complexity, reducing cognitive load."
---

# A Philosophy of Software Design (Ousterhout)

Deep modules hide complexity; shallow interfaces expose simplicity.

## Workflow
1. Identify complexity sources (state, coupling, vague interfaces).
2. Design deep module: simple interface, rich hidden behavior.
3. Push complexity down, not up to callers.
4. Measure interface depth vs implementation depth.

## Core Rules
- Information hiding over premature generalization.
- Strategic vs tactical programming.

## Pairs with
- `abstraction-quality-gate`, `clean-architecture`, `pragmatic-programmer`
