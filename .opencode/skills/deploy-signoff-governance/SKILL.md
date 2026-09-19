---
name: deploy-signoff-governance
description: "Run the final human sign-off ceremony for financial or sensitive deploys: authorization tiers (what needs a human, what never auto-approves), the evidence packet (gates verdict, execution proof, rollback plan), single-use token ceremony, and atomic rollback. Use when deploying anything that moves money, deletes data, touches production credentials, or publishes a workflow that agents will act on. Pairs with human-approval-gates, hitl-patterns-autonomous-workers, build-gates-pipeline, n8n-delivery-verification-gate, reversibility-engine."
---

# Deploy Sign-Off Governance

The last mile from "tests pass" to "a human owns this deploy".

## Sources (adopted baselines)

- "Runtime AI Governance" 2e (Bommena, Aug 2026): govern the ACTION before
  consequence — autonomy authorisation, human-on-the-loop supervision,
  reconstructable evidence, design vs operating effectiveness.
- "Agentic Governance" (Villalobos, 2026), Ch. 6 HITL: what humans are for,
  where to put the loop, anti-patterns; atomicity — without named units of
  work, traceability and rollback are theater.
- "AI Governance" (Bozdag/Bennati, Manning, 2026): six-level framework —
  policy, risk, design review, pre-launch test, live monitoring, incident
  learning.
- "Manage the Machine" (Goldman, Salesforce, 2026): which tasks delegate to AI
  vs where humans lead; guardrails that keep both from going astray.

## 1. Authorization tiers (decide BEFORE the deploy)

- Tier 0 auto: inactive/staging artifacts, docs, read-only probes. No human.
- Tier 1 human-notified: activate non-sensitive workflow; human informed with
  evidence link, silence = consent after the window.
- Tier 2 human-approves: anything moving money, deleting/writing prod data,
  touching credentials, publishing agent tool access. Silence = DENY
  (fail closed, 15-min default). No Tier 2 without the §2 packet — an approval
  without evidence is a rubber stamp.
- Tier 3 two-humans: irreversible or regulated blast radius. Never single-key.

## 2. Evidence packet (mandatory for Tier 2+)

1. Gates verdict: `build_gates_pipeline.py` → READY_FOR_DEPLOYMENT (exit 0),
   audit JSON path attached.
2. Execution proof: real run on staging/inactive item — inputs, outputs, per-node
   item totals; 0-item or collapsed-totals nodes named explicitly.
3. Blast-radius sheet: which workflows/credentials/data the deploy touches +
   who is affected if it misbehaves.
4. Rollback plan: named unit of work (workflow id + version), restore steps,
   who executes, time estimate. No named unit = no deploy (atomicity rule).
5. Expiry: approval is single-use, single-artifact. A changed artifact needs a
   new packet, never a reused "yes".

## 3. Ceremony (how the approval happens)

- Single-use token, hash-stored, `hmac.compare_digest` verify; forged attempts
  logged (this workspace: `hitl_gate.py` + `feedback_loop.py` rotation gate —
  3 tries/hour then LOCKDOWN, 15-min pending timeout auto-DENY).
- Operator secret and approval token are SEPARATE secrets, separate files,
  0600, no symlinks. A HITL token is never an override secret.
- Approval, decision, evidence paths, and rollback plan land in ONE audit row
  (SQLite + `memory/audits/<ts>.json`). If it is not in the audit row, it did
  not happen.

## 4. Anti-patterns (refuse the deploy)

- Rubber-stamp loops: human approves 50 identical packets a day → move the
  category down a tier or fix the noise, never normalize blind yes.
- Approval after the fact ("deploy now, sign later").
- Shared approver identity; screenshot-as-evidence; verbal "go ahead".
- Destructive chains without per-step approval binding (chained
  destructive/duplicate-write detection lives in `security_gate.py`).

## Verification

After deploy: monitor the first live executions against the packet's expected
outputs; any deviation → execute the §2 rollback, file the incident, and the
next packet for that category gets stricter evidence. Governance that never
rolls back is decoration.
