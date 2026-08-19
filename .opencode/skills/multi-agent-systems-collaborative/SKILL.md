---
name: multi-agent-systems-collaborative
description: "Applies Multi-Agent Systems and Collaborative AI to design groups of specialized agents that divide work and share results: role splitting, communication protocols, orchestration topologies, shared state, and conflict resolution. Covers when multi-agent pays off versus a single agent. Use when the user says 'multi-agent system', 'agent team', 'orchestrator and workers', 'delegate to subagents', or 'agents collaborating'."
---
# multi-agent-systems-collaborative

Multi-agent systems divide a task across specialized agents that exchange results instead of one agent doing everything. This skill encodes when the division pays off, how to structure roles and communication, and the coordination patterns that keep the group coherent.

## Core principles
- Add agents only when the task genuinely splits across distinct expertise or parallelizable work; otherwise one agent is cheaper and more reliable.
- Each agent needs a narrow role, a clear input contract, and an explicit output contract.
- Communication is structured: pass messages with a sender, topic, payload, and schema, never free-form text.
- The orchestrator owns the goal, the plan, and the merge; workers own their slice.
- Shared state must be explicit and conflict-resolved, not implicitly overwritten by parallel writes.
- Every decision point that matters gets a deterministic check, not another agent's opinion.

## Key patterns
- Orchestrator-worker: planner distributes tasks, workers execute, planner integrates results.
- Supervisor: one agent reviews and corrects worker output before it is accepted.
- Debate or council: several agents argue for verdicts, a synthesis step reconciles them.
- Pipeline: agents run in sequence, each consuming the previous agent's structured output.
- Blackboard: agents read and write to a shared store, coordinating through the data instead of direct calls.

## Applying this to n8n/Python automation
- Model each agent as an AI Agent node; wire tools and sub-workflows through the ai_tool and ai_languageModel connections.
- Use sub-workflows for isolated worker logic and the Execute Workflow node for each delegation step.
- Pass structured JSON across agents; validate the schema at each handoff with a Code node.
- Implement the blackboard as a data table or vector store that all agents read and write.
- Add a final deterministic validation node that checks the merged output against the goal before delivery.

## Hard rules
- Never spawn parallel agents that write to the same state without a merge and conflict policy.
- Never let a worker invent its own output contract; the schema is fixed at design time.
- Never use a second agent to check a first agent's work when a mechanical validator exists.
- Never build a multi-agent system before proving a single agent fails the task.

## Pairs with
multi-agent-patterns, n8n-agents-official, llm-council, autonomous-agent-patterns, n8n-rag-vector-qa, build-gates-pipeline
