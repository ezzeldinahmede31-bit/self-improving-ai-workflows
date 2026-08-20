---
name: refactoring-catalog-recipes
description: Applies the refactoring catalog of Martin Fowler's Refactoring as a recipe book: match the current code smell to a named refactoring, follow its mechanical steps, and run the tests after each behavior-preserving step. Covers the recipe families for names, functions, classes, data, and conditionals with the safe-step discipline that keeps every transformation reversible. Use when the user says 'refactor this', 'extract method', 'extract variable', 'inline method', 'move method', 'replace conditional with polymorphism', 'introduce parameter object', 'Fowler refactoring catalog', or when improving existing code without changing behavior.
---

# Refactoring: Catalog Recipes

Fowler's Refactoring is a recipe book: each refactoring has a name, a motivation, and a sequence of mechanical steps that preserve behavior. The skill of refactoring is matching the smell in front of you to the right recipe and executing it in safe, testable steps. This skill encodes the catalog as a decision table.

## The Safe-Step Discipline
- A refactoring is only safe if every step is behavior-preserving; change structure, never semantics.
- Run the tests after each small step so the first broken transformation is identified immediately.
- Keep steps small and reversible; if a step fails, back out to the last green state rather than pushing on.
- Refactor the code, not the tests' expectations — the tests are the safety net, not the target.

## Function-Level Recipes
- Extract Method: pull a named block out of a long function when the block has a clear purpose.
- Extract Variable: name an expression that appears more than once or is hard to read.
- Inline Method: fold a tiny function back into its callers when the indirection costs more than it saves.
- Introduce Parameter Object: cluster a repeating group of arguments into one value object.
- Replace Method with Method Object: turn a long function with many locals into a class so the locals become fields and the steps become methods.

## Class-Level Recipes
- Move Method: relocate a method to the class that owns the data it uses most.
- Move Field: follow the data to its owner class when a field is used mainly elsewhere.
- Extract Class: split a class with two responsibilities into two classes joined by delegation.
- Inline Class: merge a class that no longer earns its keep back into its only client.
- Hide Delegate: make the caller talk to one object instead of walking a chain of getters.

## Data and Conditional Recipes
- Replace Conditional with Polymorphism: when a conditional dispatches on a type field, give each type a subclass with its own method.
- Replace Nested Conditional with Guard Clauses: turn an else-heavy chain into early returns for the exceptional paths.
- Consolidate Duplicate Conditional Fragments: pull repeated code out of the branches into the common path.
- Replace Magic Literal with Named Constant: give a bare value a name that states its meaning.
- Decompose Conditional: extract each branch of a complex condition into its own named method.

## Pairs with
refactoring-improving-design, legacy-code-characterization, xunit-test-patterns, tdd-sandbox-proof-engine, code-smell-detector
