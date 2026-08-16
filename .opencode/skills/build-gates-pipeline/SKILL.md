---
name: build-gates-pipeline
description: "MANDATORY pre-build gate pipeline for EVERY n8n workflow, AI agent, or automation artifact this agent produces. Any artifact (workflow JSON, agent design, script, annotated answer) MUST pass the 7-stage pipeline (SECURITY -> QUALITY -> INTEGRITY -> MATH -> REASONING -> HITL -> AUDIT) with verdict READY_FOR_DEPLOYMENT before it is created/deployed on n8n or delivered. Runs the user's own Python gates (security_gate.py, quality_gate.py, chain_integrity_checker.py, hitl_gate.py) plus the new MATH (math-verify/z3/self-consistency vote) and REASONING (counting/boundary detection) gates. Use BEFORE creating/updating ANY n8n workflow, before delivering any workflow/agent, and whenever the user says 'شغل البوابات', 'عدي على البوابات', 'gates first', 'verify before deploy'. Pairs with: verifier_engine.py, n8n-delivery-verification-gate, n8n-schema-guardrail, automation-known-issues-compass."
---

# Build Gates Pipeline — MANDATORY before every build

Every artifact this agent produces (n8n workflow JSON, AI agent design, script,
annotated math/logic answer) MUST pass the project's own gate pipeline before
it is deployed or delivered. This is the user's standing rule: same stages,
same quality as the Python system (`/home/ezzeldin/Documents/Default Project`).

## The command

```bash
venv/bin/python scripts/build_gates_pipeline.py <artifact> [--no-hitl] [--json]
```

- Exit code **0** = `READY_FOR_DEPLOYMENT` — only then create/deploy on n8n.
- Exit code **1** = violation or pending human review — fix and re-run.
- `--no-hitl` = autonomous mode (no human approval; security risks still
  hard-reject). `--json` = machine-readable report.

## The 7 stages (fixed order, same as the Python system)

1. **SECURITY** — `SecurityGate`: hardcoded secrets (OWASP LLM06), SSRF /
   cloud-metadata egress (always fatal), banned code execution
   (subprocess/eval/exec/child_process — always fatal), privileged containers,
   promoted auto-rules. Risk >= 40 = fatal.
2. **QUALITY** — `QualityGate`: Schema V2 expression syntax (bare `$json`,
   `$node[]`, moment.js banned), graph integrity, reliability (Error Trigger /
   continueOnFail / pinned data), size (<= 10 nodes), cyclomatic complexity.
   Score >= 80 required.
3. **INTEGRITY** — deterministic DAG closure over connections: unknown node
   targets, orphans, duplicate ids, self-deps, cycles (Kahn). Structural
   violations are a hard stop — never overridable.
4. **MATH** — `MathLogicGate` (new): math-verify answer equivalence
   (`_gates.math`), Z3 SAT/UNSAT (`_gates.z3`), self-consistency majority vote
   (`_gates.vote`), expected-text parity. Verdicts: PASS / FAIL /
   NEEDS_REVIEW / SKIP.
5. **REASONING** — `DeepReasoningGate` (new): counting/boundary detection
   (off-by-one class, fence-post, open/closed intervals). A counting problem
   WITHOUT independent verification escalates to human review instead of
   shipping a guess.
6. **HITL** — `HITLGate`: security rejection or reasoning flag freezes as
   PENDING_APPROVAL in `audit.db` (15-min timeout, default DENY →
   EXPIRED_REJECTED). Approve: `--approve <request_id> <token>`; reject:
   `--reject <request_id> <reason>`.
7. **AUDIT** — every run writes `audit_log_entry` + a full JSON report to
   `memory/audits/<timestamp>.json`.

## Annotating an artifact (`_gates` section)

Attach a `_gates` object to any JSON artifact to trigger the math/logic gates:

```json
{
  "name": "...",
  "nodes": [...],
  "connections": {...},
  "_gates": {
    "math": {"answer": "149", "expected": "149"},
    "z3": {"vars": {"x": 1, "y": 1},
           "assertions": ["x + y == 10", "x - y == 4"]},
    "counting": {"answer": 149, "expected": 149},
    "vote": {"candidates": [{"answer": "149"}, {"answer": "149"}, {"answer": "150"}]},
    "expected_result": "some text that must appear"
  }
}
```

For math/logic-heavy answers produced outside JSON, write the artifact to a
temp JSON file with the `_gates` block and run the pipeline.

## Workflow integration (how the agent uses it)

1. After designing/building ANY workflow JSON or agent design (local file or
   draft), run the pipeline BEFORE `n8n_create_workflow` / update / deploy.
2. If verdict != READY_FOR_DEPLOYMENT: read the per-stage violations, fix the
   artifact (the violations ARE the feedback — same as VerifierEngine's
   retry loop), re-run until 0 or escalate to human review.
3. If PENDING_HUMAN_REVIEW: surface the request_id + violations to the user;
   continue only after `--approve` returns OVERRIDE_APPROVED.
4. The EU Brands workflow currently FAILS quality (15/100: bare `$json` in
   Code nodes, non-verb node names, >10 nodes, no Error Trigger, no pinned
   data) — use its violation list as the reference example of what a real
   fix pass looks like.

## Evidence & honesty rules

- Never report "passed gates" without the exit code 0 + `--json` output.
- Never auto-fix a SECURITY rejection — it routes to the human by design.
- A counting answer without independent verification is NEEDS_REVIEW, not PASS.
- Tests: `venv/bin/python -m pytest tests/test_build_gates_pipeline.py -q`
  (25 tests — security/quality/DAG/math/reasoning/HITL/audit).
