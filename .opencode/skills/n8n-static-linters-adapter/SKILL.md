---
name: n8n-static-linters-adapter
description: "Zero-dependency n8n static linters adapter (secret/credential lint, 24 production-debug rules, ruff-like syntax checks). Use when linting an n8n workflow JSON for leaked credentials, missing retries/timeouts, bad IF operators, silent Postgres/SplitInBatches failures, or LLM-generated structural mistakes. Trigger phrases: 'lint this workflow', 'n8n-lint', 'valn8n', 'pre-deploy check', 'افحص الورك فلو قبل النشر'."
---

# Static Linters Adapter (n8n Pre-Deploy Checks)

One adapter over three MIT/zero-dependency upstream linters (grounded from
`/tmp/opencode/upstream/` clones). They catch what security scanners miss:
**silent correctness failures** — workflows that run green but do the wrong
thing (skipped downstream nodes, notification spam loops, swallowed errors).

## When to use

- After generating or editing any n8n workflow JSON, BEFORE the gates
  pipeline: lint first (cheap), gate second (binding).
- When a workflow was LLM-generated (valn8n exists precisely for
  LLM-generated structural mistakes).
- When CI needs a no-install check (Redsf linter and the RW2023 validator
  run on the Python standard library only).

## The three tools (all MIT, all safe to run)

1. **Redsf/n8n-workflow-linter** — `n8n-lint workflows/` (install from git;
   zero runtime deps). Rules: real credential IDs, hardcoded secrets,
   credentials in URLs, missing retry/timeout on HTTP nodes, swallowed error
   outputs, pinned test data, unauthenticated webhooks, polling cost.
   `--strict` fails on warnings; `--explain` gives UI click-steps;
   `--list-rules` enumerates; `--format github` annotates PRs.
2. **RW2023/n8n-workflow-validator** — single file `n8n_validator.py`, 24
   rules from real production debugging. FAIL-level: Postgres INSERT without
   RETURNING, HTTP-in-Code sandbox blocks, invalid node references,
   hardcoded secrets, stringify-in-webhook-response, bad Anthropic params.
   WARN-level: unreliable IF operators, mark-after-send spam pattern,
   SplitInBatches wiring, Telegram-via-HTTP. Exit 0 clean / 1 FAIL / 2 WARN.
3. **DrMicrobit/valn8n** — ruff-style validator, LLM-autocorrect friendly
   (`--fmt text` for agents, JSON/CSV for dashboards). Rule groups ND01–ND08:
   filters, node structure, params, expressions, credentials, connections,
   error handling, naming/docs. `--strict-only` runs structural rules only;
   `--select/--ignore` scope by group. Needs Python 3.13+ via `uv`.

## Steps

1. Pick the cheapest tool that covers the suspicion:
   secrets/CI → Redsf; silent runtime bugs → RW2023; LLM-generated mess →
   valn8n. Running all three is fine (seconds, no services).
2. Run against the exported JSON, keep the raw output as evidence.
3. Fix findings in this order: errors/FAILs (blockers) → warnings that match
   the `automation-known-issues-compass` catalog → hints/naming.
4. Re-run until the strict mode is clean (`--strict` / `--strict-only`).
5. Proceed to `build_gates_pipeline.py` (binding verdict) and the delivery
   verification gate (live execution proof).

## Verification

- All three tools exit clean on the final artifact (or residual warnings are
  logged with a reason in the delivery notes).
- Findings + fixes recorded in the delivery evidence table
  (REQ → evidence → PASS/FAIL).

## Pairs with

`automation-known-issues-compass` (fix recipes), `build-gates-pipeline`
(binding verdict), `n8n-delivery-verification-gate` (live proof),
`n8n-schema-guardrail`.
