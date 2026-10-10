---
name: seven-ai-tools-humam
version: "1.0.0"
description: "Multi-engine AI answer collection in n8n via Scrapeless Official (7 engines: ChatGPT, Copilot, Gemini, Google AI Mode, Google AI Overview, Grok, Perplexity) with normalization, storage, and alerting"
---

# seven-ai-tools-humam

Build **multi-engine AI visibility workflows** in n8n using the **Scrapeless Official** integration (v0.5.4+) — a verified n8n partner node that exposes **seven AI Scraper actions** to query ChatGPT, Copilot, Gemini, Google AI Mode, Google AI Overview, Grok, and Perplexity in parallel, normalize results, and route to storage/reporting. Use when the user says 'seven AI tools', 'سبع أدوات ذكاء اصطناعي', 'Humam Najdat tools', 'AI answer monitoring', 'multi-engine AI visibility', 'GEO monitoring', 'brand citation tracking', 'compare AI engines', or wants to automate AI answer collection across multiple engines.

## Source & Authority

| Property | Value |
|----------|-------|
| **Official integration** | `n8n-nodes-scrapeless` (verified n8n partner node) |
| **Scrapeless docs** | `https://www.scrapeless.com/en/blog/scrapeless-n8n-ai-scraper-workflows` |
| **GitHub** | `https://github.com/scrapeless-ai/n8n-nodes-scrapeless` |
| **npm package** | `n8n-nodes-scrapeless@0.5.4+` |
| **Status** | Production-ready (verified partner node) |
| **Credential** | Scrapeless API key (password field in n8n) |

## The Seven AI Scraper Actions

| # | Engine | Action Name | Required Inputs | Engine-Specific Controls |
|---|--------|-------------|-----------------|--------------------------|
| 1 | **ChatGPT** | `chatGPT` | Prompt, Country | Web Search ✓, Shopping ✓ |
| 2 | **Copilot** | `copilot` | Prompt, Country | Mode: Chat/Reasoning/Search/Smart/Study |
| 3 | **Gemini** | `gemini` | Prompt, Country | — |
| 4 | **Google AI Mode** | `googleAiMode` | Prompt, Country | Shopping ✓, Location or UULE |
| 5 | **Google AI Overview** | `googleAiOverview` | Prompt, Country | Shopping ✓, Location or UULE |
| 6 | **Grok** | `grok` | Prompt, Country | Mode: Auto/Expert/Fast |
| 7 | **Perplexity** | `perplexity` | Prompt, Country | Web Search ✓ |

> **Shared fields**: `Prompt` (string), `Country` (ISO code) — enables one input record across all engines.
> **Geo-targeting**: All engines accept `Country`; Google AI Mode/Overview add `Location` or `UULE` for city-level precision.
> **Shopping**: ChatGPT, Google AI Mode, Google AI Overview — double base rate when enabled.

## When to Use

- **Brand visibility / citation tracking** — run controlled prompt panels across engines, store answers + citations, compare over time
- **Regional answer comparison** — same prompt, different countries/locations, compare market-specific responses
- **Product discovery monitoring** — enable Shopping on supported engines, normalize product fields, alert on changes
- **Research digests** — send research prompts to selected engines, extract themes, publish structured digests to Slack/Notion/email
- **Content & market briefs** — combine AI answer data with Scrapeless Universal Scraping API for webpage context
- **GEO / AEO programs** — automated, repeatable measurement without manual browser checks

## n8n Workflow Pattern (5 Stages)

```
Schedule Trigger → Edit Fields (prompt record) → 7× Scrapeless Official branches
                                                      ↓
                    Normalize each branch (common envelope)
                                                      ↓
                              Merge/Aggregate → Store → Notify
```

### Stage 1: Trigger
- Schedule Trigger (cron), Webhook, Form submission, or Manual run

### Stage 2: Build Prompt Record (Edit Fields)
```json
{
  "prompt": "What are the best web data tools for AI research teams?",
  "country": "US",
  "brand": "Scrapeless",
  "study": "ai-research-tools",
  "run_type": "weekly-monitor"
}
```

### Stage 3: Call 7 AI Scraper Actions
- Add **one Scrapeless Official node per engine**
- Resource: `AI Scraper` → Operation: select engine
- Map `Prompt` and `Country` from prompt record
- Configure engine-specific controls (Web Search, Mode, Shopping, Location/UULE)

### Stage 4: Normalize Each Branch (Edit Fields / Code)
**Common envelope** (nullable fields — result shapes differ):
```json
{
  "engine": "chatGPT",
  "prompt": "exact question sent",
  "country": "US",
  "answer": "main response text",
  "citations": ["source URLs when present"],
  "products": ["shopping results when present"],
  "raw_result": "complete JSON for later inspection",
  "study": "ai-research-tools",
  "collected_at": "ISO timestamp"
}
```

### Stage 5: Route Results
- Merge branches → aggregate → write to Google Sheets, Postgres, Airtable, Notion, Data Tables
- Add alerts only after clear rule for "material change" (brand mention, citation gain/loss, product appearance)

## Installation & Configuration

### 1. Install Scrapeless Official (verified node)
- n8n → Nodes panel → Search "Scrapeless Official" → Verified installation flow
- Confirm package version **0.5.4+**

### 2. Create Scrapeless Credential
- Scrapeless account → Dashboard → Copy API key
- n8n → Credentials → Scrapeless API → Paste key (password field)
- **Never** put API key in workflow JSON, screenshots, or docs

### 3. Build First Workflow
- Add Scrapeless Official node → Resource: `AI Scraper` → Operation: `chatGPT` (test)
- Map Prompt/Country → Run once → Inspect JSON output
- Define normalized schema → Add remaining 6 engine branches
- Add storage destination → Activate with production trigger

## Verified Use Cases (from Scrapeless docs)

| Use Case | Engines | Key Config |
|----------|---------|------------|
| **Brand citation tracking** | All 7 | Prompt panel with brand/non-brand variants; store citations + brand_mention boolean |
| **Regional comparison** | All 7 | Same prompt, multiple Country values; Google AI Mode/Overview add Location/UULE |
| **Product monitoring** | ChatGPT, Google AI Mode, Google AI Overview | Enable Shopping; normalize product fields; route changes to review queue |
| **Research digest** | Selected subset | Extract themes from answers; publish to Slack/Notion; keep raw results attached |
| **Market brief** | All 7 + Universal Scraping | Separate collection paths; join downstream |

## Verification Checklist

Before deploying any Scrapeless AI Scraper workflow:
- [ ] Scrapeless Official node version **0.5.4+** installed
- [ ] Scrapeless API credential created (separate from workflow)
- [ ] All 7 engine branches tested individually with sample prompt
- [ ] Normalization schema handles nullable fields (citations, products vary by engine)
- [ ] Raw result preserved alongside normalized fields
- [ ] Prompt version, engine settings, market, run label stored with each record
- [ ] Alert rules defined (what counts as "material change")
- [ ] Build gates pass: `venv/bin/python scripts/build_gates_pipeline.py <workflow>`

## Pairs With

| Skill | Why |
|-------|-----|
| `n8n-rag-vector-qa` | Combine AI answer data with document retrieval |
| `n8n-subworkflow-modularizer` | Each engine branch as sub-workflow |
| `n8n-error-boundary-architect` | Error handling per branch |
| `n8n-delivery-verification-gate` | Prove workflow runs end-to-end |
| `build-gates-pipeline` | Mandatory pre-deploy gates |
| `rate-limit-and-cost-guard` | Shopping = 2× cost; rate-limit API calls |
| `audit-trail-compliance` | Append-only log of every collection run |
| `schema-evolution` | Normalized schema versioning as engines change |
| `data-transformation-mapping-parsing` | Normalization logic in Code/Edit Fields nodes |

## Frontmatter

```json
{
  "name": "seven-ai-tools-humam",
  "version": "1.0.0",
  "description": "Multi-engine AI answer collection in n8n via Scrapeless Official (7 engines: ChatGPT, Copilot, Gemini, Google AI Mode, Google AI Overview, Grok, Perplexity) with normalization, storage, and alerting",
  "author": "Scrapeless (adapted for opencode)",
  "license": "MIT",
  "tags": ["n8n", "ai-scraper", "multi-engine", "ai-visibility", "geo-monitoring", "brand-tracking", "scrapeless", "verified-node"],
  "dependencies": ["n8n-mcp-workflow-builder", "n8n-subworkflow-modularizer", "n8n-error-boundary-architect", "n8n-delivery-verification-gate", "build-gates-pipeline", "rate-limit-and-cost-guard", "audit-trail-compliance"],
  "triggers": ["seven AI tools", "سبع أدوات ذكاء اصطناعي", "Humam Najdat", "AI answer monitoring", "multi-engine AI", "GEO monitoring", "brand citation tracking", "compare AI engines"],
  "relatedSkills": ["openbot-ai-coworkers", "n8n-rag-vector-qa", "n8n-ai-orchestration"]
}
```

---

*Generated from official Scrapeless n8n integration docs (verified partner node) + project governance standards*

---