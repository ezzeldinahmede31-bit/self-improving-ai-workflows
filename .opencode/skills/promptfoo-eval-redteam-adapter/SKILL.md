---
name: promptfoo-eval-redteam-adapter
description: "Promptfoo LLM eval + red-team adapter (golden sets, pass-rate CI gates, OWASP redteaming, n8n runner, MCP security tests). Use when an LLM prompt/agent needs regression protection, a security red-team scan, a nightly eval inside n8n, or a CI quality gate with thresholds. Trigger phrases: 'eval this prompt', 'redteam scan', 'golden set', 'pass-rate gate', 'اختبر البرومبت'."
---

# Promptfoo Adapter (Evals + Red Teaming + n8n Runner)

Adapter over **promptfoo** (open source, `npx promptfoo`, Node 20+).
Two workflows: **eval** (does the prompt still behave?) and **redteam**
(is it exploitable?). Both run headless in CI AND from inside n8n.

## When to use

- Any prompt/agent change: frozen golden set (start ~20 rows) + three
  assertion styles (regex for format, contains for must-include,
  classifier/llm-rubric for semantics) + pass-rate threshold in CI.
- Security: `redteam generate/run` with harmful/PII/contracts plugins
  and jailbreak strategies; includes MCP security testing and OWASP LLM
  mappings for compliance reports.
- Nightly/CI LLM tests driven FROM n8n (Cron/Webhook → Execute Command
  → parse JSON → IF failures>0 → alert), or n8n gating downstream steps
  on pass rates.

## Steps

1. Write `promptfooconfig.yaml`: providers, prompts, tests with weighted
   assertions (weight must-not-fail checks ×2), `writeOutput` for CI
   parsing (JSON + JUnit + HTML).
2. Keep goldens small, frozen, representative; ownership + update
   protocol in a README (propose via PR with before/after runs).
3. Gate script: `promptfoo eval --no-cache -o output.json` with
   `PROMPTFOO_PASS_RATE_THRESHOLD` (default 100; small sets swing ≥3%
   per case — set honest thresholds), hard time cap, non-zero exit on
   failure; cache via `PROMPTFOO_CACHE_PATH`.
4. Red team on schedule: generate → run → review; strip response output
   (`STRIP_RESPONSE_OUTPUT`) and keep eval history for audit.
5. n8n runner (self-hosted only — Execute Command is unavailable on
   Cloud): bake the CLI into the image (not per-run install), mount
   prompts/config at a fixed path, wrap with `timeout`, route stderr to
   a log channel, fan out per model/config, alert on failure.
6. Test the AGENT contract, not just prose: `contains-json`/`is-json`
   for downstream payloads; assert real tool calls match schema.

## Verification

- Green gate locally before wiring into CI/n8n; failures show exact
  test IDs + share/report links.
- Provider keys live in CI secrets or the n8n credential store — never
  in the workflow, config, or logs.
- Red-team findings feed the security review; regressions block merge.

## Pairs with

`agent-readiness-verifier-adapter` (fixtures + scorecard),
`build-gates-pipeline` (binding verdict), `n8n-e2e-test-runner`,
`automation-known-issues-compass`.
