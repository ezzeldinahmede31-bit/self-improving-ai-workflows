---
name: enterprise-security-gate
description: "Autonomous Zero-Trust security enforcer complying with OWASP Top 10 for LLMs, NIST AI RMF, and SOC 2 Type II controls. Use whenever generating or reviewing any workflow JSON, script, or configuration before it is created or deployed."
---

# ENTERPRISE ZERO-TRUST SECURITY GATE

## DIRECTIVE
Security and privacy take absolute priority over speed and brevity. Inspect
every workflow, script, and configuration against strict Zero-Trust policies.
This gate runs BEFORE any create/deploy happens, programmatically or by review.

## SECURITY CHECKS & BANNED PATTERNS

1. **AST STATIC CODE ANALYSIS:**
   - **Banned Python Modules/Calls:** `os`, `subprocess`, `sys`, `shutil`,
     `socket`, `eval()`, `exec()`, `unlink()`, `rmtree()`.
   - **Banned JS Modules/Calls:** `child_process`, `fs` (direct system writes),
     `eval()`.
   - These are not automatically fatal: any legitimate use MUST be justified and
     flagged for human review before execution.

2. **HARDCODED SECRETS DENIAL (OWASP LLM06):**
   - Zero tolerance for hardcoded API keys (`sk-*`, `ghp_*`, `AIzaSy*`, JWTs,
     Basic Auth strings, DB URLs with credentials).
   - Scan EVERY key of every JSON node — including `pinnedData`, mock payloads,
     and Code-node source. Flag any node containing plaintext credentials
     immediately.
   - Correct pattern: reference existing credential ids only, or use
     `$env.VARIABLE` placeholders.

3. **NETWORK & EGRESS PROTECTION:**
   - Block unvetted calls to cloud metadata endpoints (`169.254.169.254`,
     AWS IMDS `169.254.170.2`, GCP metadata `metadata.google.internal`).
   - Validate local network targets (`127.0.0.1`, `localhost`) in webhook/HTTP
     nodes to ensure no Server-Side Request Forgery (SSRF) vulnerabilities exist.
   - Flag any URL built with untrusted user input (open redirect / SSRF risk).

4. **RISK SCORING MATRIX:**
   - Assign a risk score (0 to 100) for every artifact. Scoring inputs:
     - +35  hardcoded secret
     - +25  banned module / eval / exec
     - +20  SSRF-able URL or metadata endpoint
     - +15  privileged/root container config, insecure volume mount
     - +10  missing error handling on write paths
     - +5   missing human-review note on a mutated system
   - **If Risk Score >= 40:** Trigger `REJECTED_SECURITY_RISK`, halt deployment,
     and route execution to `PENDING_HUMAN_REVIEW` with an audit log entry
     (classification, risk score, offending node, reason).

## INTERFACE WITH THE AUDIT DB
- On any REJECT: record severity, node name, risk score, timestamp, and
  offending pattern in the governance audit log (SQLite) — hash the raw input,
  never store secrets.
- On APPROVE: record approval with score so the decision is replayable later.

## OUTPUT CONTRACT
Report per artifact:
- Risk score (0-100).
- Findings list: pattern flagged + node + severity.
- Decision: APPROVE / REJECTED_SECURITY_RISK / PENDING_HUMAN_REVIEW.