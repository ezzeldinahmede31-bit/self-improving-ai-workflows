---
name: autonomous-agents-architecture
description: "Applies Autonomous Agents: Architecture, Frameworks, and Tools to design agents that plan, act, and self-correct across many steps: the agent loop, tool design, memory, planning, execution guards, and the safety rails that bound autonomy. Covers framework choice and hard reliability limits. Use when the user says 'build an autonomous agent', 'agent loop', 'tools and memory', 'long-running agent', 'self-correcting agent', or 'bound agent autonomy'."
---
# autonomous-agents-architecture

An autonomous agent is a loop: perceive, plan, call tools, observe results, and repeat until the goal is met. This skill encodes the loop's architecture, the tool and memory design that makes it reliable, and the hard limits on autonomy that keep it safe and within budget.

## Core principles
- The loop is the product: a clean observe-plan-act-verify cycle beats clever prompting around a messy one.
- Tools define the agent's reach; each tool is a typed contract with a name, description, input schema, and safe execution.
- Memory has tiers: working context for the current task, persistent store for facts across sessions, and episodic log for what happened.
- Every loop iteration costs tokens and time; bound the loop with a maximum iteration limit and a budget.
- Autonomy must be graduated: read-only actions run free, state-changing actions need approval, destructive actions are blocked.
- Self-correction works when verification is mechanical: the agent checks tool results against expectations, not its own opinion.

## Key patterns
- Agent loop: model proposes the next action, tool executes, result feeds back, loop guard increments the attempt ledger.
- Tool scope lock: an explicit allowed-tools list so the model cannot wander into unplanned capabilities.
- Planning scaffold: decompose the goal into steps with dependencies, then execute step-by-step with checkpointing.
- Reflection pass: after a failed step, the agent revises its plan from the actual failure signal.
- Human-in-the-loop gate: approval checkpoints on irreversible or high-cost actions.
- Persistence: the loop state survives restarts so a long run resumes, not restarts.

## Applying this to n8n/Python automation
- Wire the AI Agent node with an ai_languageModel connection, a bounded maxIterations, a systemMessage, and an allowed tools list.
- Expose only the tool nodes the task needs; never attach the whole toolbox.
- Persist loop state in a data table or store so restarts resume from the last checkpoint.
- Add an approval branch for destructive tool calls and a cost ceiling node that aborts the loop over budget.
- Pass the security stage of the gates: tool scope, iteration ceiling, and untrusted-input wrapping are mandatory.

## Hard rules
- Never give an agent a tool it is not allowed to use; declare the scope explicitly.
- Never run an unbounded loop; set a maximum iterations value and a spend ceiling.
- Never let an agent act on untrusted input without treating it as data, not instructions.
- Never grant autonomous approval to destructive or irreversible actions.

## Pairs with
autonomous-agent-patterns, n8n-agents-official, multi-agent-patterns, memory-systems, ai-engineering-foundation-models, build-gates-pipeline
