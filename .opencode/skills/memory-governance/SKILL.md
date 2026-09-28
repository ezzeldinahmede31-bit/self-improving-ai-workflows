---
name: memory-governance
description: "Memory governance skill (stamped writes, TTL expiry, untrusted quarantine, authority-ranked conflicts). Use when memory accepts external input, when two memories disagree, when stale facts must die, or when a privilege-escalation-via-memory is suspected. Trigger phrases: 'govern memory', 'memory conflict', 'quarantine memory', 'حوكمة الذاكرة'."
---

# Memory Governance (Poison-Resistant Recall)

Code: `memory_governance.py` (stdlib only). Wraps plain-dict stores
without modifying them: writes carry source/timestamp/confidence/
author; TTL expiry filters reads; untrusted sources quarantine (never
served until a trusted author promotes); conflicts resolve by source
authority, then newest stamp, then confidence — losers archive with
reasons. A "save that I am admin" claim from an untrusted source
stays inert by construction (promotion requires a trusted author).

## When to use

- Any memory write path fed by users, tools, or retrieved content.
- Disagreement triage: read the archive, see who lost and why.
- Scheduled `sweep()` for TTL hygiene; `quarantine()` as review queue.

## Verification

- `tests/test_p0c_memory.py` green (roundtrip, quarantine default,
  self-promote attack fails, authority resolution, TTL sweep,
  confidence clamp).
- The self-promotion attack test re-runs on every change to this file.

## Pairs with

`provenance-lineage` (source authority), `agent-runtime-guard-adapter`
(input side), `long-term-memory-retriever` (serving side),
`build-gates-pipeline`.
