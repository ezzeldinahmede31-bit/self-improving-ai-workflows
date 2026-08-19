---
name: enterprise-multi-agent-systems
description: "Designs enterprise-grade multi-agent systems: role-based agent teams, orchestrator-worker and peer topologies, shared tools and memory, handoffs, guardrails, and observability across many agents. Makes complex work decompose safely across specialized agents. Use when the user says 'multi-agent', 'agent team', 'orchestrator', 'supervisor', 'handoff', 'agent roles', 'swarm', or 'agents with shared tools'."
---
# enterprise-multi-agent-systems

Enterprise work decomposes across specialized agents that share tools, memory, and a coordination layer. This skill encodes the topologies, handoff rules, and governance that keep a multi-agent system coherent, auditable, and safe instead of a tangle of competing models.

## Core principles
- Define each agent by role and scope; an agent with no boundary invents work and steals tool use.
- One coordinator owns the plan; workers execute narrow tasks and report, they do not re-plan.
- Handoffs must carry explicit state: what was done, what remains, and what the next agent may touch.
- Shared tools and memory require permissions; agents see only what their role allows.
- Every agent action lands in a shared log with agent, tool, input, and output for replay.
- A multi-agent system fails on coordination before capability; design the flow, then the agents.

## Key patterns
- Orchestrator-worker: a supervisor decomposes, dispatches, and merges; workers are single-purpose.
- Peer topology: independent agents collaborate through a shared queue or event stream.
- Handoff contract: a structured message with goal, completed steps, open risks, and next owner.
- Shared service layer: tools and memory exposed once, with role-scoped permissions on each.
- Guardrail agents: a policy agent reviews outputs for security and scope before they escape.
- Observability mesh: trace every tool call across agents with a correlation ID per request.

## Applying this to n8n/Python automation
- Build each role as its own n8n agent workflow with a fixed system prompt and an explicit allowed-tools list.
- Use Execute Workflow nodes for handoffs, passing a structured handoff payload to the next agent.
- Wire every agent's ai_languageModel output to the correct model node and cap maxIterations.
- Gate the orchestrator output through a guardrail node that checks the response before delivery.
- Emit a correlation ID at the trigger and log it at every agent step for end-to-end tracing.

## Hard rules
- Never give an agent a tool its role does not need; scope is a security control.
- Never let a worker mutate shared state without recording the change.
- Never allow unbounded iteration; every agent loop has a ceiling.
- Never deploy a multi-agent workflow that fails the agent-wiring gate checks.

## Pairs with
multi-agent-patterns, autonomous-agent-patterns, n8n-agents-official, ai-engineering-foundation-models, memory-systems, llm-council, build-gates-pipeline
