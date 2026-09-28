---
name: secret-scanning-lifecycle-adapter
description: "Secret-scanning lifecycle adapter (fast offline pre-commit gate + scheduled verified sweeps + regex boundary hardening). Use when adding secret scanning to pre-commit/CI, triaging a suspected leak, writing custom detectors, or hardening our own secret regexes. Trigger phrases: 'scan for secrets', 'gitleaks', 'trufflehog', 'leaked key', 'فحص الأسرار المسربة'."
---

# Secret Scanning Lifecycle Adapter (Fast Gate + Verified Sweeps)

Adapter over the industry-standard pairing (2026 consensus): **Gitleaks/
Betterleaks** (fast, offline, broad — blocks commits/PRs; note: Gitleaks
is feature-complete, its author continues in Betterleaks, same TOML
format) + **TruffleHog** (700+ detectors with LIVE verification —
confirms which credentials actually work). Baselines: upstream READMEs,
Rafter 2026 comparisons, arXiv boundary-mutation paper (Sep 2026).

## When to use

- New repo or skill: install the fast gate at the edge (pre-commit +
  CI step, SARIF output, blocking).
- Suspected leak or audit: run the verified sweep (history + states:
  verified = live danger, unverified = judgment call, unknown = retry).
- Custom credentials (project tokens, internal formats): custom regex
  detectors with keyword + webhook verification.
- Hardening OUR OWN scanner regexes (`security_gate.py`,
  `secret_redactor.py`): apply the boundary-mutation lesson below.

## Steps

1. Edge gate: Betterleaks/Gitleaks pre-commit hook + CI action; custom
   TOML rules for project-specific formats; `.gitleaksignore` only by
   fingerprint with a reason; fail the build on findings.
2. Scheduled sweeps: weekly TruffleHog full-history + filesystem/S3/
   chat-surface scans with `--only-verified` triage; rotate anything
   verified-live immediately (emergency path, not a ticket).
3. Custom detectors: regex + keyword + verification webhook (200 =
   verified); composite rules with proximity for multi-part secrets;
   decode/archive traversal on for packaged artifacts.
4. Boundary hardening (arXiv 2609 lesson — REAL bugs found in 2026):
   trailing `\b` after credential char classes FAILS when the secret
   ends in `-` (detection collapsed 0.9976 → 0.5233); Gitleaks'
   hard-coded terminator allowlist misses `f(AKIA…)` shapes. Fix: end
   credential patterns with negative lookahead `(?![A-Za-z0-9_])`
   instead of `\b`; re-run the battery after ANY regex fix (the paper's
   first plausible fix silently regressed two rules).
5. Keep evidence: SARIF in CI, verified findings in the audit trail with
   rotation records.

## Verification

- Pre-commit blocks a planted test secret; CI SARIF annotates the PR.
- A scheduled sweep report exists with verified/unverified split.
- Every regex change re-ran its test battery (no silent regressions).

## Pairs with

`credential-secret-handling`, `enterprise-security-gate`,
`build-gates-pipeline` (SECURITY stage), `n8n-credential-security-guard`.
