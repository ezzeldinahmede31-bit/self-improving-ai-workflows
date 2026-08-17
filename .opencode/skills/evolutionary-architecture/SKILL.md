---
name: evolutionary-architecture
description: "Applies Building Evolutionary Architectures by Ford, Parsons & Kua: design systems that adapt to continuous change instead of freezing — architecture fitness functions (automated tests that guard architectural characteristics), guided incremental change, the architecture quantum (deployability, modifiability, testability), and coupling analysis. Use when the user says 'evolutionary architecture', 'fitness function', 'architecture quantum', 'make the architecture testable', 'incremental change', 'strangler fig pattern', 'coupling analysis', 'guard against regression in the architecture', 'build for change', or when a system must keep evolving without a rewrite. Pairs with: agent-arch-system-design, tradeoff-and-postmortem-documenter, code-execution-guided-swemaster, test-driven-development."
---

# Evolutionary Architecture

Ford, Parsons & Kua: architecture is not a frozen blueprint — it is a set of
characteristics you keep *fitting* to the system as it changes. The mechanism is the
fitness function: an automated check that the current build still exhibits a desired
architectural characteristic.

## When to use

- Designing a new system that must absorb years of feature change.
- Adding guardrails to an existing architecture so changes do not silently erode it.
- Deciding how far to decompose a monolith, or how to migrate one safely.

## The method

### 1. Choose the architecture characteristics (quality attributes)
- Decide the few characteristics that matter (deployability, modifiability,
  scalability, security, performance) and make them explicit and measurable.
- Everything else is noise — an over-scored system optimizes the wrong things.

### 2. Write fitness functions (architectural tests)
- For each characteristic, add an automated check that runs in CI and fails the
  build when the characteristic regresses.
- Examples: dependency rule check (layers only point inward), deploy time ceiling,
  security gate score, coupling metric ceiling, cyclomatic complexity threshold.
- Fitness functions are code — keep them in version control with the system.

### 3. The architecture quantum
- Think of deployability per component: what is the smallest unit that can be
  deployed, modified, and tested independently?
- Smaller quanta = faster change but more operational surface. Choose the granularity
  deliberately; not every service deserves its own quantum.

### 4. Coupling analysis and the strangler pattern
- Measure coupling (afferent/efferent, fan-in/fan-out) before refactoring — the
  coupling map tells you where to cut.
- Migrate incrementally with the strangler fig: route traffic to the new component
  gradually while the old one is retired — never a big-bang rewrite.

## Verification
- The fitness functions are green in CI (each maps to a stated characteristic).
- A real change (add a field, add a service) ships without touching unrelated
  components — that is the evolution test.
- Re-run the coupling analysis and confirm the target component boundaries held.

## Pairs with
- `agent-arch-system-design` — architecture characteristics and ADRs.
- `tradeoff-and-postmortem-documenter` — documenting the trade-offs of each choice.
- `code-execution-guided-swemaster` — execution-evidence verification of changes.
- `test-driven-development` — the discipline that makes fitness functions reliable.