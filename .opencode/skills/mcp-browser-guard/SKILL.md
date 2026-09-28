---
name: mcp-browser-guard
description: "MCP and browser guard skill (server enrollment with risk tiers, domain allow-list, download quarantine). Use when an agent browses, downloads, or calls MCP tools, when an unknown server appears, or when a file must clear quarantine first. Trigger phrases: 'enroll MCP', 'allow-list domain', 'scan download', 'حارس المتصفح'."
---

# MCP + Browser Guard (Registered Surfaces Only)

Code: `mcp_browser_guard.py` (stdlib only). `McpRegistry` enrolls
servers (tools/permissions/risk/signature); calls to unenrolled
servers or undeclared tools deny; high-risk needs approval.
`BrowserGuard` allow-lists navigation (deny-by-default, suffix
match) and gates downloads (size ceiling, extension policy, content
hook) into quarantine. Automation itself still routes through the
sandbox + egress firewall.

## Verification

- `tests/test_p2c_guard.py` green (tiers, unknown/undeclared deny,
  revoke, allow-list, three quarantine paths).
- Agents never see unenrolled servers or unlisted domains.

## Pairs with

`agent-runtime-guard-adapter` (call-time enforce), `agent-sandbox`
(execution side), `egress-firewall` (network side),
`skill-trust-registry` (registry shape), `build-gates-pipeline`.
