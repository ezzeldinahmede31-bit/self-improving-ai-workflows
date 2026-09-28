---
name: hitl-patterns-durable-adapter
description: "Durable HITL design patterns adapter (tool-level decorators, signal-based waits, approve/edit/reject/respond, sticky decisions, timeout+escalation). Use when designing any approval flow that must survive crashes, when choosing between n8n-native vs decorator vs durable-execution HITL, or when partial approvals and durable resume are required. Trigger phrases: 'durable approval', 'ask_human pattern', 'edit before approve', 'موافقة بشرية متينة'."
---

# Durable HITL Patterns Adapter (Four Designs, One Doctrine)

Design donor distilled from four production systems: **HumanLayer**
(tool-level `@require_approval` + `human_as_tool`, omnichannel Slack/
Email/Discord), **Temporal durable HITL** (signal + `wait_condition`,
zero compute while waiting, crash-proof resume), **OpenAI Agents SDK**
(interruptions + serializable `RunState`, sticky per-call decisions),
**LangChain HITL middleware** (policy map + checkpointed interrupts).
Local `hitl_gate.py` stays the binding implementation; these are the
patterns it should mirror.

## When to use

- Designing any approval flow: pick the lightest pattern that satisfies
  durability (minutes → in-workflow wait; hours/days → durable persisted
  state; cross-framework → signal-based).
- Tool-level gating (garbage in never executes) vs output review (react
  after the fact): prefer tool-level for irreversible actions.
- Multi-approver, escalation, or partial-approval needs.

## The four decisions (support all four verbs)

`approve` (run as-is) / `edit` (human modifies parameters, then run) /
`reject` (skip + feedback to the agent: abandon, safer alternative, or
follow-up?) / `respond` (human IS the tool — answer becomes the tool
result; never use to deny side effects). Gate interrupts on arguments
via predicates so reviewers see only what needs them.

## Durability rules

- Persist the wait: serializable run state (decisions, approvals, usage)
  in a store/queue; version-marker agent definitions beside it.
- Timeouts always: wait with deadline → escalate (backup approver) →
  safest default. Authorize deciders (non-approver input recorded but
  ignored); idempotency keys make duplicate signals no-ops.
- Sticky decisions per call identity survive resume; unresolved items
  re-pause on rerun (never silently continue).
- Agent-as-human-tool: mid-reasoning `ask_human` suspends the loop and
  resumes with the answer as the next observation (both HITL directions:
  agent→human question AND human→agent steering).

## Steps

1. Classify each action (read / moderate / critical) → gate level +
   channel + timeout + escalation target.
2. Implement at the tool layer (decorator/middleware), so even a
   hallucinating model cannot bypass review.
3. Add edit-capable forms where "approve with changes" is realistic.
4. Persist state + log every decision (who, what params, verdict, time,
   execution ID) into the audit trail.
5. Drill timeout, crash-during-wait, and unauthorized-decider cases.

## Verification

- Kill-during-wait drill: resume works, no re-approval needed.
- Unauthorized decision ignored + recorded; duplicate signal is a no-op.
- Denied/edited calls carry feedback the agent can act on.

## Pairs with

`human-approval-gates`, `n8n-production-governance-adapter`,
`agent-control-plane-adapter`, `build-gates-pipeline`.
