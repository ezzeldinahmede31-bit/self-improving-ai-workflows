---
name: building-agentic-ai-systems
description: Applies Biswas & Talukdar's Building Agentic AI Systems method to construct autonomous agents from four core components — planning, memory, tool use, reflection — wired as an explicit perceive-plan-act loop rather than prompt hope. Covers ReAct-style reasoning-and-acting, typed tool/function-calling schemas, short-term vs long-term memory separation, multi-agent orchestration topologies (orchestrator-worker, peer handoffs), guardrails and bounded autonomy, and agent evaluation before production. Use when the user says 'build an AI agent', 'autonomous agent', 'agent architecture', 'planning and tool use', 'ReAct', 'agent memory', 'multi-agent orchestration', 'agent guardrails', 'evaluate my agent', 'اعمل وكيل ذكي', 'بني agent مستقل'. Pairs with autonomous-agents-architecture, agentic-workflows, enterprise-multi-agent-systems, ai-automation-security-governance, evaluation, n8n-agents-official.
---

## Purpose

An agent is not "a model in a loop". It is a system with four named components, each designed separately and each testable alone:
1. **Planning** — decompose the goal, sequence steps, replan on failure.
2. **Memory** — working state for the current task; long-term store across sessions.
3. **Tool use** — typed, described capabilities the model can invoke.
4. **Reflection** — self-check of outputs and actions before they become final.

## Gate 1 — Component inventory before code

For every agent request, write the four components down explicitly. If planning is implicit in the prompt, or memory is "the chat history", or tools lack schemas, or nothing checks its own output — the design is incomplete. Fix the component, not the prompt.

## Gate 2 — Reasoning-and-acting discipline

Use the ReAct shape: thought → action (a real tool call with typed arguments) → observation → next thought. Every action must map to a declared tool schema (name, purpose, parameters, return type) — the schema IS the prompt the model routes on. Vague tool names produce wrong tool picks.

## Gate 3 — Memory separation

Short-term memory holds the current task's scratchpad and recent turns; long-term memory holds durable facts retrieved on demand. Never stuff unbounded history into context — summarize or retrieve. Persist long-term state outside the prompt (store, vector index, or file).

## Gate 4 — Multi-agent topology choice

Single agent first. Split into multiple agents only when roles genuinely differ (orchestrator-worker for decomposable work, peer handoff for stage-specialized pipelines). Every inter-agent boundary needs a defined message contract; every orchestrator needs termination conditions.

## Gate 5 — Bounded autonomy + guardrails

Cap iterations, whitelist tools per role, require human approval for destructive/state-changing actions, log every decision trace. Autonomy without ceilings is a liability, not a feature.

## Gate 6 — Evaluate before production

Test agents on scenario suites: success rate, step efficiency, tool-choice correctness, failure recovery. A demo pass proves nothing; measured behavior does.

## Output contract

Deliver agents with: the filled four-component table, tool schema list, memory strategy, topology verdict, autonomy limits, and eval results. Missing any item = not done.
