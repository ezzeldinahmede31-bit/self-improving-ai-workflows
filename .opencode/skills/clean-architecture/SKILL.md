---
name: clean-architecture
description: "Applies Robert C. Martin's Clean Architecture to structure software so business rules stay independent of frameworks, databases, and UI: the concentric layers (entities, use cases, adapters, frameworks), the Dependency Rule (dependencies point inward, never outward), boundary crossing, and the Screaming Architecture principle. Use when the user says 'clean architecture', 'dependency rule', 'use cases', 'entities', 'separate business rules from frameworks', 'onion architecture', 'hexagonal', 'ports and adapters', 'Screaming Architecture', or when a codebase needs its business logic protected from framework and tooling churn. Pairs with: dependency-inversion-enforcer, domain-modeling-functional, ddd-tactical-aggregates, abstraction-quality-gate, api-design-patterns."
---

# Clean Architecture

The premise: the framework, the database, and the UI are details. The business
rules are the point. Clean Architecture arranges the code so the important part
never depends on the details — and the details can be swapped freely.

## When to use

- Structuring a new codebase or reorganizing one that has tangled business logic
  with frameworks.
- Protecting business rules from tooling churn (upgrading a framework or swapping
  a database must not rewrite the rules).
- Explaining why a UI change or a DB migration should not touch core logic.

## The layers (inward to outward)

1. **Entities** — the enterprise business rules and data structures (the most
   stable layer).
2. **Use cases** — application-specific business rules that orchestrate entities
   for one scenario.
3. **Interface adapters** — controllers, presenters, gateways that translate data
   for the inner layers.
4. **Frameworks and drivers** — the web framework, DB, UI, messaging — the
   outermost, most volatile layer.

## The Dependency Rule (the whole discipline)

- Source code dependencies point inward only: an outer layer may depend on an
  inner layer, never the reverse.
- Inner layers never import framework classes or database libraries; they define
  the interfaces (ports) the outer layers implement (adapters).
- The same rule applies to n8n and service code: business nodes must not depend on
  specific API/database nodes (see `dependency-inversion-enforcer`).

## Boundary crossing

- Data crosses boundaries in the form most convenient for the inner layer — a
  plain structure, not a framework object.
- Dependencies cross the boundary against the flow: the inner layer declares an
  interface, the outer layer implements it, and the inner layer holds the
  reference.

## Practical rules

- **Screaming Architecture**: the top-level structure should announce the business
  domain (policies, orders, claims), not the tools (spring, django, express).
- Keep the use cases small and readable; a use case that needs many entity calls
  is usually the sign of a missing abstraction.
- Do not apply the full ceremony to a small app — the rule of thumb: the business
  rules stay clean, and the adapters stay thin.
- Test the use cases without the framework (pure unit tests); if a test must boot
  the framework, the rules are not clean.

Pairs with: dependency-inversion-enforcer (automated check),
domain-modeling-functional (types for rules), ddd-tactical-aggregates (aggregates
in the core), abstraction-quality-gate (deep modules), api-design-patterns
(interfaces).