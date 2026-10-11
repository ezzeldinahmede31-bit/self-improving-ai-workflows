---
name: the-agency-agents
version: "1.0.0"
description: "Use the 77 installed Agency specialist agents (marketing, sales, product, testing, support + healthcare/workflow/MCP picks) from msitarzewski/agency-agents. Use when the task needs a specialist persona (SEO audit, ad copy, clinic content, code review, proposal, pricing) instead of a generic answer."
---

# the-agency-agents

A roster of specialist AI personas from **The Agency** (`https://github.com/msitarzewski/agency-agents`, MIT, 157k stars): each agent is a Markdown file with deep role expertise, a distinct voice, and deliverable-focused workflows. Instead of writing long prompts to explain the role you want, you activate the matching specialist.

## Installed on this machine

- **Location:** `.opencode/agents/` (77 agents, project-scoped)
- **Divisions:** marketing (37), sales (9), product (6), testing (9), support (6)
- **Specialist picks (10):** `healthcare-customer-service`, `healthcare-marketing-compliance-specialist`, `medical-billing-coding-specialist`, `agents-orchestrator`, `workflow-architect`, `mcp-builder`, `customer-success-manager`, `business-strategist`, `specialized-pricing-analyst`, `language-translator`
- **Source clone:** `/tmp/agency-agents` (depth-1, for reconvert/reinstall)

## When to use

| User says | Activate |
|-----------|----------|
| SEO audit,AEO/GEO, keyword plan | `seo-specialist`, `ai-citation-strategist`, `aeo-foundations-architect` |
| Clinic content/sales (Arabic) | `healthcare-customer-service`, `healthcare-marketing-compliance-specialist`, `clinic-organic-sales-content` project skill |
| Ad copy, hooks, video script | `ad-creative-strategist`, `viral-hooks` project skill, `video-optimization-specialist` |
| Offer, pricing, proposal | `specialized-pricing-analyst`, `proposal-strategist`, `offer-lead-gen-strategist` |
| Code review, architecture | `code-reviewer`, `backend-architect`, `ai-generated-code-security-auditor` |
| n8n workflow design | `workflow-architect`, `agents-orchestrator` |
| MCP/tool building | `mcp-builder` |
| Translation AR/EN | `language-translator` |

List all installed: `ls .opencode/agents/`

## How to invoke

Reference the agent file directly when delegating (Task tool `subagent_type` or reading the persona first):

```
Read .opencode/agents/seo-specialist.md, then act strictly in that voice and process.
```

For multi-specialist work, chain them: strategist → creator → reviewer (e.g. `keyword-research` → `content-creator` → `evidence-collector`).

## Update procedure

Upstream moves fast. Refresh monthly (or when a persona feels stale):

```bash
git -C /tmp/agency-agents pull --depth 1
bash /tmp/agency-agents/scripts/convert.sh --tool opencode
bash /tmp/agency-agents/scripts/install.sh --tool opencode --division marketing,sales,product,testing,support --agent healthcare-customer-service,healthcare-marketing-compliance,medical-billing-coding-specialist,agents-orchestrator,specialized-workflow-architect,specialized-mcp-builder,customer-success-manager,business-strategist,specialized-pricing-analyst,language-translator
```

Keep the subset under ~119 agents (OpenCode runtime limit — upstream bug). To add a division later: `engineering`, `design`, `security`, `finance`, `game-development`.

## Boundaries

- Agents are **personas/prompts**, not sandboxes — they don't add tool permissions by themselves; pair with `agent-control-plane-adapter` / `human-approval-gates` for consequential actions.
- Verify persona output with `evidence-over-memory` (real tool results, not persona confidence).
- Medical/finance personas give drafts, not professional advice — human review mandatory.

## Pairs with

| Skill | Why |
|-------|-----|
| `agent-reach` | Specialists research the live internet (trends, competitors, videos) before producing |
| `omni-request-orchestrator` | Audience psychology pass before the specialist produces |
| `clarify-before-execute` | Confirm the contract before activating a specialist chain |
| `evidence-over-memory` | Persona claims must cite tool output |
| `human-approval-gates` | Approval before publishing/ sending anything a persona drafted |
| `build-gates-pipeline` | Mandatory pre-deploy gates |

## Frontmatter

```json
{
  "name": "the-agency-agents",
  "version": "1.0.0",
  "description": "Use the 77 installed Agency specialist agents (marketing, sales, product, testing, support + healthcare/workflow/MCP picks)",
  "author": "msitarzewski (adapted for opencode)",
  "license": "MIT",
  "tags": ["personas", "specialists", "marketing", "sales", "seo", "clinic", "code-review", "agency-agents"],
  "triggers": ["activate SEO mode", "act as a specialist", "agency agent", "I need a marketer", "review like a senior", "clinic specialist", "ad strategist"]
}
```

---

*Installed from official msitarzewski/agency-agents (MIT) via convert.sh + install.sh --tool opencode; 77/282 agents curated for agency + clinics + content work*
