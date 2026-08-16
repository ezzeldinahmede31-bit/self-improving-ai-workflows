---
name: execution-guided-tot-validator
description: "Validates Tree-of-Thought (ToT) reasoning branches using real execution feedback in a local Docker sandbox rather than relying on LLM self-judgment. Corrects ToT drift in weak models (the 75% to 96% complex-reasoning gap) by eliminating non-running branches deterministically. Use when the planner enumerates multiple candidate solutions/architectures, when branch scoring is speculative, or when LLM self-evaluation might pick a plausible-but-broken path. Trigger phrases: 'which approach works', 'compare solutions', 'validate the plan', 'ToT', 'tree of thought', 'branch comparison', 'execute and pick the winner'."
---

# EXECUTION-GUIDED TREE-OF-THOUGHT (ToT) VALIDATOR

## DIRECTIVE

Do NOT trust LLM self-evaluations for complex decision trees. Every branch
proposed in a Tree-of-Thought search must be empirically validated against
actual execution or deterministic rules. Self-scoring hello-works; execution
tells the truth.

## TOT BRANCH VALIDATION PROTOCOL

```
              [Problem Statement]
                       │
       ┌───────────────┼───────────────┐
       ▼               ▼               ▼
   [Branch A]      [Branch B]      [Branch C]
       │               │               │
       ▼               ▼               ▼
[Sandbox A]       [Sandbox B]     [Sandbox C]
 (exit 1)          (exit 0)        (exit 0)
    ❌                │                │
                     ▼                ▼
            [Benchmark]         [Benchmark]
            latency 50ms        latency 400ms
                🏆                 ⚠️
```

## EXECUTION STEPS

1. **Branch Generation:** Generate up to 3 candidate solution
   workflows/scripts from the same problem statement.
2. **Sandbox Trial Run:** Execute each candidate inside a temporary Docker
   container (`python:3.11-slim`), network-disabled, bounded CPU/mem/timeout.
3. **Deterministic Selection:**
   - Eliminate branches returning non-zero exit codes or syntax errors
     IMMEDIATELY (no second chance, no prose appeal).
   - Benchmark surviving branches for execution latency and memory.
   - Select the branch with the lowest complexity and zero runtime errors.
     Ties broken by deterministic rules (fewer moving parts), never by how
     "smart" the branch *sounds*.

## VALIDATION SUB-RULES

- A branch with exit code 0 but a corrupted output shape is still FAILED —
  verify output against the artifact schema deterministically.
- Latency alone must not win: a fast-but-fragile branch loses to a robust one.
  Use a weighted score: `non_blocking(exit_code) + quality(structural) +
  penalty(latency > threshold)`.
- Cache last executions per (branch-signature, sandbox-image) so identical
  candidates are not re-run.

## INTEGRATION

In `master_system_orchestrator` the planner currently scores paths
(`dual_process_planner.score_and_select`); this skill replaces speculative
cost/risk scoring with the sandbox trial-run veredict for any candidate that
produces runnable code. Runtime failures surface through the existing
`cybersec_sandbox_engine.ExecutionSandbox`.