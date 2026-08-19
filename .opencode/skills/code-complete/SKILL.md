---
name: code-complete
description: Applies Steve McConnell's Code Complete to the craft of constructing software well: the construction process, design in construction, class and routine design, data and control structures, code layout, and the science of debugging, testing, and building quality in. Use when the user says 'code complete', 'McConnell', 'software construction', 'routine design', 'good practice', 'code quality', 'debugging', 'construction practices', or when the craft decisions of writing software need authoritative grounding.
---

# Code Complete (Steve McConnell)

Code Complete is the encyclopedic treatment of the craft of construction. This skill applies its guidance on design, routines, data, control, and quality to everyday coding.

## Construction discipline

- Construction is where the design becomes code; the craft is the quality multiplier.
- Programming is an act of writing for humans first; the compiler is the secondary reader.
- Plan the construction: the checklist is a tool for consistency, not bureaucracy.

## Routine and class design

- Keep routines small and focused; the name should say what the routine guarantees.
- Design classes around a coherent responsibility and hide their internals.
- Coupling and cohesion are the two forces: low coupling, high cohesion.

## Data and control

- Choose data structures and types that make illegal states hard to express.
- Simplify control flow: avoid deep nesting, prefer early returns, and keep the main path visible.
- Complexity is the enemy; the simpler expression is the more correct one.

## Debugging and quality

- Debug by hypothesis: find the cause, then fix it; a fix that hides the cause is a new bug.
- Test during construction, not after; defects found early are cheap.
- Quality is built in by the practices, not inspected in at the end.

## Pairs with
clean-code, refactoring-improving-design, xunit-test-patterns, code-debugging, professional-conduct-gate
