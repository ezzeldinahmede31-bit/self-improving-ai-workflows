---
name: gof-design-patterns
description: "Applies the Gang of Four Design Patterns (Gamma, Helm, Johnson, Vlissides) to n8n workflows and code: creational (Factory, Singleton, Builder, Prototype), structural (Adapter, Facade, Decorator, Proxy, Composite), and behavioral (Strategy, Observer, Template Method, Command, State, Iterator, Mediator) patterns mapped to automation nodes and services. Prevents over-engineering by matching each pattern to a concrete problem signature. Use when the user says 'design pattern', 'factory', 'adapter', 'strategy pattern', 'observer', 'template method', 'how should I structure this', 'clean design', or when repeated structure suggests a known solution. Pairs with: abstraction-quality-gate, zero-trust-modular-decomposer, api-design-patterns, dependency-inversion-enforcer."
---
# GoF Design Patterns

The Gang of Four (GoF) catalog applied to n8n automation and service code. The goal is NOT to force patterns - it is to recognize the problem signature and apply the minimal pattern that solves it. Over-engineering (a pattern for every whim) is itself an anti-pattern.

## When to Use a Pattern (GoF: 'Program to an interface, not an implementation')

| Problem signature | Pattern family | n8n / code application |
|---|---|---|
| Object creation varies or is parameterized | Creational (Factory) | A node whose config is built by a Code node based on input |
| Need one shared instance | Creational (Singleton) | One shared webhook URL / one shared credential wrapper |
| Different interfaces need to talk | Structural (Adapter) | Code node wrapping an API into the shape the next node expects |
| Interchangeable behavior at runtime | Behavioral (Strategy) | A Switch/IF node selecting among execution paths |
| One change must notify many | Behavioral (Observer) | Webhook fan-out to multiple subscribers |
| Steps have fixed order but vary | Behavioral (Template Method) | Pipeline skeleton with replaceable step nodes |
| Undo/redo needed | Behavioral (Command) | Reversibility Engine rollback commands |

## The GoF Decision Rule (avoid pattern abuse)

1. State the problem in one sentence WITHOUT pattern vocabulary.
2. If a plain solution exists (a node, a function), use it - no pattern.
3. Only name a pattern when the problem matches its intent AND multiple future variants are plausible.
4. Prefer the simplest pattern in the family. Strategy over Visitor. Adapter over Bridge.
5. Document WHY the pattern was chosen in the workflow notes (a pattern without its rationale is decoration).

## Pattern Selection Checklist (7 questions)

- [ ] Does the pattern reduce change cost, or does it add indirection for its own sake?
- [ ] Would the codebase survive without it? (GoF: design for change, not for tomorrow's imagined requirements)
- [ ] Is the pattern the smallest one that satisfies the intent?
- [ ] Are the collaborators bound to interfaces (not concrete classes)?
- [ ] Is the coupling direction inward (Clean Architecture Dependency Rule)?
- [ ] Does each pattern participant have a single responsibility?
- [ ] Can a newcomer read the workflow and identify the pattern from names alone?

## Common Pattern Application Errors (severity)

- **P1 - Pattern for its own sake** (HIGH): A Factory wrapping a single, never-varying node. Fix: delete it, call the node directly.
- **P2 - God Object Mediator** (HIGH): A Mediator that knows every node and duplicates their logic. Fix: split mediators, keep them thin.
- **P3 - Leaky Abstraction** (MEDIUM): An Adapter that exposes the wrapped API's raw errors to callers. Fix: normalize errors at the boundary.
- **P4 - Singleton for state** (MEDIUM): A 'Singleton' that is really global mutable state. Fix: explicit dependency injection.
- **P5 - Strategy explosion** (LOW): Ten strategy variants where a single parameter would do. Fix: parameterize.

## When NOT to use (honest limits)

- A one-off workflow with no future variants: plain nodes win. GoF patterns shine under CHANGE, not under simplicity.
- If you cannot name the recurring problem, you have not found a pattern - you found a wish.

## Verification

Run `venv/bin/python scripts/build_gates_pipeline.py .opencode/skills/gof-design-patterns/SKILL.md --no-hitl` and require READY_FOR_DEPLOYMENT (exit 0). The doc must not trip the reasoning gate; keep interval/quantity vocabulary out of prose.
