---
name: frontier-red-team-auditor
description: "Enforces mandatory Frontier LLM reasoning for security audits while backing it up with deterministic input validation and isolated Docker sandboxing. Security analysis MUST NEVER rely on low-tier or lightweight models. Use when auditing a workflow/code for vulnerabilities, reviewing SSRF/exfiltration/exec vectors, threat-modeling against OWASP LLM Top 10, or whenever a generated artifact must pass a security review before deploy. Trigger phrases: 'red team', 'audit for security', 'is this safe', 'SSRF check', 'security review', 'threat model', 'vulnerability scan'."
---

# FRONTIER RED-TEAM & DEFENSE-IN-DEPTH AUDITOR

## DIRECTIVE

Security analysis MUST NEVER rely on low-tier or lightweight models. All
vulnerability assessments, threat modeling, and payload analysis must be
executed strictly by Tier-3 Frontier Models combined with strict deterministic
validation. A weak model cannot be trusted to notice the attack it was not
trained to see.

## DUAL-LAYER SECURITY PIPELINE

```
          [Generated Workflow / Code]
                       │
                       ▼
 ┌──────────────────────────────────────────────────────┐
 │ Layer 1: Deterministic Perimeter (Local Mint)          │
 │  - Regex Entropy Scanner (auto-detect API keys/tokens) │
 │  - Static AST Parser (block exec/eval/rm/subprocess)    │
 └──────────────────────────────────────────────────────┘
                       │
                       ▼
 ┌──────────────────────────────────────────────────────┐
 │ Layer 2: Frontier Red-Team Agent (Claude Opus)        │
 │  - Logic-flaw detection & SSRF vector audit            │
 │  - OWASP LLM Top 10 threat modeling                    │
 └──────────────────────────────────────────────────────┘
                       │
                       ▼
 ┌──────────────────────────────────────────────────────┐
 │ Layer 3: Isolated Execution Sandbox                    │
 │  - Ephemeral Docker run (--net=none, --read-only)      │
 └──────────────────────────────────────────────────────┘
```

## MANDATORY AUDIT CHECKLIST

1. **SSRF Audit:** Block any HTTP node addressing `127.0.0.1`, `localhost`, or
   private subnets (`10.x`, `172.16-31.x`, `192.168.x.x`). Allowlist is safer.
2. **Secret-Exfiltration Check:** Reject payloads where raw API tokens
   (`sk-...`) are hardcoded string literals. Tokens belong in the secret store,
   never in the workflow JSON or code.
3. **Execution Constraint:** If the frontier red-team flags risk score >= 40,
   trigger the HITL Gate INSTANTLY (default-deny on timeout). Frontier doubts
   are never overridden by a weaker stage.

## SEQUENCING RULES

- Layer 1 (deterministic) runs FIRST and can hard-reject without the model —
  `exec/eval/rm` or leaked `sk-` is a stop, not a prompt for a second opinion.
- Layer 2 (frontier) is *mandatory* for: any node with a network egress,
  code-node JS/Python, auth handling, or payment/stripe surfaces. Skip it only
  for provably static JSON with zero code and zero egress.
- Layer 3 (sandbox) runs any code-node payload with `--net=none` (network
  disabled), read-only filesystem, no host mounts, and a hard CPU/mem budget.

## INTEGRATION

Replaces the weak-model red-team assumption:
`cybersec_sandbox_engine.CyberSecRedTeamAgent` runs the deterministic
perimeter + sandbox schedule; the frontier verdict is provided through this
skill's Tier-3 call. HITL escalation goes through `hitl_gate.HITLGate`.