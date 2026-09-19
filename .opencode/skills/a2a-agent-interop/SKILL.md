---
name: a2a-agent-interop
description: "Connect n8n agents to the open Agent-to-Agent (A2A) protocol: publish Agent Cards, drive the task lifecycle (message, polling, streaming, push), authenticate per card schemes, and wrap remote agents as n8n tools with MANUAL_REVIEW fail-safe. Use when agents built on different frameworks must interoperate, when exposing an n8n agent to external callers, or when orchestrating multi-agent teams across trust boundaries. Pairs with enterprise-multi-agent-systems, n8n-agents-official, ai-automation-security-governance, sre-incident-response."
---

# A2A Agent Interop (n8n mapping)

The HTTP of the agent world: any two agents interoperate through one contract.

## Source (adopted baseline)

Google A2A specification (open standard, Linux Foundation): Agent Cards for
discovery, JSON-RPC 2.0 transport, stateful Task lifecycle, declared auth —
plus the ADK multi-agent tutorial fail-safe (unreachable downstream =
MANUAL_REVIEW, never silent drop).

## 1. Publish (expose an n8n agent)

Serve an Agent Card at `/.well-known/agent-card.json` (n8n Webhook GET):
name, description, version, endpoint URL, input/output MIME modes,
capabilities (streaming, pushNotifications), skills array (id, name,
description, tags, examples), securitySchemes + requirements (API key, OAuth2,
mTLS — never none in production). Card is the contract: unknown skill id in
a call = `TaskNotFound`-class rejection, never a guess.

## 2. Consume (call a remote agent from n8n)

Flow: fetch card → verify skills/capabilities/auth → `message/send`
(HTTP Request, JSON-RPC 2.0 envelope, server-generated taskId returned) →
track: polling (`tasks/get`), streaming (SSE), or push webhook. Terminal
states only: completed, failed, canceled, rejected. Non-terminal task accepts
follow-up messages (multi-turn). Timeout on EVERY wait; on timeout or
unreachable → route to MANUAL_REVIEW human lane (the ADK fail-safe), never
retry-blindly into a dead peer.

## 3. Orchestrate (host pattern)

A host agent holds the card registry (name → card + connection), decomposes
the request, sends tasks to named remotes, aggregates artifacts. Shared
session/context id across the team; per-agent state stays server-side (never
leak internal state across the boundary). Choose sync (message/send,
short tasks) vs async (submit + subscribe) per task duration, same protocol.

## 4. Harden

TLS in production, auth exactly as the card declares, least-privilege scopes
per skill, push-notification webhooks authenticated + replay-guarded,
idempotency keys on sends (provider retries must not double-execute),
Ctrl-Bus flag to disable a misbehaving remote without redeploy.

## Verification

Card validates against the spec shape, unknown-skill call rejected, timeout
drill routes to MANUAL_REVIEW with full context, replayed send executes once.
Record card versions beside workflow versions — a changing card is a contract
change (see deploy-signoff-governance).
