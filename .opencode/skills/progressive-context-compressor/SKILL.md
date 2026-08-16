---
name: progressive-context-compressor
description: "Survives long sessions without losing fidelity: instead of a single late collapse, maintains a rolling structured summary as the conversation grows, decides WHAT is droppable and WHAT is load-bearing, and rehydrates detail on demand. Use when the session is long, many turns, large file reads, or nearing the context limit. Trigger phrases: 'context is full', 'remember the beginning', 'long session', 'summarize what we did', 'we are losing track'."
---

# PROGRESSIVE CONTEXT COMPRESSOR

## DIRECTIVE
Do not wait until the context window is about to explode. Compress continuously
and deliberately: every N substantial turns, collapse the conversation into a
lossless-enough capsule so old facts survive without keeping every token.

## COMPRESSION POLICY (what stays / what goes)
**Always KEEP (load-bearing):**
- Decisions and their reasons (even if code changed, the reason is durable).
- Verified facts + their evidence pointer (test name, file:line, output).
- Open problems, rejected options and why, user constraints and preferences.
- Security-relevant settings and secret-management rules (never summarized away).
- Exact identifiers: module/class/function names, DB tables, env var names.

**Drop freely (no memory value):**
- Intermediary chatter, failed attempts (keep only the winning path + 1-line
  "why X failed"), repeated tool-output, cosmetic/format discussions.

## MECHANISM
1. Every ~10 substantial turns (or whenever the visible context is >70% full),
   write a compressed capsule: `[CAPSULE] <goal> | decided: <x> | facts: <a,b,c>
   | open: <y> | evidence: <z>`.
2. Keep capsules ONLY as landmarks — replace the verbose transcript you no
   longer need to hold with the capsule, keeping the most recent ~5 turns live.
3. Rehydrate on demand: if a user asks about an old decision, read the capsule
   and pull the exact file/line via `evidence-over-memory` before answering —
   never rely on the compressed text alone for exact numbers.

## RULES
- Never summarize a security decision or a secret rule away — they are
  load-bearing by definition.
- Never claim a number (test counts, sizes, timings) from memory: cite the
  evidence, or re-run.
- Compression is lossy for PROSE, lossless for IDENTIFIERS and DECISIONS.
- If unsure whether something is load-bearing, keep it.

## Local adaptation
The durable version of this is the project's compact memory:
`memory/conversation-memory.md` (+ `.bin` via `scripts/memory-encode.py`),
loaded at session start by `long-term-memory-retriever`. Use this skill IN
SESSION for mid-conversation control; use the memory files for ACROSS-session
durability. The suite stays green throughout: `venv/bin/python -m pytest`.