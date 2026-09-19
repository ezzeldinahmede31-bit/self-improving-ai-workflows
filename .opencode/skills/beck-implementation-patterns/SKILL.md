---
name: beck-implementation-patterns
description: "Writes code at the method level the Beck way: intention-revealing classes, methods, and state. Use when the user says 'implementation patterns', 'method design', 'intention-revealing', 'Beck patterns', 'composed method', 'guard clause', or when code works but reads badly."
---

# Beck Implementation Patterns

Distilled from Kent Beck's *Implementation Patterns*: values (communication
first) drive principles (locality, symmetry, declarative style) that select
concrete coding patterns. Write code for the reader — the computer will
manage.

## Purpose

Make every class, method, and state decision communicate intent: code that
teaches its reader instead of testing them.

## The patterns (by scale)

1. **Class:** single coherent purpose; intention-revealing name; isolated
   creation (constructors/factories that leave no half-built objects);
   instance-specific behavior via pluggable objects, not conditionals on
   type codes.
2. **State:** fields with intention-revealing names; derived values computed
   (never stored-and-synced); collections chosen by access pattern; direct
   variable access inside, accessors at boundaries. Common state hoisted to
   constructors, not scattered across methods.
3. **Behavior — composed method.** Each method: one level of abstraction,
   intention-revealing selector, composed of messages to helpers at that
   same level. Long method? Extract till each piece says WHAT, with HOW one
   level down. Guard clauses up front (handle the exceptional, exit), happy
   path last and flat.
4. **Messages and control.** Tell, don't ask (behavior to the object holding
   the data); double dispatch where types collide; intention-revealing
   parameters (boolean flags are hidden conditionals — split the method);
   exceptions for exceptional flow only, with the cleanup discipline
   (resources released in finally/using/RAII equivalents).
5. **Collections and iteration.** Internal iteration (map/filter/fold) over
   manual loops where the language allows — the operation name documents
   intent; manual loops only when the pattern genuinely doesn't fit.

## Values check (the appeal court)

When patterns conflict, values decide: communication > simplicity >
flexibility. Optimize for the future reader's comprehension speed — measured
by how fast a newcomer explains the code back correctly.

## Verification

Code review per unit: name states intent, method fits one abstraction level,
guards precede happy path, state has one home, collections match access.
Three "what does this do?" questions in review = rewrite the unit.

## Pairs with

- `clean-code-naming-functions` (naming depth),
  `art-of-readable-code` (readability craft),
  `refactoring-catalog-recipes` (mechanical improvements),
  `test-driven-development-by-example-beck` (Beck's design loop).
