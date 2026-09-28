---
name: agent-control-plane-adapter
description: "Deterministic agent governance adapter (policy engine, approval gates, token budgets, kill switch, event-sourced audit). Use when an agent needs pre-execution policy decisions, tiered adoption from cost-tracking to full governance, session audit trails, or a reference design for budget/kill-switch semantics. Trigger phrases: 'policy before execution', 'control plane', 'kill switch', 'token budget', 'حوكمة الوكيل'."
---

# Control Plane Adapter (Policy + Budget + Kill Switch)

Adapter over upstream **ryanwi/agent-control-plane** (Python 3.11+, MIT,
only two runtime deps: sqlalchemy + pydantic). Its founding split is the
doctrine to copy: the **control plane decides** when/how an agent may act;
the **data plane executes**. Policy is deterministic code, not prompt text.

## When to use

- Any autonomous or long-running agent: wrap runs in policy + budget before
  the first side effect.
- Adopt in tiers (upstream's own ladder): cost-tracking only → + session
  audit trail → + full governance (policy, approvals, revocation). Start
  at tier 1; escalate only when the agent gains side effects.
- As the reference design when extending this repo's own
  `master_system_orchestrator.py` budget/HITL/audit pieces.

## Single-trail rule (avoid double bookkeeping)

Upstream keeps a durable event store for audit/replay/recovery. This repo
already keeps `audit.db` + `cost_ledger`. NEVER run two trails: map
upstream events onto the existing stores (policy verdicts → audit rows,
token spend → cost ledger). If both exist, the local stores win.

## Steps

1. Classify the run: single action, single-agent loop, or multi-agent loop;
   pick the matching upstream example shape (quickstart / continuous-loop /
   tenant-budget / audit-trail) as the skeleton.
2. Declare policy first: condition trees (and/or/not composition), pluggable
   evaluators, parallel evaluation with cancel-on-deny, egress rules in a
   capability-grant form (destination AND capability both explicitly
   allowed).
3. Attach enforcement: pre-execution budget check with a local soft ceiling
   (token counts are known post-call, so record-then-raise keeps the ledger
   honest); concurrency guard; kill switch with multi-agent revocation.
4. Add preconditions for resource drift (file hashes, environment) before
   side effects; session lifecycle with crash recovery and timeout
   escalation.
5. Record every decision + spend into the local audit/cost stores with the
   upstream event vocabulary (propose → policy verdict → approve/deny →
   execute → usage recorded).
6. High-impact allows still route to the local HITL human checkpoint; the
   control plane narrows WHAT reaches the human, never replaces them.

## Verification

- A denied action has an audit row and zero side effects.
- An over-budget call is recorded in the ledger even though it raised.
- Kill-switch drill: in-flight loop halts and session recovers to a known
  state.

## Pairs with

`human-approval-gates` (human checkpoint), `build-gates-pipeline`
(binding verdict), `agent-runtime-guard-adapter` (microsecond inline
checks), `rate-limit-and-cost-guard`.
