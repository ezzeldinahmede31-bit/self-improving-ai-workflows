---
name: fundamentals-of-software-architecture
description: "Applies Mark Richards & Neal Ford's Fundamentals of Software Architecture to think like an architect: architecture characteristics (and the tension that no architecture satisfies them all), architectural styles and their trade-offs, component thinking, the architecture quantum, ADRs for recording decisions, and team/architecture alignment. Use when the user says 'architecture characteristics', 'architectural styles', 'layered vs modular', 'event-driven architecture', 'microkernel', 'architecture quantum', 'component design', 'ADR', 'architecture decision record', 'how to think like an architect', 'architecture review', or when choosing or justifying an architecture style. Pairs with: software-architecture-hard-parts, agent-arch-system-design, evolutionary-architecture, tradeoff-and-postmortem-documenter, domain-driven-design-strategic."
---

# Fundamentals of Software Architecture

The premise: architecture is the stuff that is hard to change later — and the
architect's job is to make the few decisions that constrain the rest, and to keep
every decision honest by naming its trade-offs.

## When to use

- Choosing an architecture style for a new system or a growing one.
- Reviewing a system against its architecture characteristics.
- Recording architecture decisions for a team.

## The mental model

1. **Architecture characteristics** — the qualities you cannot get from
   requirements documents alone (scalability, performance, availability, security,
   testability, deployability, cost).
2. **The tension** — no architecture satisfies all characteristics at once; a
   chosen set is a deliberate trade (see `software-architecture-hard-parts`).
3. **Architectural styles** — the shapes systems take (see below), each with a
   built-in set of strengths and weaknesses.
4. **Components and their dependencies** — how the system is divided and how the
   pieces connect.
5. **The quantum** — the smallest deployable unit with its data and dependencies;
   coupling across quanta is what makes "microservices" hard.

## Architectural styles (the menu)

- **Layered**: familiar, simple, but a single change can ripple through every
  layer.
- **Event-driven**: decoupled and elastic, but asynchronous and harder to trace
  (see `designing-event-driven-systems`).
- **Microkernel**: a small core with pluggable extensions — strong for extensible
  products.
- **Microservices / service-based**: independent deployability with a
  distributed-systems tax (see `microservices-boundary-design`).
- Choose the style for the characteristics you need, not for fashion.

## Component thinking

- Partition by domain/business capability, then refine the internals; keep
  coupling low and cohesion high.
- Name components for what they do; a component that cannot be described in one
  phrase is too broad.

## Decisions and review

- Record every decision as an **ADR** (Architecture Decision Record): context,
  decision, consequences, and the triggers that would reverse it (see
  `tradeoff-and-postmortem-documenter`).
- Measure fitness: automated checks that the architecture still matches the
  chosen characteristics (see `fitness-function-engineering`).
- Keep a personal radar of trade-offs per style so you can defend a choice under
  review.

Pairs with: software-architecture-hard-parts (no-perfect-answer decisions),
agent-arch-system-design (design method), evolutionary-architecture (fitness
functions), tradeoff-and-postmortem-documenter (ADRs),
domain-driven-design-strategic (domains).