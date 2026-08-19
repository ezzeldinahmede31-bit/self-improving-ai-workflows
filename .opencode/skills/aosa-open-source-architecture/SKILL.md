---
name: aosa-open-source-architecture
description: Applies the case studies of The Architecture of Open Source Applications (Brown & Wilson) to learn architecture from real, working systems: how large projects (from web servers and databases to compilers and desktop apps) structure their code, make trade-offs, and evolve, and the transferable lessons about modularity, concurrency, and maintainability. Use when the user says 'AOSA', 'architecture of open source', 'learn architecture from real projects', 'case study architecture', 'how is project X structured', 'Brown Wilson', or when real architecture examples are the best teacher.
---

# The Architecture of Open Source Applications (Amy Brown & Greg Wilson, ed.)

AOSA shows the architecture of real open source systems through the eyes of their maintainers. This skill applies those lessons to design and code review.

## Learning from real systems

- Real systems earn their structure under real constraints; the case studies show why each choice was made.
- Name the problem each project solved before judging its architecture.
- The lessons transfer: modularity, clear interfaces, and explicit failure handling appear in every success.

## Common architectural themes

- Small, focused modules with clean interfaces recur across successful projects.
- Concurrency is handled by isolating state and using the right coordination primitive.
- Extensibility comes from design (plugins, callbacks, abstractions), not from features.

## Trade-offs and evolution

- Every architecture is a set of trade-offs; the case studies make the trade visible.
- Systems evolve; the architecture must accommodate change without a rewrite.
- Simplicity is a property to protect; complexity creeps in one convenience at a time.

## Applying the lessons

- Read a real project's source when designing something similar; the example is the spec.
- In code review, ask what the maintainer of a well-architected project would say.
- Document the architecture decisions; the next engineer learns the why, not just the what.

## Pairs with
agent-arch-system-design, fundamentals-of-software-architecture, software-architecture-hard-parts, zero-trust-modular-decomposer, codebase-mind-persistence
