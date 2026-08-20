---
name: clean-code-classes-error-handling
description: Applies the classes and error-handling chapters of Robert C. Martin's Clean Code to structure maintainable systems: classes built around cohesion and encapsulation, the Single Responsibility Principle applied to classes, and error handling as a distinct concern with exceptions, the Special Case object, and fail-fast boundaries. Use when the user says 'design my classes', 'single responsibility class', 'class too big', 'error handling', 'exceptions', 'special case object', 'fail fast', 'Clean Code classes', 'rethrow and wrap exceptions', or when reviewing class structure and error paths.
---

# Clean Code: Classes and Error Handling

Clean Code treats classes as the unit of organization and error handling as a concern you design for, not a detail you bolt on. A class with one reason to change and an error path that reads like the happy path is what keeps a system maintainable as it grows. This skill encodes both disciplines.

## Classes Built Around Cohesion
- A class should encapsulate its data and expose behavior; the fewer the operations a client can perform on the internals, the safer the design.
- Cohesion is the measure: a class whose methods all use the same data is cohesive, and cohesion is the sign of a class doing one job.
- Prefer many small, highly cohesive classes over one large class holding several responsibilities.
- Expose behavior, not data — getters that return raw collections leak the representation and invite callers to mutate internals.

## Single Responsibility for Classes
- A class has one reason to change: name the single actor or policy it serves, and keep every method aligned with it.
- When a change request touches a class for an unrelated reason, that is the smell that the responsibility has split.
- Split god classes by the responsibility each group of methods serves, then let the pieces compose.
- Keep dependencies few and explicit so each class can be tested in isolation.

## Error Handling as a Concern
- Treat error handling as an input-output flow: the error path should be readable and complete, not scattered if-statements.
- Prefer exceptions over error codes so callers cannot silently ignore failures.
- Use the Special Case pattern — return a harmless do-nothing object instead of a null that every caller must check.
- Wrap third-party exceptions at the boundary so your callers depend on your vocabulary, not on a vendor's.

## Boundaries and Fail-Fast
- Fail fast at the edge: validate input where it enters and raise early rather than propagating a corrupted state.
- Do not swallow exceptions to keep a test green; let failures surface at the boundary where recovery is possible.
- Push the error handling to the boundaries of the system, keeping the core logic free of exception noise.
- Design the boundary so a change of vendor or library touches one place, not every call site.

## Pairs with
clean-code, abstraction-quality-gate, dependency-inversion-enforcer, ddd-tactical-aggregates, refactoring-improving-design
