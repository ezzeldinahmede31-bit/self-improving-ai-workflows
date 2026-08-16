---
name: durable-experience-consolidator
description: "Turns a finished working session into durable cross-session knowledge so nothing important is forgotten after the chat ends: extracts principles, verified facts, failures with causes, and reusable recipes; writes them to the project memory; and encodes them to the compact store. Use at the END of any substantial task or before closing. Trigger phrases: 'save what we learned', 'don't forget this', 'end of session', 'consolidate', 'write it to memory'."
---

# DURABLE EXPERIENCE CONSOLIDATOR

## DIRECTIVE
An ephemeral mind can still ship durable knowledge. Before a working session
ends, distill what was learned into the project memory file so a future session
(which has no memory of this one) starts already knowing it. Learn from
FAILURES too — they are the highest-value knowledge.

## CONSOLIDATION PROTOCOL (run at session end / after big tasks)
1. **Extract principles:** 1–3 durable rules learned this session, stated
   so they apply to FUTURE tasks, not just this one (e.g., "always pre-read a
   file with Edit"). Skip task-specific noise.
2. **Extract verified facts:** numbers, paths, versions, behaviors — each with
   its evidence (test/output/file:line). Facts without evidence are opinions.
3. **Extract failures + causes:** what failed, the ROOT cause, and the one-line
   rule that prevents it. This is the anti-repeat loop.
4. **Extract recipes:** reusable command sequences / patterns that worked
   (e.g., the exact playwright+real-Chrome startup line).
5. **Write to memory:** update `memory/conversation-memory.md` (append-only,
   never rewrite) under the matching section, then `venv/bin/python
   scripts/memory-encode.py encode` to refresh the compact `.bin`, then verify
   `decode` says integrity MATCH.

## LOCAL-HOOK RULES
- Every file write is checked: no secrets, no test-only leftovers — secrets go
  to `.env`/vault, sessions stay under `memory/.sessions/` (gitignored).
- Test the extract, don't trust it: if a fact affects code, run the affected
  test class before recording it as fact.
- If the session changed the suite, record the NEW passing count exactly
  (`venv/bin/python -m pytest` output), not the old.

## Local adaptation
Target file is `memory/conversation-memory.md`; encode via
`scripts/memory-encode.py`. The memory is loaded at every session start by
`long-term-memory-retriever`, so consolidation here IS the bridge between
sessions. Combine with `progressive-context-compressor` (in-session control) —
this skill owns the across-session write.