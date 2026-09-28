---
name: agent-runtime-guard-adapter
description: "Inline runtime firewall adapter for agent tool calls (sub-millisecond policy checks, MCP tool scanner, deny-by-default). Use when every tool call, file write, or inter-agent message must pass a policy verdict at the boundary, when MCP tools need poison/typosquat screening, or when a kill switch and tamper-evident trail are required. Trigger phrases: 'guard every tool call', 'MCP scanner', 'deny by default', 'runtime firewall', 'جدار الحماية وقت التشغيل'."
---

# Runtime Guard Adapter (Inline Tool-Call Firewall)

Adapter over upstream **Aveerayy/agent-guard** (`pip install agent-guard`,
Python 3.9+, MIT). It answers a different question than HITL: not "should
a human approve this?" but "is this call allowed at all?" — in under a
tenth of a millisecond, at the tool boundary, for every call.

## When to use

- Wrap any agent framework's tool loop (LangChain/CrewAI/AutoGen-style or
  the repo's own orchestrator tool calls) with a deny-by-default policy.
- Before adopting ANY third-party MCP server: run the MCP security scan
  (poisoned descriptions, hidden instructions, typosquatted names, hidden
  unicode, schema abuse, cross-server collisions, privilege overreach,
  embedded secrets).
- Outputs leaving the agent (messages, files, logs) need PII/secret
  filtering: emails, phones, national IDs, cards (Luhn-checked), internal
  IPs, cloud/API tokens, private keys, connection strings.

## Steps

1. Install the package (`pip install agent-guard`, plus the extra matching
   the framework in use). No vendor copy; the PyPI release is the source.
2. Write policy as YAML or fluent Python: default-deny, per-agent rules,
   wildcards, conditionals, priority ordering. Start from a built-in
   template matching the domain (standard, research, development,
   financial, HIPAA-style) and tighten.
3. Wrap the loop: every tool call, file write, and inter-agent message goes
   through `Guard.check()` FIRST — allow / deny / require-confirmation.
   Denials happen at the boundary; only confirmations escalate toward HITL.
4. Scan MCP tool definitions at registration time; re-scan on server
   version change. Quarantine anything flagged; never auto-allow on scan
   failure (fail closed).
5. Filter all outbound text through the PII/secrets filter with custom
   patterns for project-specific identifiers.
6. Keep the tamper-evident decision log (hash-chained) and export the
   governance attestation next to the delivery; mirror verdicts into the
   local `audit.db` (single-trail rule — see control-plane adapter).

## Verification

- A forbidden call is denied with zero side effects and a log entry.
- The MCP scan runs green on every adopted server (report kept).
- The OWASP Agentic Top 10 attestation (`verify()`) is exported per
  release; any gap is named, not hidden.

## Pairs with

`agent-control-plane-adapter` (policy/budget/kill-switch),
`human-approval-gates` (human checkpoint for confirmations),
`credential-secret-handling`, `build-gates-pipeline`.
