---
name: long-term-memory-retriever
description: "Provides persistent memory for the agent. At session start, loads the COMPACT compressed memory `memory/conversation-memory.bin` via `venv/bin/python scripts/memory-encode.py decode` (zlib; ~2x smaller on disk than the .md) and refreshes the skill stack. After significant work, updates `memory/conversation-memory.md` and re-encodes so the next session reads the new compact copy. Trigger phrases: 'remember', 'memory', 'what did we do', 'what happened before', 'conversation history', 'don't forget', any question about past project decisions/skills/tests."
---

# LONG-TERM MEMORY RETRIEVER

## PURPOSE
Make the agent behave as if it has long-term memory while keeping the stored
copy tiny and self-contained on this device. The machine-readable store is the
compressed binary `memory/conversation-memory.bin`; the `.md` is the human
edit form.

## SESSION-START PROTOCOL (must run first in every session)
1. Load memory: run `venv/bin/python scripts/memory-encode.py decode` and read
   the FULL output (integrity line `MATCH` confirms the compact copy is valid).
2. If decode fails or the file is missing, read `memory/conversation-memory.md`
   instead (same content, uncompressed).
3. List `.opencode/skills/` to confirm the pack (17 routing + browser +
   memory skills) so routing references stay valid.
4. Optionally check the `.bin` size to confirm it is the small storage form
   (`ls -la memory/conversation-memory.bin`).

## SESSION-END / AFTER-SIGNIFICANT-WORK PROTOCOL
1. Update `memory/conversation-memory.md` with what changed: new modules,
   new tests + counts, new skills, new security decisions, new known issues.
   Append; never rewrite history sections.
2. Re-encode: `venv/bin/python scripts/memory-encode.py encode` so the compact
   `.bin` always matches the newest `.md` (verify with `decode` → MATCH).
3. If the change is a design trade-off, also append to `KNOWN_ISSUES.md`.

## QUERYING OLD CONVERSATION FACTS
- Because the full compressed memory is loaded at session start, answer past
  questions (skills list, test counts, security decisions, module names) from
  the decoded memory — cite the memory section, then verify against code if
  the claim matters (evidence over memory).

## VECTOR LAYER (optional, Supabase — free 500MB pgvector)
Only when the env vars exist (they do NOT today → skip silently):
- `MEMORY_SUPABASE_URL` + `MEMORY_SUPABASE_ANON_KEY`.
- Upsert: {content: fact, embedding: <pgvector>, project: "default", ts}.
- Retrieve: top-5 facts by cosine similarity, join with the local memory file.
- Rule: store only HARD KNOWLEDGE (decisions, constraints, gotchas, test
  counts) — never raw conversation or code dumps. That is what keeps context
  free and the store small.

## GROUNDING RULES
- Memory is a cache, not authority: verify any claim it contains against code
  or tests before acting on it.
- Never write secrets (`.env`, tokens, keys) into memory files or vectors.
- Keep the `.bin` as the canonical compact copy; the `.md` is only the editable
  source. Re-encode after every memory update.

## Local adaptation
Storage is fully local + compact: `scripts/memory-encode.py` (zlib, ~2x).
A cloud mirror via `scripts/memory-sync.sh` (rentry/catbox) is optional and
stays dormant until the user picks a backend; it is not required for memory
to work.