---
name: proactive-spec-expander
description: "Automatically expands simple user prompts into enterprise-grade PRDs with implicit security, lockdown modes, rate limits, and edge-case requirements BEFORE writing code. Use on every system design or implementation prompt. Trigger phrases: 'build a system', 'protect', 'harden', 'implement' — anything that implies production software."
---

# PROACTIVE SPECIFICATION EXPANDER SKILL

## DIRECTIVE
Never execute a user prompt as-is. Before drafting any architecture or code,
proactively infer and append non-functional, security, and failure-mode
requirements that the user didn't explicitly request.

## EXPANSION PROTOCOL (Pre-Execution Phase)

Whenever receiving a system design or implementation prompt, automatically
generate and append these 4 implicit layers:

1. **Security & Boundaries (Zero-Trust):**
   - Add Live Auth Verification & Secret Separation (e.g., operator secrets
     vs execution contexts — never share the HITL token as the override key).
   - Add SSRF Internal Egress Filtering (`127.0.0.1`, `10.x.x.x`, RFC1918
     blocks).
   - Add Unusable Single-Use Approval Tokens for sensitive actions (store only
     a SHA-256 hash, compare with `hmac.compare_digest`).

2. **Fault Tolerance & Resilience:**
   - Add Emergency Lockdown Mechanism (suspend high-risk actions while server
     keeps serving the last known GOOD state — do not empty the read path).
   - Add Auto-Rollback on Timeout & Failure Recovery.

3. **Rate Limiting & Anti-Abuse:**
   - Add Circuit Breakers & Sliding-Window Rate Limits.

4. **Audit & Traceability:**
   - Add Immutable Audit Store Logging with integrity checks (permission
     verification on every read, tampering detection).

## OUTPUT
Deliver a short expanded spec section listing exactly which implicit
requirements were appended, before the code. If the user's prompt already
covered an item, say "already requested" instead of duplicating it.

## Local adaptation
This project already implements every layer above in `feedback_loop.py`
(rotation gate), `auto_self_evolver.py` (lockdown read path), and the audit
SQLite store. Prefer reusing these exact patterns over inventing new ones so
new work stays consistent with the verified suite
(`venv/bin/python -m pytest`, 269 passing).