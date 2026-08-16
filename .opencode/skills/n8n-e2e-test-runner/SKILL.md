---
name: n8n-e2e-test-runner
description: "Run a real end-to-end integration test after deploying an n8n workflow: hit the live webhook/trigger with a sample payload and verify it returns a 200 OK (plus capture downstream results). Use ONLY after creating, updating, or re-wiring an n8n workflow that exposes a webhook trigger, and whenever the user asks 'does it actually work live'."
---

# n8n E2E Integration Test Runner

Pinned data proves the canvas runs; this proves the LIVE wiring works (webhook reachable,
credentials valid, external APIs responding).

## When to run
- After `n8n_create_workflow` / `n8n_update_full_workflow` on a workflow with a webhook trigger.
- When the user reports "the node works manually but nothing arrives".
- Before telling the user "it's done" — a live 200 is part of done.

## Procedure
1. From the workflow's trigger node, read:
   - Webhook path (e.g. `/webhook/leadgen` or a custom `path`).
   - HTTP method (GET/POST/PUT).
2. Determine the test payload:
   - If a pinned/mock payload exists → reuse it (realistic fields, placeholders for secrets).
   - Else build a minimal realistic payload that satisfies the first node's schema.
3. Call the n8n MCP `n8n_test_workflow` (or direct API) with `waitForResponse: true`.
4. Assert:
   - HTTP status is 2xx (expected 200/201). Anything else → FAIL.
   - Response body includes expected downstream marker (e.g. `telegramMessageId`,
     `recordsWritten`, `csvPath`) if the design promises it.
5. Then inspect the execution: `n8n_executions` `action: list` filtered by workflowId,
   latest run status. Confirm ALL nodes completed (no `continueOnFail` swallow):
   - If a node errors → report the node name + error via the execution detail
     (`action: get`, `mode: error`).
6. Cleanup: if the test created real records (Supabase/CSV), note them for the user.

## Outcome reporting template
```
E2E result:
  webhook  → POST {base}/webhook/{path}
  status   → ✅ 200 OK
  run id   → {executionId}
  duration → {ms}
  nodes    → N passed, 0 failed
  side effects → wrote {n} rows / sent {n} msg (check duplicates)
```

## Rules
- Never skip the live test when a webhook exists — manual "Execute Workflow" is not a substitute.
- If the test fails, DEBUG until green or clearly route to a known blocker (e.g. missing
  credential → per credential-security-guard, pause and ask user to wire it).
- Do not fire repeated spammy tests; one clean run with the same payload is enough.
- For destructive effects, prefer a dry-run/test payload that cannot corrupt production data.