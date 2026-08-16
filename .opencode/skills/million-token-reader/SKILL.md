---
name: million-token-reader
description: "Reads corpora that are 10-100x our context window (docs, books, transcripts, big repos, logs, full datasets — 50K tokens and up, up to a million) with ZERO forgetting: deterministic segmentation into structural chunks, a disk-persisted digest per chunk, a ledger that accounts for EVERY token (gaps/overlaps are detected, coverage is verified), then question-answering by targeted re-read of the exact chunks involved. Emulates the 'reads 1M tokens in one shot' capability the same way a librarian emulates a man with a photographic memory: nothing is skipped, everything is indexed, any fact is retrievable on demand. Use whenever a task needs the WHOLE of a large corpus understood ('read this entire book/repo/series and answer anything about it', 'understand all 400 transcripts', 'analyze this whole dataset'), or when a task would otherwise sample/forget large input. Trigger phrases: 'اقرأهم كلهم', 'read everything', 'whole dataset', 'all the files', '1M tokens', 'كوربوس كبير', 'don't forget anything', 'understand this book'. Pairs with: long-context-sharding-engine, codebase-mind-persistence, context-budget-governor, evidence-over-memory, long-term-memory-retriever."
---

# Million-Token Reader (sharded, forget-proof)

Goal: understand an entire huge corpus so that ANY question about ANY part
of it can be answered — without a million-token window. We do it with
mechanical segmentation + disk-persisted digests + a coverage ledger that
proves nothing was skipped.

Principle: our memory is unreliable; the DISK is reliable. Every fact read
goes into a digest FILE before the next chunk is read. Losing the
conversation's memory costs nothing — the digests are the memory.

## Protocol

### Phase 0 — Inventory & ledger (before reading anything)

Create the ledger: `memory/corpus-ledgers/<corpus-id>.json`

```json
{
  "corpus_id": "docs-v2",
  "source": "<path or URL list>",
  "total_segments": 0,
  "ledger": [
    {"seg": 1, "source_file": "...", "range": "L1-1200", "tokens": 0, "status": "pending"}
  ]
}
```

Rules:
- Enumerate EVERY file/URL of the corpus — none may be anonymous.
- Estimate tokens per item (`wc -m`/4 or known char→token ratio); the ledger
  MUST total ≈ corpus size. If a file is unaccounted, the job is not done.

### Phase 1 — Deterministic segmentation (never split mid-entity)

Split boundaries (in priority order):
1. Physical structure: one file → its own segment when files exist.
2. Semantic units: Markdown `#`/`##` sections, book chapters, JSON
   top-level records (never half an object), function/class blocks in code
   (never half a function — use AST/indentation boundaries).
3. Fallback: line-batch chunks broken at blank lines / paragraph ends.

Target chunk size: **5–8K tokens max** (this model's reliable window).
Numbered segments: `seg-001.md`, `seg-002.md`, … — each entry recorded in
the ledger BEFORE reading.

### Phase 2 — Sequential read + digest (the "no forgetting" step)

For each segment IN ORDER, one at a time:
1. Read the exact range (full read — never truncated summaries of the read).
2. Write `memory/corpus-digests/<corpus-id>/seg-NNN.md` with:

```markdown
# seg-NNN | <source> L<start>-<end> | ~<tokens> tok
## Facts (who/what/when/numbers — EVERY concrete claim)
- ...
## Entities & symbols (names, IDs, functions, params, schema fields)
- ...
## Decisions / instructions / constraints stated
- ...
## Data refs (tables, indices, offsets, paths worth revisiting)
- ...
## Cross-refs (explicit links to other segments/docs)
- ...
```

3. Flip ledger status `pending → read` with the real token count taken from
   the read (not the estimate).

NEVER proceed to seg-N+1 until seg-N's digest is written and verified
(file exists, non-empty). This is the anti-forgetting invariant.

### Phase 3 — Coverage gate (prove completeness)

Run the mechanical check; pass = "the whole corpus was read":
- every ledger row `status == read`,
- digest file count == ledger segment count,
- ranges are gap-free and overlap-free per source file (concatenate →
  covers the full file),
- Σ actual tokens ≈ Σ estimate (large deviation = an unmapped file → go back
  to Phase 0).

Only after GREEN may questions be answered "from the corpus".

### Phase 4 — Query resolution (answer anything, cheaply)

1. Load ALL digest heads (facts + symbols sections only — kind of like a
   table of contents; fits in ~1/10 of the corpus).
2. Pick the 1..N candidate segments for the question.
3. Targeted full re-read of ONLY those segments (exact ranges from ledger).
4. Answer, citing `seg-NNN / source / L-range` for every claim — never an
   uncited fact. If the answer needs synthesis across far-apart segments,
   do it in a small pass reading their digests together, then verify each
   cited part by re-reading its segment.

### Phase 5 — Drift maintenance (corpus changes later)

- Only changed segments get re-read; their digests are replaced, ledger
  re-checked. Unchanged segments keep their digests (no re-read).

## Worked example (this workspace, 2026): AIME transcripts/benchmarks

A 400-transcript corpus (~2M tokens) becomes: 1 ledger file + ~350 digests
(~6K tokens each) + one 3K-token digest INDEX. A question "which problems
did we score wrong" → index → 4 candidate segments → 4 targeted reads →
answer with citations. Total spent per query: ~25K tokens instead of 1M.

## Honest limits

- We cannot cross-attend instantly between 50 far-apart segments like a
  native 1M window can; synthesis that needs many distant parts takes
  multiple targeted passes (each still cheap).
- The digests must be written with discipline — this protocol is only as
  forget-proof as the invariant in Phase 2. If interrupted mid-run,
  RESUME reads at the first `pending` segment; never trust memory of where
  you stopped.