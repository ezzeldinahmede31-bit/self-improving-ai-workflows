---
name: tool-result-verifier
description: "Tool-result verifier skill (independent re-check before commit, has-keys/matches checkers, JSONL verdict journal). Use when a tool claims success before dependent state commits, when a 200 needs a re-read, or when commit must be conditional on verification. Trigger phrases: 'verify tool result', 're-check before commit', 'trust but verify', 'تحقق مستقل'."
---

# Tool-Result Verifier (Verify Before Commit)

Code: `tool_result_verifier.py` (stdlib only). Protocol:
tool call → claimed result → INDEPENDENT checker (re-read, second
query, predicate over fresh state) → commit state solely on verified
True. `has_keys` / `matches` cover common shapes; crashing checkers
fail closed. Every verdict journals to JSONL with claim hash +
evidence. `commit_if_verified()` without a commit_fn is an explicit
dry run.

## When to use

- Bookings, payments, writes, external calls with real effects.
- Stale-cache suspicion: re-read the source of truth, compare.
- Incident forensics: the journal shows what was claimed vs proven.

## Verification

- `tests/test_p0c_toolverify.py` green (verified commit, blocked
  commit, checker shapes, crash-closed, dry run, journal).
- No dependent state commits on unverified claims — ever.

## Pairs with

`business-invariants` (what correctness means), `egress-firewall`
(safe re-reads), `immutable-audit-log` (verdict archive),
`build-gates-pipeline`.
