---
name: agentic-workflows
description: "Designs agentic workflows where LLMs take actions through tools: planning loops, tool selection, structured outputs, verification of tool results, and stopping conditions. Turns a passive chat model into a reliable doer inside n8n and Python. Use when the user says 'agentic workflow', 'tool-using agent', 'plan and act', 'agent loop', 'function calling', 'verify the tool result', or 'when should the agent stop'."
---
# agentic-workflows

An agentic workflow gives an LLM tools and a loop: it plans, calls a tool, reads the result, and repeats until done. This skill encodes the loop design, tool contracts, and stop conditions that keep the agent effective, bounded, and trustworthy.

## Core principles
- The loop is plan, act, observe, decide; each step is a distinct, verifiable operation.
- Tool calls must have a contract: name, input schema, output shape, and error format.
- The model proposes tool calls; the system executes them and feeds back real results.
- Verification beats trust: check the tool result against expectations before the next step.
- Every agent needs a stop condition: goal met, budget spent, or escalation to a human.
- Errors are data: a failed tool call feeds back as an input for the next decision, never a crash.

## Key patterns
- Plan-then-execute: the model writes a step list, then executes each step with verification.
- ReAct loop: interleave reasoning and tool calls, reading tool output after every action.
- Tool-gated actions: destructive operations require a second approval inside the loop.
- Structured output: force the model's tool calls into a validated JSON schema before execution.
- Reflection step: after the work, the model reviews its own output against the goal.
- Escalation rule: when the loop fails twice on the same step, stop and ask a human.

## Applying this to n8n/Python automation
- Model the loop in n8n with an AI Agent node whose tools are workflow tools with clear descriptions.
- Declare allowed_tools on the agent so it can only reach the nodes its task needs.
- Cap maxIterations so a confused loop cannot run indefinitely against paid APIs.
- Make each tool node return structured JSON and handle errors with continueOnFail into an error branch.
- Log every tool call with its result so the loop is replayable in the audit trail.

## Hard rules
- Never let the model execute a tool call it proposed without the system running and verifying it.
- Never grant an agent a tool whose side effects do not have an approval gate.
- Never allow an unbounded loop; maxIterations and a timeout are mandatory.
- Never trust a tool's success status without checking the returned payload.

## Pairs with
n8n-agents-official, ai-engineering-foundation-models, autonomous-agent-patterns, multi-agent-patterns, evaluation, build-gates-pipeline
