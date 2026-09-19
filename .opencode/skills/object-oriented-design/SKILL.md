---
name: object-oriented-design
description: "Designs with objects: responsibilities, contracts, and composition over inheritance. Use when the user says 'class design', 'CRC cards', 'responsibility-driven', 'coupling cohesion', 'inheritance or composition', 'design by contract', 'Liskov', 'OOD', 'domain model', or when behavior must live in the right object."
---

# Object-Oriented Design

Distilled from the OOD tradition (Wirfs-Brock responsibility-driven design,
Meyer contracts, Martin principles): objects own behavior, contracts guard
boundaries, and inheritance is the tightest coupling — spend it sparingly.

## Purpose

Place every behavior in the object that owns its data, with interactions
governed by explicit contracts.

## The method

1. **Responsibilities first (CRC).** For each candidate class list what it
   KNOWS and DOES plus collaborators. If a card is all data or all
   collaborators, the design is wrong — behavior follows data.
2. **Contracts at boundaries.** Preconditions (caller owes), postconditions
   (routine guarantees), invariants (always true). Design by Contract turns
   integration arguments into checkable facts.
3. **Composition over inheritance.** Inherit only for true substitutability
   (Liskov: a subclass must honor every contract of its parent — no
   strengthened preconditions, no weakened postconditions). Share code via
   composition/delegation; share interface via abstract types.
4. **Coupling/cohesion budget.** High cohesion (one reason to change),
   low coupling (few, narrow, stable dependencies). Dependency direction:
   toward abstractions, away from details. A change rippling across packages
   is the metric that convicts the design.
5. **Patterns as vocabulary, not goals.** Strategy/Observer/Factory/Adapter
   name recurring solutions — apply when the forces match, never to look
   sophisticated. One pattern per decision, stated explicitly.

## Tells of a sick design

- Feature envy (a method using another object's data more than its own).
- Refused bequest (subclass ignoring inherited behavior).
- Message chains and middlemen (Law of Demeter violations).
- God class / data class pairs (responsibilities never assigned).

## Verification

Review ends with: CRC for new classes, contracts on public routines, an
inheritance justification per subclass, and the dependency direction
diagram. Unplaced behavior is a defect, not a TODO.

## Pairs with

- `law-of-demeter-guard` (chain detection), `clean-code-classes-error-handling`
  (class craft), `gof-design-patterns` (pattern catalog),
  `ddd-tactical-aggregates` (consistency boundaries).
