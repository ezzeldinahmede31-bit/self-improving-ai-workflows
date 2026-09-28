---
name: n8n-flowguard-adapter
description: "Graph-based n8n security scanner adapter (OWASP Agentic Top 10, SARIF output, CI fail-on-severity). Use when scanning an n8n workflow JSON for trigger-to-code escalation, hardcoded credentials, unauthenticated webhooks, AI tool overreach, or when a SARIF report is needed for CI. Trigger phrases: 'scan this workflow', 'flowguard', 'SARIF scan', 'OWASP n8n audit', 'افحص الورك فلو أمنياً'."
---

# FlowGuard Adapter (n8n Security Scanner)

Adapter over the upstream open-source scanner **MohibShaikh/FlowGuard**
(`n8n-flowguard` on npm, 111 tests passing). Purpose-built for n8n's
node-and-connection model: it follows trigger paths through the graph and
flags flows that reach sensitive sinks without validation.

## When to use

- Before delivering ANY n8n workflow: run this scan, then feed findings into
  `security_gate.py` / `build_gates_pipeline.py` (local gates stay
  authoritative; FlowGuard is corroborating evidence).
- When the task mentions SARIF, CI gating, or OWASP coverage for n8n.
- When a workflow came from the web / a template and needs a trust verdict.

## License boundary (hard rule)

Upstream is **AGPL-3.0-only**. NEVER vendor its source into this repo.
Use it only as an **external CLI** (`npx` or global install). No file from
`/tmp/opencode/upstream/FlowGuard` may be copied here.

## Steps

1. Obtain the scanner without vendoring:
   `npm install -g n8n-flowguard` (or run once via `npx n8n-flowguard`).
2. Scan the exported workflow file:
   `flowguard scan workflow.json` — single file.
   `flowguard scan ./workflows/` — directory.
3. For a live instance (only with the owner's explicit approval, read-only):
   `flowguard scan ./workflows/ --url <N8N_URL> --api-key <N8N_API_KEY>`
   (placeholders only — never paste a real key into chat; pass via env).
4. Machine-readable output for CI: request SARIF
   (`flowguard scan workflow.json --sarif`) or JSON (`--json`); gate merges
   with `--fail-on high` so critical/high findings block the pipeline.
5. Map each finding to the local model:
   - Unrestricted Code Execution / Missing Input Validation → local
     SecurityGate risk family (webhook-to-code without IF/Switch/Filter).
   - Insecure Credential Usage → hardcoded-secret family (must move to the
     n8n credential store, never node parameters).
   - Unauthenticated Webhook → webhook-auth family.
   - AI Agent Tool Access → agent tool-scope family.
6. Fix at the graph level (add IF/Switch validation, credential refs, webhook
   auth), re-scan until clean, then run the local gates pipeline.

## Detection families covered

Excessive Agency, Unrestricted Code Execution, Missing Input Validation,
Unsafe Output Handling, Insecure Credential Usage, Excessive Data Exposure,
Unauthenticated Webhook, Sub-Workflow Escalation, AI Agent Tool Access —
each mapped to the OWASP Top 10 for Agentic Applications.

## Verification

- Re-run `flowguard scan workflow.json --fail-on high` → exit code 0.
- Keep the SARIF file next to the delivery as evidence
  (`memory/audits/<ts>-flowguard.sarif`).
- Local `build_gates_pipeline.py` SECURITY stage still passes (it is the
  binding verdict; a FlowGuard pass never overrides a local rejection).

## Pairs with

`automation-known-issues-compass` (pre-flight), `build-gates-pipeline`
(binding verdict), `n8n-credential-security-guard`, `n8n-delivery-verification-gate`.
