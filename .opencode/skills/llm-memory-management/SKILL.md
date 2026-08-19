---
name: llm-memory-management
description: "Manages memory for LLM applications: conversation windows, persistent stores, summarization, retrieval of past sessions, and memory eviction, so agents keep long-term context without bloating the prompt. Makes multi-turn assistants and agents coherent across sessions. Use when the user says 'long-term memory', 'session memory', 'conversation window', 'summarize the chat', 'vector memory', 'evict context', or 'remember across sessions'."
---
# llm-memory-management

Memory is what turns a stateless model into a coherent assistant. This skill encodes how to hold short-term conversation state, persist facts and history, compress when the window fills, and retrieve the right memory on demand instead of dumping everything into the prompt.

## Core principles
- Separate memory by lifetime: working window, session state, and durable store; never blur the three.
- Retrieval beats retention: keep durable memory in a store and pull only what the task needs.
- Summarization is lossy by design; preserve identifiers, decisions, and facts, drop chatter.
- The window is a budget: every token added competes with task-relevant instructions.
- Memory writes and reads must be explicit operations, not implied in the system prompt.
- Eviction must be reproducible: when a fact is dropped, the reason is recorded.

## Key patterns
- Sliding window: keep the last N turns plus a rolling summary of everything before the window.
- Summarizing memory: compress older turns into structured notes keyed by topic and date.
- Vector memory: embed facts and queries; retrieve the top-k relevant memories before each turn.
- Entity store: a table of people, projects, and decisions with updated-at timestamps.
- Compaction: when the window is full, merge the oldest turns into a summary and evict details.
- Forget protocol: stale facts are marked, archived, or deleted with an audit entry.

## Applying this to n8n/Python automation
- Store the sessionId and a memory key so every chat turn reads and appends the same conversation.
- Use a Qdrant collection for durable memory: embed facts at write time, retrieve top-k at read time.
- Add a summarize node that compacts the window when the character budget is crossed.
- Keep entity facts in a data table; query it before the AI Agent composes an answer.
- Meter memory reads and writes in the audit table so growth is visible over time.

## Hard rules
- Never write raw PII into a memory store without encryption and access control.
- Never append forever; always pair a write with a retention and eviction policy.
- Never let a retrieved memory override a current explicit instruction.
- Never drop a security-relevant decision silently; record the eviction.

## Pairs with
ai-engineering-foundation-models, memory-systems, context-engineering, n8n-rag-vector-qa, qdrant-ops, evaluation, build-gates-pipeline
