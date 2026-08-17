---
name: domain-modeling-functional
description: "Applies Scott Wlaschin's Domain Modeling Made Functional method: translate business requirements into precise code by modeling the domain as types and workflows, making illegal states unrepresentable, using a functional core with an imperative shell, and handling errors as data (Option/Result). Use when the user says 'model this business domain', 'make illegal states impossible', 'domain modeling', 'functional core imperative shell', 'type-driven design', 'translate requirements into code', 'workflow as a function', 'error handling as data', 'Option and Result types', 'business rules as types', or when requirements must be captured exactly and bugs prevented by the type system. Pairs with: proactive-spec-expander, clarify-before-execute, sicp-abstraction-and-interpretation, zero-trust-modular-decomposer."
---

# Domain Modeling Made Functional

Wlaschin's core idea: the type system is the strongest contract with the business.
Model the domain (nouns as types, verbs as workflows) so that states that cannot
happen in the business cannot be expressed in code — and keep side effects at the
edge.

## When to use

- Turning business requirements into a code structure where the types must mirror
  the business rules exactly.
- Reducing bugs caused by invalid states, nulls, or partial data.
- Designing workflows (order processing, approval chains, onboarding) where each
  step's input/output should be explicit.

## The method

### 1. Understand the domain from the business (not the DB)
- Ask the domain expert for the processes (workflows), not the data model first.
- Capture each workflow as a function: `Input -> Output`, where the types carry the
  business meaning. Every workflow gets a name and a one-line purpose.

### 2. Make illegal states unrepresentable
- Encode constraints in the types: use unions for allowed alternatives, require the
  invariants as fields (e.g. an order can exist only when its items and totals are
  present), and prefer making invalid combinations unbuildable over validating at
  runtime.
- Replace raw strings/numbers with single-purpose types where a typo or mixed unit
  would be a bug (e.g. `EmailAddress`, `CustomerId` — not bare `string`).
- Where a rule is too dynamic for types, validate at the boundary and convert to a
  typed value once.

### 3. Functional core, imperative shell
- Keep the pure core (all business logic, no I/O) testable in isolation — pure
  functions make the business rules unit-testable without mocks.
- Put side effects (DB, network, files) in a thin shell around the core. The shell
  reads input, calls the pure core, writes output.

### 4. Errors as data
- Return `Option`/`Result`-style values for operations that can fail or be absent;
  do not rely on exceptions or nulls for expected business outcomes.
- Model the error cases in the type of the workflow output so callers must handle
  them (the compiler/runtime keeps them honest).

## Verification
- Every business rule appears as a type or a pure function in the core — walk each
  requirement and point at where it is enforced.
- Unit-test the pure core with the exact business scenarios; the shell is thin and
  needs only integration-level tests.
- Check the "illegal state" claim: try to construct the invalid state in code; it
  must be impossible or visibly rejected at the boundary.

## Pairs with
- `proactive-spec-expander` — expand requirements into the domain model before code.
- `clarify-before-execute` — extract the load-bearing business rules from the user.
- `sicp-abstraction-and-interpretation` — layered abstraction for the model.
- `zero-trust-modular-decomposer` — modular file layout around core and shell.