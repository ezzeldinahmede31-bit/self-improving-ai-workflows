---
name: world-class-design-review
description: "Grade any n8n workflow 0-100 against the world-class scorecard: input contracts, idempotency, error handling, security, observability, cost control, maintainability, docs — benchmarked against the best public repos (studiomeyer hardened patterns, enterprise contract-first templates). Use when reviewing a workflow before production, comparing two designs, or tracking design quality over time. Pairs with eip-workflow-patterns, build-gates-pipeline, n8n-delivery-verification-gate, stability-patterns-production."
---

# World-Class Design Review

"Best designer" is a scoreboard, not a title. Grade every graph.

## Sources (adopted baselines)

- studiomeyer-io/n8n-workflows (audited Apr 2026): the gap in most public
  templates = no HMAC, no idempotency, no rate limit, silent LLM errors,
  duplicate writes on retry. Their fix: 4 opt-in nodes (Verify, Rate Limit,
  Idempotency, always-on Error Branch), env-gated, default-off for clean
  import; CI blocking credential leaks and malformed refs.
- zarif3624/n8n-enterprise-workflows: contract-first packages — typed input
  contract, low/high-risk + invalid fixtures, explainable scoring with stable
  rule ids, inactive-by-default import, observable outcomes (request id, score,
  reasons, decision), promotion discipline, ROI metric per workflow.
- kspandian32 Enterprise-n8n-Architectures: layered stack, global SAFE_MODE,
  centralized log-drain observability, queue-mode deployment.
- EIP vocabulary for naming shapes (see eip-workflow-patterns).

## Scorecard (100 total, read-only JSON analysis)

- Input contracts (15): typed expected shape, field validation at ingress,
  invalid-input fixtures produce clean 4xx. No contract = 0 here.
- Idempotency (15): dedup key + duplicate short-circuit before side effects;
  provider retries cannot double-write.
- Error handling (15): every external call has an error branch or
  continue-strategy + error workflow; failures are loud with reason + payload.
- Security (15): webhook auth/HMAC where public, credentials only via n8n
  credential store, zero inline secrets, least-privilege scopes.
- Observability (10): request/correlation ids, decision reasons logged,
  execution history readable, alert on drift not just death.
- Cost/rate control (10): LLM/API calls bounded, rate limits, route-early
  discard before expensive nodes, batching where volume lives.
- Maintainability (10): named EIP shapes, one router location, sub-workflow
  split past ~20 nodes, no orphan/dead nodes, sticky-note topology.
- Docs (10): purpose, inputs, fixtures, runbook, owner, rollback pointer.

## Grades

90+ world-class (ships anywhere) · 75+ production-ready · 60+ shippable with
named findings · below 60 rework before any activation. A green gates verdict
is necessary, never sufficient — gates check shape, this checks judgment.

## Procedure

1. Export JSON (read-only), enumerate nodes/edges/credentials-triggers.
2. Score each dimension with the single strongest evidence line.
3. List findings ordered by blast radius, each with pattern + fix pointer.
4. Record the score + date in the design ledger for trend tracking.

## Verification

Re-review after fixes; score must rise on the SAME rubric. Two reviewers
(human + this skill) disagreeing by 10+ points = rubric discussion, not
averaging. Ledger lives beside audits for trend proof.
