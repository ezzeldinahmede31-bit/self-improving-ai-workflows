---
name: long-context-sharding-engine
description: "Prevents context degradation by sharding large documents into JIT task-scoped chunks and dynamically routing massive contexts to long-context frontier models. Never dump unprocessed context >30k tokens into a lightweight model — instruction-following decay destroys the output. Use when handling large docs, multi-file codebases, long API references, transcripts >30k tokens, or any prompt where recency bias would override appended instructions. Trigger phrases: 'large context', 'long document', 'context too big', 'shard the context', 'chunk this file', 'instruction following decay', 'huge codebase'."
---

# LONG-CONTEXT SHARDING & DEGRADATION ENGINE

## DIRECTIVE

Never dump unprocessed large context (>30k tokens) into lightweight models.
Enforce context extraction, chunking, or automatic routing to high-context
models (Kimi K3 / Claude) to prevent instruction decay. Window size is not
retention: a 13B model forgets the top of the prompt even inside a huge window.

## CONTEXT HANDLING WORKFLOW

```
        [Raw Context > 30,000 Tokens]
                      │
      ┌───────────────┴────────────────┐
      ▼                                ▼
[Option A: Extract & Shard]    [Option B: High-Context Escalation]
 * Parse API schemas/structs     - Route directly to Kimi K3 (1M+ window)
 * Extract only the endpoints    - Retain multi-file relationship DAGs
   THIS task actually touches    - All-or-nothing reasoning: do not shred
 * Feed JIT Task-Scoped RAG        intertwined logic
```

## RULES FOR CONTEXT MANAGEMENT

1. **Threshold Trigger:** If prompt context > 32,000 tokens:
   - **Path 1 (Extractable Task):** Run local Regex/Parser to isolate
     relevant sections -> pass a small JIT payload to Tier 1/2. Most tasks
     only need a slice of an API reference or a single file of a repo.
   - **Path 2 (Intertwined Reasoning):** Override Tier 1 and route the WHOLE
     context directly to **Kimi K3** or **Claude Opus**. Cross-file dependency
     reasoning cannot survive sharding.
2. **Instruction Preservation:** Keep core directives/system prompt appended at
   the VERY END of the user prompt (post-context placement) to defeat recency
   bias and context degradation. Instructions buried in the middle of a long
   prompt are instructions lost.
3. **Chunk Integrity:** Each shard is internally complete (schema + endpoint +
   auth) and carries provenance (source path, offset, parent doc id) so the
   verifier can trace claims back to the original.
4. **Verification After Shard:** Re-check the final artifact against the
   sharded source — a shard that lost its auth section will produce a
   beautifully plausible, broken workflow.

## INTEGRATION

Sits in front of `rag_engine.RagMemory` and the JIT pipeline in
`master_system_orchestrator.TaskScopedJITRAG`: big inputs pass through Extract
& Shard (Path 1) when scoped, or escalate the whole context (Path 2) when
intertwined. Complements `cognitive-task-triager` (huge-context tasks auto-rank
to the high-context tier).