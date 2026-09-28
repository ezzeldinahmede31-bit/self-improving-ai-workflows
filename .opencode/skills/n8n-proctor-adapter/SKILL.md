---
name: n8n-proctor-adapter
description: "Change-targeted n8n validation adapter with trust ledger (validate only the diff, MCP tools, execution only when warranted). Use when iterating on a large n8n workflow, when re-validating the whole graph wastes tokens, or when a guardrail verdict is needed before pushing to n8n. Trigger phrases: 'validate only changes', 'n8n-proctor', 'trust status', 'should I push this', 'راجع التعديل بس'."
---

# n8n-proctor Adapter (Targeted Validation + Trust)

Adapter over upstream **Rakurai/n8n-proctor** (TypeScript, MIT, Node 20+;
MCP server + CLI). Core idea this repo lacks: **validate the change, not
the workflow** — a persistent trust ledger remembers already-validated
regions, so each edit re-checks only the diff plus forward propagation.

## When to use

- Iterative workflow development: after every edit, before any push.
- Large graphs where full re-validation is expensive.
- As the pre-push gate in front of `n8n-mcp-workflow-builder` flows.
- When the agent is unsure whether live execution is needed (proctor
  decides: static first, execution only when runtime evidence is required).

## External dependency (never vendored)

Upstream runs as an MCP server plus CLI (`n8n-proctor validate/test/trust/
explain`). It needs a live n8n instance only for the `test` (execution)
tool; `validate` is fully local. Wire it as an MCP server entry (same
pattern as the existing n8n MCP entry) or invoke the CLI per change.
Runtime peers it expects: the n8n MCP server and n8n-as-code push tooling —
both already in this workspace's stack.

## Steps

1. `trust_status` first: see what is trusted, what changed, what still needs
   validation. Identical reruns and over-broad targets are refused by
   guardrails — narrow the target instead of retrying.
2. `validate` (static, always): expression tracing, data-loss detection,
   disconnected-node detection on the change slice. Fix diagnostics, keep
   the compact JSON as evidence (token-cheap by design).
3. `explain` when a guardrail blocks: preview what validate/test would
   decide before spending an execution.
4. `test` (execution) only when static analysis says runtime evidence is
   needed; coordinate push-then-test through the existing n8n MCP tooling.
5. Trust updates automatically after green runs; the next edit starts from
   the new baseline.
6. Feed the diagnostic JSON into `audit.db` / delivery notes as validation
   evidence, then continue to the local gates pipeline.

## Verification

- `validate` returns no errors on the change slice.
- `trust_status` shows the edited region trusted after the green run.
- No `test` execution was spent when static analysis sufficed (cost
  discipline: execution is the exception, not the default).

## Pairs with

`n8n-mcp-workflow-builder` (push path), `incremental-generation`
(one-node-at-a-time builds), `build-gates-pipeline` (binding verdict),
`n8n-delivery-verification-gate` (final live proof).
