---
name: n8n-delivery-verification-gate
description: MANDATORY gate before delivering ANY n8n workflow to the user. Proves the workflow actually RUNS end-to-end with no problems (real execution, not just validation), and audits the user's original commands one-by-one to confirm every requirement was executed and the agreed result actually appeared. Never hand over a workflow that has not been executed and verified. Trigger on EVERY n8n workflow delivery, fix, or update — 'سلمني الشغل', 'deliver the workflow', 'is it done', 'جربها', 'شغال ولا لأ', any workflow completion.
---

# n8n Delivery Verification Gate

The user's rule: **"متسلمنيش حاجة تاني قبل ما تجربها وتطلع شغالة"** — never deliver anything before you test it and it actually works.

This skill is the mechanical, evidence-based gate that makes that rule enforceable. Two mandatory passes:

1. **EXECUTION PASS** — the workflow must actually run on the live n8n instance and the agreed output must appear. Validation (0 errors) is NOT proof — a workflow can validate perfectly and still produce 0 items (seen live: SPARQL `data` string bug — validation green, execution dead).
2. **REQUIREMENTS AUDIT PASS** — the user's original commands must be checked one-by-one against evidence, and any deviation reported honestly.

## Phase 1 — Requirements Audit (BEFORE touching anything)

Restate the contract from the user's ACTUAL words (the last message containing the request), as a numbered checklist:

```
REQ 1: <original command, verbatim or near-verbatim>
REQ 2: ...
AGREED RESULT: <what success looks like, e.g. '100 rows with emails/phones in the table'>
```

- If the request is ambiguous, this phase surfaces the ambiguity to the user BEFORE building.
- Keep this checklist — Phase 4 grades each REQ against evidence.

## Phase 2 — Static Verification (fast, cheap, catches most)

1. `n8n_validate_workflow` — MUST be: errorCount 0, warningCount 0 (or documented + justified).
2. Node schema check: every node's `typeVersion` matches the installed version (use `n8n_get_node` / `n8n_validate_node`).
3. Expression check: every `{{ }}` references fields that EXIST in the upstream data structure — walk the chain by hand, field by field (this is where `data`-vs-`json` and `undefined/contact` bugs live).
4. Known-issues pre-flight: run the automation-known-issues-compass gates (credential ambiguity, draft-vs-published, expression v1/v2, webhook paths, onError/continueOnFail conflicts).
5. Credential guard: no hardcoded keys in nodes; credentials by ID.

Static green is REQUIRED but NOT SUFFICIENT. Proceed to Phase 3.

## Phase 3 — Real Execution Proof (the actual gate)

The workflow must be executed on the live instance and every stage inspected:

1. **Trigger**: if the workflow has a Manual Trigger (or Schedule), temporarily add a `n8n-nodes-base.webhook` node ("Test Trigger", POST, path like `<wf-slug>-test`) connected to the first data node, and ACTIVATE the workflow so the webhook is live. If it already has a Webhook/Form/Chat trigger, use it directly.
2. **Run**: `n8n_n8n_test_workflow` with `waitForResponse: false` (the run is async), then poll `n8n_n8n_executions list` until the new execution is `finished`.
3. **Inspect the FULL path** with `n8n_n8n_executions mode=error` (fastest complete path + error info) or `mode=preview`:
   - status MUST be `success` (or every failure node has an intended error-handling path).
   - EVERY expected node must appear in `executionPath` with an item count.
   - **Item count trap**: watch for nodes showing `itemCount: 0` or collapsed counts (1 instead of 100). A node that receives 100 items and outputs 1 is a hidden bug (seen live: Extract collapsed a 100-item list). A terminal node with 0 items = dead chain.
   - If `status: error`, get `mode=error` → `errorInfo.primaryError` names the failing node — fix, re-run, NEVER deliver with a known error.
4. **Verify the AGREED OUTPUT appeared** (the result the user asked for):
   - data table → `getRows` count == expected
   - message/text → inspect Build-node output items (sample item JSON)
   - HTTP/webhook downstream → check side effects
5. **Restore**: remove the test Webhook trigger, restore the original trigger (Manual/Schedule), and set `active` back to its pre-test state (deactivate if it was inactive). Deliverable ships with the trigger the user expects.
6. **Note honest limits**: if a step needs user secrets (Telegram chatId, API creds) that were never provided, run the chain as far as possible, verify everything upstream, and say exactly what remains and what the user must provide — do NOT claim full E2E green.

## Phase 4 — Delivery Report (evidence table)

Deliver a compact table; never prose-only claims:

```
| REQ | Requirement (user's words) | Evidence | Status |
|-----|---------------------------|----------|--------|
| 1   | <command>                 | execution <id>, node X output N items | PASS |
| 2   | <command>                 | <file/table/URL + count>            | PASS |
| ... |                           |                                          |      |
| AGR | <agreed result>           | table has 100 rows, verified via getRows | PASS |
```

Rules:
- `PASS` only with concrete evidence (execution ID, item counts, row counts, screenshots).
- `FAIL` → do NOT deliver. Fix, re-run Phase 3, re-report.
- `PARTIAL` → explain exactly what is missing and why (usually missing user secret), and what the user must do.
- Deliver in the user's language (Arabic if they write Arabic).

## Hard Rules

1. NO delivery of any n8n workflow without a Phase-3 execution run on the live instance.
2. Validation green ≠ done. 0-item executions are failures.
3. Never leave the test Webhook trigger in a delivered workflow, never leave it active when the user expects inactive, never destroy pinned data or credentials during tests.
4. If the workflow errors, fix → re-run → only then report. Never report "fixed" on the basis of a code change alone.
5. The requirements audit is against the USER's words, not your memory of intent — re-read their message.
