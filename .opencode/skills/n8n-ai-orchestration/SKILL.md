---
name: n8n-ai-orchestration
description: "Applies the n8n orchestration model to AI systems: agents, models, tools, vector stores, and memory assembled as nodes in one executable graph, with triggers, branches, error paths, and human checkpoints. Covers the wiring rules that keep an AI workflow observable and recoverable. Use when the user says 'n8n AI orchestration', 'assemble an AI workflow', 'AI agent in n8n', 'chat workflow', 'tool-calling workflow', or 'orchestrate agents'."
---
# n8n-ai-orchestration

n8n AI orchestration treats an AI system as an executable graph: every model call, tool, memory store, and human checkpoint is a node, and the workflow engine provides triggers, retries, error paths, and audit. This skill encodes how to assemble and operate AI workflows on n8n so they stay observable and recoverable.

## Core principles
- The graph is the contract: structure, connections, and error handling are explicit, not hidden in code.
- Every AI node declares its role: model, tool, memory, retriever, or output — with typed connections.
- Failure is a first-class path: each branch has an explicit error output and a recovery step.
- State is explicit: conversations, jobs, and progress live in a store, not in the node memory.
- Observability is designed in: logs, item provenance, and audit trail flow out of every run.
- Human review is a node like any other: approval checkpoints gate irreversible actions.

## Key patterns
- Trigger-to-model chain: webhook or chat trigger feeds a model node whose output feeds validation and then downstream tools.
- Tool scope wiring: the agent node connects only to the tool nodes the task requires, via the ai_tool output.
- Error boundary: a node-level error output routes failures to a retry, a fallback, or a human review branch.
- State persistence: conversation and job state stored in a data table or store so a rerun resumes cleanly.
- Checkpoint gate: after each sensitive step, pause for approval or confirmation before continuing.
- Provenance chain: every node writes which inputs produced its output, so any answer is traceable.

## Applying this to n8n/Python automation
- Build node-by-node: generate one node, check it against the schema cache, wire it, then continue.
- Connect the AI Agent node with an ai_languageModel and an explicit allowed-tools list; never attach the full toolbox.
- Add an error output to every external call and route failures to a fallback branch.
- Persist multi-turn state in a data store keyed by session so restarts do not lose context.
- Pass the full build gates before deploy: security, quality, integrity, precision, and the RAG stage when vector stores are involved.

## Hard rules
- Never deploy an AI workflow with an unhandled error path on a model or tool call.
- Never give an agent tool access beyond its declared scope.
- Never run an AI node without a bounded iteration limit and a spend ceiling.
- Never deliver an AI workflow that has not run end-to-end with real triggers.

## Pairs with
n8n-agents-official, n8n-workflow, ai-engineering-foundation-models, autonomous-agent-patterns, multi-agent-patterns, build-gates-pipeline
