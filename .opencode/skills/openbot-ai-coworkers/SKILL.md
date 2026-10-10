---
name: openbot-ai-coworkers
description: Deploy and operate CopilotKit OpenBot AI coworkers that each get their own computer with a real browser, files, and granted tools, where every action is decided before it happens and recorded after. Use when the user says 'OpenBot', 'موظف AI', 'AI coworker', 'AI employee that works in front of me', 'every step recorded', 'bring my own agent', 'AG-UI bot', 'تسجيل كل خطوة', or wants a self-hosted ChatGPT-like assistant running on their own infrastructure.
version: 1.0.0
---

# OpenBot AI Coworkers

## Purpose

Stand up and operate **CopilotKit OpenBot** (MIT, alpha): a self-hosted agent
platform where each AI coworker gets its own computer — a real Chromium
browser with its own logins, its own `/workspace` files, and only the tools
granted to it. Every tool call passes one gateway that decides against policy
(CEL, fail-closed) and writes an audit row BEFORE acting. Source:
https://github.com/CopilotKit/openbot (raw README verified this session);
TikTok intel: SalmanAlFares00 video 7690216470780955910 ("موظف AI يشتغل
جدامك، وكل خطوة مسجلة").

## When to use

- User asks for an AI employee/coworker that works visibly with recorded steps.
- User wants a company-owned ChatGPT/Claude/Grok equivalent on their own infra.
- User wants to connect any AG-UI agent (LangGraph, Mastra, CrewAI,
  Pydantic AI, Google ADK, hand-written) as a governed coworker.
- User asks about OpenBot setup, computers, audit, approvals, routines.

## Steps

1. **Frame it honestly:** OpenBot is a TEMPLATE to clone and own, not a
   hosted product; nothing is published as a package. Alpha status — expect
   rough edges. Requirements: Docker, Bun 1.3+, a CopilotKit Intelligence
   project (free Developer plan works, self-hostable on a Mac), one model key.
2. **Clone and configure (never commit secrets):**
   ```sh
   cp .env.example .env && bun install
   npx --yes copilotkit@latest login
   npx --yes copilotkit@latest project select
   bun scripts/setup-learning.ts
   ```
   Fill `OPENAI_API_KEY`; generate a real `KEY_ENCRYPTION_KEY`
   (`openssl rand -base64 32` — the example key is public). Keep managed
   Intelligence URLs unless self-hosting. Credentials go through
   `/admin/credentials` (encrypted, write-only, never in tenant YAML).
3. **Run and verify:** `bash scripts/start.sh` (Docker services, migrations,
   API :3001, app :3010, health-checked). Open http://localhost:3010 and
   prove it: ask `/bot` to open news.ycombinator.com and report the top
   story; then inspect `/admin/audit` for the recorded rows.
4. **Govern before delegating:** add deny rules/presets at
   `/admin/boundaries`, retry the same browser action, and confirm the
   refusal names its rule. Login walls/2FA hand control to the person
   (`computer.help_requested` → `control_taken` → `control_released`);
   while a person drives, Bot actions are refused, not queued.
5. **Grow carefully:** create Bots from `/bots` (standing role, private by
   default); tenant agents via `agents.yaml` (`built-in` prompt or
   `remote-ag-ui` endpoint; private addresses need
   `AGENT_ENDPOINT_ALLOWED_HOSTS`). Single-user mode
   (`OPENBOT_SINGLE_USER=true`) is for a fresh laptop clone only — delete it
   and configure Google/Microsoft/Okta (or SAML/OIDC) before anyone else
   connects. Cap routines (15-min floor, max 20, auto-off after 10 failures).

## Verification

- `bash scripts/start.sh` prints healthy services; the HN top-story task
  succeeds AND its rows appear in `/admin/audit` with permit/refuse verdicts.
- A `/admin/boundaries` deny rule demonstrably refuses the same action it
  previously permitted. No credential value appears in YAML, logs, or audit.

## Pairs with

- `persistent-browser-automation` + `hitl-captcha-auth-handler` (login-wall
  handoff pattern) + `site-login-session-registry` (per-Bot browser profiles).
- `human-approval-gates` + `deploy-signoff-governance` (approvals before
  Bot autonomy) + `immutable-audit-log` (audit-trail discipline).
- `build-gates-pipeline` (gate any workflow an OpenBot Bot will act on).
