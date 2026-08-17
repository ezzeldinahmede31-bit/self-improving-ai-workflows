---
name: fitness-function-engineering
description: Applies the fitness function practice from Building Evolutionary Architectures (Ford, Parsons, Kua): encode architectural characteristics as automated tests that run in CI, so every change is continuously checked against the architecture's non-negotiable properties — coupling, dependency rules, performance budgets, security, and design metrics. Use when the user says 'fitness function', 'architectural test', 'guard the architecture', 'automated architecture checks', 'coupling analysis', 'dependency rule test', 'performance budget', 'architecture regression', 'ArchUnit', 'evolutionary architecture', or when a system must evolve without silently losing its architectural properties. Pairs with: evolutionary-architecture, code-execution-guided-swemaster, tradeoff-and-postmortem-documenter, devops-handbook-flow.
---

# Fitness Function Engineering

Transfers the fitness function method from Building Evolutionary Architectures (Ford, Parsons, Kua) to delivery pipelines: turn architectural characteristics into automated checks that run on every change.

## When to use
- Guarding coupling and dependency rules that must never regress.
- Enforcing performance, security, or design budgets in CI.
- Building the automated verification the architecture relies on as it evolves.

## The method
1. Name the architectural characteristics that are non-negotiable (deployability, modifiability, coupling limits, latency budgets).
2. For each, write a fitness function: an automated test that returns pass/fail with a concrete measurement.
3. Run every function in CI so a violation fails the pipeline immediately.
4. Review the functions themselves when the architecture's intent changes — stale functions become noise.

## Function families
- Structural: dependency-direction checks (no cycle across modules), forbidden-import scans.
- Coupling: fan-in/fan-out thresholds and module-boundary leak detectors.
- Performance: latency and throughput budgets asserted under a standard load.
- Security: dependency and secret scanners wired as gatekeeping tests.
- Design: cyclomatic and duplication metrics held under agreed ceilings.

## Verification discipline
- Prove each function fails on a deliberately violated sample before trusting it in CI.
- Keep a dashboard of function results so drift is visible, not hidden.

## Pairs with
evolutionary-architecture, code-execution-guided-swemaster, tradeoff-and-postmortem-documenter, devops-handbook-flow.