---
name: n8n-production-governance-adapter
description: "Official n8n production governance adapter (5 pillars: RBAC, tool-level HITL, runtime guardrails, output sanitization, observability + 15-point checklist). Use when shipping any n8n AI agent to production, hardening a template/prebuilt agent, setting timeout/escalation SLAs, or calibrating escalation rates. Trigger phrases: 'production readiness n8n', 'governance pillars', 'harden this agent', 'جاهزية الإنتاج'."
---

# n8n Production Governance Adapter (5 Pillars + Checklist)

Adapter over n8n's official **AI Agent Governance framework** (July 2026)
and production checklist. The core doctrine: governance decisions execute
INSIDE the workflow, not in a sidecar. Baseline: n8n docs (HITL for tools,
blog HITL automation), community production notes, `n8n-agents-official/
references/HUMAN_REVIEW.md` (freshly updated from upstream).

## When to use

- Before ANY n8n AI agent ships: apply all 5 pillars, then the checklist.
- When starting from a template or prebuilt agent: templates ship WITHOUT
  HITL, timeouts, logging, or monitoring — hardening is mandatory, never
  optional.
- When escalation rate drifts: >15% of executions seeking humans means a
  miscalibrated agent (prompt too cautious or tools too broad); denials
  >20% mean the tool scope is wrong.

## The 5 pillars (risk-tiered)

1. **RBAC** — least-privilege credentials per tool; custom roles for high
   risk; read tools stay ungated, writes get gated.
2. **Tool-level HITL** — pause BEFORE the tool runs (preventive, not
   reactive). Reviewer sees tool name + literal parameters (`$tool`
   variable). Channels: Chat, Slack, Discord, Telegram, Teams, Gmail,
   WhatsApp, Google Chat, Outlook. Response types: approval (single/
   double), freeText, customForm (human edits parameters — the answer to
   "approve at $40 instead of $50").
3. **Runtime guardrails** — jailbreak detection, blocked keywords,
   PII/secret filtering on inputs AND outputs, tool-call format checks.
4. **Output sanitization** — check mode (pass/fail) vs sanitize mode
   (active cleaning); never let the model paraphrase what the human
   approves (no `fromAi()` in approval text).
5. **Observability** — error rate, duration, escalation rate, denial rate;
   every decision (approve/deny/timeout/escalate) persisted with
   timestamp, reviewer, tool, parameters, duration, execution ID.

## Timeout / escalation SLA (never wait forever)

`limitWaitTime` on EVERY approval (default 45 min is a pile-up risk).
Proven schema: 2h primary channel → 22h backup channel → 24h total SLA,
then safest-outcome default. Confidence routing: high-confidence paths
run, only edge cases go human.

## Steps

1. Classify every tool: read (ungated) / moderate write (gated, short
   timeout) / critical (gated, double validation, full log).
2. Wire native review nodes (`*HitlTool` via `subnodes.tools` only —
   never `.to()` wiring), literal-parameter messages, explicit wait
   limits, system-prompt notes on denial handling.
3. Add guardrails + sanitization + per-decision logging.
4. Validate on 20–30 real cases; measure escalation/denial rates.
5. Run the delivery verification gate; archive the checklist as evidence.

## Verification

- Every write tool gated; every gate has a wait limit + escalation path.
- 20–30 case run: escalation <10–15%, denials <20%, full decision log.
- `build_gates_pipeline.py` READY + live execution proof archived.

## Pairs with

`n8n-agents-official` (HUMAN_REVIEW.md), `human-approval-gates`,
`build-gates-pipeline`, `n8n-delivery-verification-gate`,
`n8n-ai-security-lab-adapter` (staging evidence).
