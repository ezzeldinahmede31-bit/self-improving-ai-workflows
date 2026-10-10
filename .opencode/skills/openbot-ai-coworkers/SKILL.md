---
name: openbot-ai-coworkers
version: "1.0.0"
description: "Deploy and operate CopilotKit OpenBot AI coworkers with isolated computers, browser, files, tools, and fail-closed CEL policy governance"
---

# openbot-ai-coworkers

Deploy and operate **CopilotKit OpenBot** AI coworkers — self-hosted agents that each get their own isolated computer with a real browser, persistent file system, and governed tool access. Every action is decided before it happens and recorded after via a fail-closed CEL policy gateway. Use when the user says 'OpenBot', 'AI coworker', 'AI employee', 'self-hosted AI agent with browser', 'AG-UI bot', 'bring my own agent', 'every step audited', or wants a governed "computer use" layer inside their infrastructure.

## Source & Authority

| Property | Value |
|----------|-------|
| **Official repo** | `https://github.com/CopilotKit/openbot` |
| **License** | MIT (code) + CopilotKit Intelligence license for running instance |
| **Status** | Alpha (v0.0.x) — not production-ready |
| **Architecture** | Docker Compose: app (3010), server (3001), agent-computer (4100), supervisor (4500/4300), per-bot containers (4200+), PostgreSQL + pgvector |
| **Protocol** | AG-UI (any AG-UI endpoint works: LangGraph, Mastra, CrewAI, Pydantic AI, Google ADK, hand-written) |

## When to Use

- User wants **autonomous AI coworkers** that can browse, use files, and call tools with full audit trail
- Need **self-hosted** "computer use" (browser + files + tools) with governance
- Building **multi-agent systems** where each agent has persistent identity and isolated resources
- Require **human-in-the-loop takeover** for logins, 2FA, CAPTCHAs in the same UI
- Want **AG-UI compatible** agents that can be swapped (LangGraph, CrewAI, etc.)
- Need **CEL policy governance** (fail-closed, deny-by-default) for every tool/browser/file action

## Core Concepts

| Concept | Description |
|---------|-------------|
| **One computer per Bot** | Isolated container with Chromium, `/workspace` volume, browser profile; optionally gVisor (`COMPUTER_RUNTIME=runsc`) |
| **Gateway governance** | All browser/file/MCP/component calls route: resolve target → evaluate CEL policy → write audit row → execute |
| **CEL policy (fail-closed)** | Rules inspect `tool.name`, `intent`, `bot.id`, `actor.id`, `page.url/host`, `element.*`, `file.*`, `mcp.*`; missing policy = deny |
| **Human takeover** | Bot requests help at login/2FA; control handed over in same panel; recorded as `computer.help_requested`, `control_taken`, `control_released` |
| **Components over prose** | Bots answer with compiled React components (gallery + sandboxed playground) |
| **Governed MCP** | Curated connectors (Atlassian, Box, Slack, Salesforce, ServiceNow, Composio); custom servers pass URL checks |

## Setup & Operations

### Prerequisites
- Docker + Bun 1.3+
- PostgreSQL with pgvector extension
- Model API keys (OpenAI, Anthropic, etc.)
- CopilotKit Intelligence license (for running instance)

### Quick Start
```bash
# Clone and configure
git clone https://github.com/CopilotKit/openbot
cd openbot

# Generate secrets
openssl rand -base64 32  # for KEY_ENCRYPTION_KEY
# Add OPENAI_API_KEY, ANTHROPIC_API_KEY, etc. to .env

# Start stack
bash scripts/start.sh
# Opens http://localhost:3010
```

### Key Configuration Files
| File | Purpose |
|------|---------|
| `.env` | Model keys, tokens (`COMPUTER_TOKEN`, `SUPERVISOR_TOKEN`, `AGENT_TOOL_TOKEN`), `AGENT_ENDPOINT_ALLOWED_HOSTS` |
| `agents.yaml` | Declare coworkers (built-in or remote AG-UI endpoints) |
| `docker-compose.yml` | Service topology, per-bot isolation via `COMPUTER_SUPERVISOR_URL` |

### Admin Endpoints (secured)
| Endpoint | Purpose |
|----------|---------|
| `/admin/credentials` | Write-only encrypted secrets storage |
| `/admin/boundaries` | CEL policy rules (deny/allow per tool/action) |
| `/admin/audit` | Review all permitted/refused/failed actions |
| `/admin/plugins` | MCP servers, grants, deployment skills |
| `/bot` | AG-UI endpoint for bot interactions |

## n8n Integration Patterns

| Pattern | How |
|---------|-----|
| **n8n → OpenBot** | n8n HTTP Request node calls OpenBot `/bot` (AG-UI) or webhook triggers Bot action |
| **OpenBot → n8n** | Configure n8n as custom MCP server; grant via `/admin/plugins`; Bot calls n8n workflows as tools |
| **Shared audit** | Both write to PostgreSQL; correlate OpenBot `/admin/audit` with n8n execution logs |
| **Human approval bridge** | n8n workflow pauses for human approval; OpenBot's "take the wheel" handles browser 2FA/login |

> **No native n8n integration exists yet** — requires custom MCP server or webhook bridge.

## Verification Checklist

Before deploying any OpenBot workflow or configuration:
- [ ] `KEY_ENCRYPTION_KEY` generated and in `.env`
- [ ] All model API keys configured
- [ ] `agents.yaml` defines coworkers with correct AG-UI endpoints
- [ ] CEL policies in `/admin/boundaries` cover all intended tool/browser/file actions (fail-closed)
- [ ] Credentials stored in `/admin/credentials` (never in workflow JSON)
- [ ] Audit logging verified via `/admin/audit`
- [ ] `OPENBOT_DEV_NO_AUTH=0` for any network-exposed instance
- [ ] Build gates pass: `venv/bin/python scripts/build_gates_pipeline.py <artifact>`

## Pairs With

| Skill | Why |
|-------|-----|
| `persistent-browser-automation` | OpenBot's browser layer; shares patterns for login/2FA handling |
| `hitl-captcha-auth-handler` | Human takeover for CAPTCHA/2FA flows |
| `site-login-session-registry` | Persistent authenticated sessions per bot |
| `human-approval-gates` | Approval gates before destructive actions |
| `deploy-signoff-governance` | Sign-off ceremony for production deployments |
| `immutable-audit-log` | Tamper-evident audit trail for every action |
| `build-gates-pipeline` | Mandatory pre-deploy gate pipeline |
| `agent-control-plane-adapter` | Policy engine, token budgets, kill switch |
| `agent-runtime-guard-adapter` | Sub-millisecond policy checks on tool calls |

## Frontmatter

```json
{
  "name": "openbot-ai-coworkers",
  "version": "1.0.0",
  "description": "Deploy and operate CopilotKit OpenBot AI coworkers with isolated computers, browser, files, tools, and fail-closed CEL policy governance",
  "author": "CopilotKit (adapted for opencode)",
  "license": "MIT",
  "tags": ["ai-coworker", "computer-use", "browser-automation", "ag-ui", "self-hosted", "governance", "audit"],
  "dependencies": ["persistent-browser-automation", "hitl-captcha-auth-handler", "site-login-session-registry", "human-approval-gates", "immutable-audit-log", "build-gates-pipeline"],
  "triggers": ["OpenBot", "AI coworker", "AI employee", "self-hosted AI agent", "AG-UI bot", "bring my own agent", "computer use", "browser automation with audit"],
  "relatedSkills": ["seven-ai-tools-humam", "autonomous-agents-architecture", "enterprise-multi-agent-systems"]
}
```

---

*Generated from official CopilotKit/OpenBot source (MIT) + project governance standards*

---