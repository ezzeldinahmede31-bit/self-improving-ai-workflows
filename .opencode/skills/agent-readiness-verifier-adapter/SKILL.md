---
name: agent-readiness-verifier-adapter
description: "Agent readiness and claim-verification adapter (production scorecard, prompt-injection fixtures, refute-by-default done-verifier). Use when an agent must prove it is shippable, when 'done' claims need independent refutation, or when spec-gated waves with per-wave audits are required. Trigger phrases: 'readiness score', 'refute this done claim', 'injection fixtures', 'verify completion', 'هل الوكيل جاهز للإطلاق'."
---

# Readiness + Verifier Adapter (Scorecard + Refute-by-Default)

One adapter over two complementary upstreams (both MIT, both grounded
from `/tmp/opencode/upstream/` clones):

- **lindixu6-hash/awesome-agentic-engineering** — executable production
  readiness: Agent Card (does / must-never-do / safe-failure), 10-area
  scorecard, risk-tiered profiles (read-only, draft-only, state-changing),
  8 prompt-injection fixtures (direct, indirect, exfiltration + benign
  controls) run through real adapters with trusted/untrusted channel
  separation, attested evidence (SHA-pinned, replay-rejecting), launch
  checklist, failure-modes regression library, MCP safety checklist.
- **joymin5655/Agent** — refute-by-default harness: `/spec → spec-gate`
  (no approved plan, no substantive edits) → supervised waves (every wave
  audited, FAIL = STOP, no auto-retry) → `/verify-completion` (mechanical
  checks + a fresh-context judge whose default verdict is REFUTED — low
  confidence and judge crashes both mean REFUTED) → secret/risk gates →
  commit. Tool-boundary guards enforce allow/ask/deny; every gate records
  the model weakness it assumes plus a review date (dead/stale gates are
  retired, not worshipped).

## When to use

- Before ANY agent ships to real users: scorecard first, fixtures second,
  launch checklist last. The first `agentic-init` run deliberately scores
  0/20 — fill TODOs and evidence honestly instead of gaming the score.
- After ANY agent claims completion: route the claim through the
  refute-by-default verifier (mechanical checks + fresh-context judge)
  before a human ever sees it.
- When a spec exists: enforce the spec gate so implementation cannot start
  (or drift) without an approved plan.

## Steps

1. Init: generate the Agent Card + eval plan + launch checklist from
   templates; choose the risk profile matching the agent's blast radius
   (read-only < draft-only < state-changing).
2. Score honestly across the 10 areas (goal clarity, tool permissions,
   memory, evals, failure handling, security, observability, cost, human
   review, docs). Anything un-evidenced scores 0.
3. Run the 8 injection fixtures through the agent's real path with
   trusted/untrusted separation; record observed actions, violations, and
   traces in the eval-result contract.
4. Convert every failure mode and production incident into a regression
   case (failure-modes library) so the same breakage cannot recur
   silently.
5. For the build itself: spec-gate → wave dispatch with per-wave audit →
   refute-by-default completion check → secret scan → wrap. A REFUTED
   claim returns to work with the judge's counter-evidence attached.
6. Archive the scorecard, fixture results, and verifier verdict in
   `audit.db` / delivery notes as the "why this was allowed to run"
   evidence; unresolved launch blockers stay visible (never hidden behind
   a passing sub-score).

## Verification

- Scorecard + fixture results attached; blockers listed or empty.
- Every "done" survived a fresh-context refutation attempt (verdict +
   trace kept).
- The CI gate shape (`min-score`, `fail-on-blockers`) is recorded so the
  next change re-proves readiness.

## Pairs with

`agent-control-plane-adapter` (runtime policy), `human-approval-gates`
(risky-action review), `test-driven-development` (mechanical checks),
`build-gates-pipeline` (binding verdict).
