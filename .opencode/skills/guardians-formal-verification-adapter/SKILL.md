---
name: guardians-formal-verification-adapter
description: "Pre-execution formal verification adapter for agent plans (taint analysis, security automata, Z3 proofs, verify-before-run). Use when an LLM produces a tool-call plan that must be proven safe before anything executes, when untrusted data meets sensitive sinks, or when a plan-execute split with static gates is required. Trigger phrases: 'verify this plan', 'taint analysis', 'Z3 proof', 'plan before execute', 'تحقق شكلي قبل التنفيذ'."
---

# Guardians Adapter (Verify the Plan, Then Run It)

Adapter over upstream **metareflection/guardians** (Python 3.11+, MIT,
only `pydantic` + `z3-solver`; `[llm]` extra adds `litellm`). It
implements the published thesis (CACM, January 2026): prompt injection is
a code/data-separation failure, so the fix is structural — the model
generates a **plan with symbolic references** (placeholders, never live
data), a **static verifier** proves it against policy, and only verified
plans execute. No model call is needed for verification itself.

## When to use

- Any agent loop where untrusted content (emails, pages, user pastes)
  flows near sensitive tools (send, publish, write, pay, delete).
- As the pre-execution stage inside this repo's own orchestrator: plan →
  guardians-verify → execute-or-HITL.
- When a security claim must be a proof ("taint cannot reach the sink",
  "the automaton never hits the error state") rather than a hope.

## Steps

1. Install upstream as a library (`pip install -e .` from a checkout, or
   the published package when available). Core stays dependency-free;
   keep the `[llm]` planner optional.
2. Register every tool the agent may call as a `ToolSpec`: parameter
   types, which params are taint sinks, source/sink labels, and
   pre/post/frame conditions. Unregistered tools fail closed
   (`missing_spec`).
3. Write the `Policy`: tool allow-list, `TaintRule`s (source tool/output
   → sink tool/param, with sanitizer escape hatches), `SecurityAutomaton`s
   (states + transitions; error states must be unreachable), invariants.
4. Force the planner to emit `Workflow` objects: ordered steps of
   `ToolCallNode`s wired ONLY by `SymRef` placeholders, `ConditionalNode`
   for branches, `LoopNode` for iteration. Raw data never appears in the
   plan — this is the entire security property.
5. Call `verify(workflow, policy, registry, strict=...)` and read the
   eight static checks: allowlist, missing-spec, well-formedness
   (every reference in scope), taint, Z3 preconditions, Z3
   postconditions, Z3 frame conditions, automaton safety — plus the
   fail-closed `analysis_incomplete` verdict. Fix the plan, not the
   verdict.
6. Execute only on `result.ok` via `WorkflowExecutor` (verify-first stays
   on; budgets enforced at runtime). Archive violations + trace with the
   delivery; route `analysis_incomplete` and high-severity violations to
   HITL with the check name attached.

## Mapping n8n workflows to the AST

Treat each n8n node type+operation as a tool name (fetch/read nodes are
taint sources; send/publish/write nodes are sinks); linearize `connections`
into ordered steps bound by node id; rewrite `{{ $json... }}` expressions
into `SymRef`s or literals; map IF/Switch → conditionals, batch/loop
nodes → loops; put credentials and URLs into automaton constants and the
allow-list. Then verify before any run.

## Verification

- `verify()` returns `ok` with zero violations (warnings reviewed or
  promoted via `strict=True`).
- The injection demo shape holds: a malicious instruction inside
  untrusted content produces a plan the verifier REJECTS (taint +
  automaton), with nothing executed.
- Every executed plan has its verification result archived beside it.

## Pairs with

`formal-math-logic-verification-engine` (local Z3/verify habits),
`build-gates-pipeline` (MATH/REASONING stages), `human-approval-gates`
(unverifiable-but-suspicious plans), `agentic-workflows`.
