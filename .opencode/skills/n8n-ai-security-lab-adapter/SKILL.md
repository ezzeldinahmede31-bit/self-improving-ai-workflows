---
name: n8n-ai-security-lab-adapter
description: "n8n AI-workflow security regression adapter (static audit score, isolated staging gate, fingerprint-bound receipts, dependency-free PR gate). Use when an AI-agent workflow needs a security score, a staging behavior contract, a baseline-vs-candidate change review, or a GitHub PR check that never executes workflows. Trigger phrases: 'security regression gate', 'staging receipt', 'change review', 'PR gate n8n', 'راجع أمان وكيل الذكاء'."
---

# AI Security Lab Adapter (Audit + Staging Gate + PR Gate)

Adapter over upstream **0xCD4/n8n-ai-agent-security-lab** (Node 20 ESM,
MIT). It adds three things this workspace does not have: (a) a numeric
**static audit score** for AI workflows, (b) a **staging regression gate**
that replays sanitized fixtures against an isolated target, (c) a
**change-review + PR gate** whose receipts are bound by workflow
fingerprint — a mismatched receipt can never approve a candidate.

## When to use

- Any AI-agent n8n workflow before production: audit → stage → review.
- Baseline-vs-candidate comparison (what risk was added/removed, new
  outbound domains, credential-type changes).
- GitHub PRs carrying workflow JSON: run the dependency-free PR gate
  (no credentials, no AI service, no n8n instance, no code execution —
  it only scans and writes redacted SARIF/JSON/Markdown evidence).
- Multi-workflow estates: build the trust-boundary map (credential reuse
  across workflows, unresolved sub-workflow targets) with raw secret values
  always redacted.

## Safety boundaries (inherited from upstream, non-negotiable)

- Never activate the intentionally-unsafe teaching fixture; never attach
  production credentials to any test fixture.
- Dynamic checks run ONLY against an isolated staging target the operator
  owns or is authorized to test; remote targets stay blocked unless the
  operator allow-lists exact host + path prefixes.
- A passing report is review evidence, not a penetration test, compliance
  result, or safety certificate. The local HITL decision stays binding.

## Steps

1. Static audit: `node bin/audit.mjs <workflow> [report]` → score + risky
   paths (untrusted-lane → credentialed-action without an approval step is
   the headline finding) + exposure graph (JSON/Mermaid/SVG).
2. Stage gate: run `node bin/gate.mjs` against the isolated staging target
   with the provided security contract (auth, signature, field shape,
   injection-marker-behind-approval, replay idempotency, method allow-list).
3. Change review: combine baseline scan + candidate scan + the staging
   receipt whose recorded candidate fingerprint matches the export under
   review; record added/removed risk and limits still needing a human.
4. Local rehearsal (optional, credential-free): contained throwaway
   environments record observed action differences without touching real
   destinations.
5. PR gate: `pr-gate.mjs` on the changed files; upload SARIF + redacted
   summary as CI artifacts.
6. Archive the score, receipt, and review record in `audit.db` / delivery
   notes, then continue to HITL (human approves the literal parameters,
   never a paraphrase) and the delivery verification gate.

## Verification

- Audit score recorded; staging receipt fingerprint matches the candidate
  export (mismatch = cannot approve, no exceptions).
- PR gate artifacts (SARIF + summary) attached to the delivery.
- HITL approval references the exact tool parameters, not a summary.

## Pairs with

`human-approval-gates` (literal-parameter review), `build-gates-pipeline`
(binding verdict), `n8n-delivery-verification-gate` (live proof),
`automation-known-issues-compass` (triage).
