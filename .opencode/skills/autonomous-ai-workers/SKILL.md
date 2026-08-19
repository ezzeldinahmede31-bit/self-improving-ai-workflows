---
name: autonomous-ai-workers
description: "Designs background AI workers: always-on agents that poll triggers and queues, decide with a model, act through tools, and report results — with idempotency, persistence, supervision, and cost bounds. Covers the patterns that keep an unattended worker safe and reliable. Use when the user says 'background AI worker', 'autonomous worker', 'unattended agent', 'queue-driven agent', 'monitor and act', or 'supervised automation'."
---
# autonomous-ai-workers

An autonomous AI worker is an unattended agent that continuously watches a trigger source and acts on what it finds. This skill encodes worker design: trigger ingestion, model-driven decisioning, tool execution, persistence, supervision, and the cost and safety bounds that make unattended operation safe.

## Core principles
- A worker must be resumable: every unit of work is persisted before, during, and after execution.
- Idempotency is the safety net: reprocessing the same event must never duplicate side effects.
- Triggers are sources of truth; the worker records what it consumed so nothing is lost or replayed twice.
- The model decides, tools execute, and the human supervises: sensitive actions route to approval.
- Cost is bounded: the worker stops itself when spend or runtime exceeds a ceiling.
- Supervision means alerting: the worker reports what it did and surfaces anything it could not do.

## Key patterns
- Poll-and-dispatch: a schedule or queue trigger feeds one item at a time into a decision node.
- Claim-then-process: mark an item in-flight before work, then complete or release it, so two workers never collide.
- Idempotent action: every side-effecting tool call carries a dedupe key derived from the triggering event.
- Retry ladder: transient failures retry with backoff; persistent failures move to a dead-letter queue with an alert.
- Approval gate: destructive or external-facing actions pause until a human confirms.
- Heartbeat reporting: the worker writes status and results to a log table on a fixed cadence.

## Applying this to n8n/Python automation
- Build the worker as an n8n workflow started by a schedule trigger or a queue node, processing one item per run.
- Persist claim and completion state in a data table keyed by the event id, so restarts resume rather than duplicate.
- Give every external action node a dedupe key and an error output with a backoff retry.
- Add a supervisor workflow that reads worker logs, raises alerts on failures, and opens approval tasks for blocked items.
- Set a spend ceiling node that stops the worker when the budget is exhausted.

## Hard rules
- Never process an event without claiming it first, or two workers may duplicate the work.
- Never let a worker run without a dedupe key on every side-effecting action.
- Never deploy an unattended worker without a dead-letter path and an alert.
- Never allow unbounded spend or runtime on an unattended worker.

## Pairs with
autonomous-agent-patterns, long-horizon-prompting, n8n-agents-official, memory-systems, ai-engineering-foundation-models, build-gates-pipeline
