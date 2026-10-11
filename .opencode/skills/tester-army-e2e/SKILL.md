---
name: tester-army-e2e
version: "1.0.0"
description: "Write agentic end-to-end tests with tester-army/e2e (agent.act/agent.assert + classic locators, web + mobile, smart replay without model calls). Use when the user says e2e test, agentic testing, اختبار end-to-end, test the checkout flow, or wants UI tests that don't break on every CSS change."
---

# tester-army-e2e

Agentic E2E testing framework by **TesterArmy (Callstack team)** — `https://github.com/tester-army/e2e` (Apache 2.0). Describe the goal in plain English; an agent drives the app. Mixes agentic actions with classic Playwright-style locators/assertions in one test, for **web + mobile (iOS/Android)** in a single SDK.

## Install / requirements (this machine)

- Node ≥22 required (system node is v24.21.0 ✅, installed via nodesource)
- e2e CLI verified: `npx -y e2e@0.19.0 --version` → `0.19.0`
- Per-project setup: `npx e2e init` inside the app repo (scaffolds config + example test)
- Model key: bring your own — ChatGPT Plus, GitHub Copilot, SuperGrok, any AI-SDK model via Vercel AI Gateway, or a local model. No e2e subscription.

## The pattern (hybrid)

```ts
// tests/checkout.e2e.ts
import { test, expect } from 'e2e';

test('a member upgrades to Pro', async ({ app, agent, screen }) => {
  await app.open('/settings/billing');
  await agent.act('upgrade the workspace to the Pro plan');
  await agent.assert('the invoice preview shows a prorated amount');
  await expect(screen.getByRole('status')).toContainText('Pro');
});
```

- `agent.act('goal')` — natural-language goal, agent achieves it any way
- `agent.assert('expected state')` — smart verification
- `screen.getByRole()` + `expect()` — classic deterministic assertions

## Why it doesn't rot

**Smart Replay:** first run uses the model and records actions; later runs replay the same actions with **zero model calls** until the app actually changes. AI flexibility at deterministic speed and near-zero long-term cost.

## Packages

| Package | Role |
|---------|------|
| `e2e` | SDK + runner + CLI |
| `@e2e-dev/web` | Browser engine |
| `@e2e-dev/mobile` | iOS + Android engine |
| `@e2e-dev/github` | PR comments with screenshots/recordings |
| `@e2e-dev/kernel` | Hosted browsers |
| `@e2e-dev/eas` | Hosted simulators |

Migration guides included for Playwright, Cypress, Selenium, Detox, Maestro. Docs ship inside `node_modules/e2e/docs` (readable offline by coding agents).

## When to use

- New SaaS/app built with AI (Vibe Coding output) needs a safety net before production
- Classic selectors keep breaking (CSS churn) — replace brittle steps with `agent.act`
- One suite for web + mobile (React Native) with the same API
- Client QA-automation setup (agency service)

## Pairs with

| Skill | Why |
|-------|-----|
| `playwright-modern-automation` | Classic-selector fallback and trace-viewer debugging |
| `tdd-sandbox-proof-engine` | Unit-test discipline alongside E2E |
| `evidence-collector` (agency agent) | Screenshots/recordings as proof artifacts |
| `build-gates-pipeline` | Mandatory pre-deploy gates |

## Frontmatter

```json
{
  "name": "tester-army-e2e",
  "version": "1.0.0",
  "description": "Agentic E2E tests with tester-army/e2e (agent.act/assert + classic locators, web + mobile)",
  "author": "tester-army/Callstack (adapted for opencode)",
  "license": "Apache-2.0",
  "tags": ["e2e", "testing", "agentic-testing", "playwright-alternative", "qa", "mobile-testing"],
  "triggers": ["e2e test", "agentic testing", "اختبار end-to-end", "test the flow", "checkout flow test", "tester army"]
}
```

---

*Source: github.com/tester-army/e2e via n8nar Arabic guide (Ibrahim Khalil FB post); CLI v0.19.0 verified on this machine*
