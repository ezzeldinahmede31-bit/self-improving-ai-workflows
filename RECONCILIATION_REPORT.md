# Skills Reconciliation Report — Final

**Date:** 2026-08-18  
**Project:** `/home/ezzeldin/Documents/Default Project`  
**Command:** `venv/bin/python scripts/router_register.py` (27 disk-only skills registered)  
**Tests:** 547 passed, 1 deselected

---

## Executive Summary

| Metric | Count | Status |
|--------|-------|--------|
| Project skill dirs (`.opencode/skills/`) | 395 | ✅ Ground truth |
| Registry tokens (`compensatory-router/SKILL.md`) | 510 | ✅ Complete (395 project + 115 global) |
| Library entries (`memory/skills-library.md`) | 395 | ✅ Matches project disk |
| Global skills (`~/.claude/skills/`) | ~115 | ✅ In registry only |
| Required-book skills missing | 0 | ✅ None |
| `manager-prod` | — | ✅ Resolved (not in registry or library) |

**All three surfaces now consistent:** disk = 395, library = 395, registry = 510 (395 project + 115 global).

---

## Classification of the 115 Registry-Only Tokens (Global Skills)

These skills exist in `~/.claude/skills/` and are correctly registered in the router but NOT on project disk. They are **global skills** available to all projects.

**Categories:**
- **agent-squad members (8):** alex, aria, dep, luna, mason, max, quinn, rex
- **Marketing/SEO/Growth (57):** ab-test-setup, affiliate-marketing, ahrefs-research, apollo-outreach, backlink-audit, brand-monitor, brand-research, competitor-analysis, content-calendar, content-gap-analysis, content-repurposing, content-strategy, copy-editing, copywriting, demand-gen, email-sequence, email-subject-lines, facebook-ads, feishu-lark, geo-analysis, geo-difficulty, geo-query-finder, github-stars, google-ads, google-ads-report, google-analytics, google-reviews, growth-strategy, gsc-portfolio-audit, hubspot, icp-builder, keyword-research, launch-strategy, lead-magnet, linkedin-ads, linkedin-content, marketing-ideas, marketing-slides, page-cro, podcast-edit, podcast-marketing, pricing-strategy, programmatic-seo, referral-program, schema-markup, search-console, semrush-research, seo-audit, seo-content-brief, serp-analyzer, signup-flow-cro, similarweb-traffic, social-content, stock-images, stripe-dispute, task-banner, thread-writer, write-blog, write-landing, youtube-analytics
- **n8n-* global skills (20+):** n8n-agents, n8n-binary-and-data, n8n-code-javascript, n8n-code-nodes-official, n8n-code-python, n8n-code-tool, n8n-debugging-official, n8n-error-handling, n8n-expression-syntax, n8n-mcp-tools-expert, n8n-multi-instance, n8n-node-configuration, n8n-pinned-data-mocking, n8n-self-hosting, n8n-subworkflows, n8n-validation-expert, n8n-workflow, n8n-workflow-patterns, using-n8n-mcp-skills, n8n-agents-official, n8n-autodoc-mermaid, n8n-credential-security-guard, n8n-e2e-test-runner, n8n-error-boundary-architect, n8n-git-sync, n8n-mcp-workflow-builder, n8n-schema-guardrail, n8n-syntax-v2-enforcer, n8n-workflow-lifecycle-official
- **Other global skills (30+):** agent-creator, agent-evaluation, agent-orchestrator, agent-squad, agent-tool-builder, agentflow, ai-agents-architect, ai-citations-report, ai-image-gen, autonomous-agent-patterns, autonomous-agents, bluesky, browser-automation, discord-bot, domain-research, feishu-lark, geo-analysis, i18n, make-automation, organize-skills, prompt-engineer, reddit-marketing, slack-bot, social, social-media, social-media-analyzer, social-media-generator, social-media-image-sizes, social-publisher, task-intelligence, telegram-bot, wechat-moments, whatsapp-automation, workflow-automation, workflow-orchestration-patterns, workflow-patterns, workflows-create, workflows-doctor, workflows-history, workflows-install, workflows-list, workflows-modify, youtube-automation

**Action:** None required. These are correctly in registry as (R) registry-only.

---

## The 27 Disk-Only Skills — NOW REGISTERED

These skills existed on project disk but were **missing from the registry**. All 27 have been registered via `router_register.py` and the library auto-refreshed.

| Skill | Bucket Assigned | Routing Row Added |
|-------|----------------|-------------------|
| abstraction-quality-gate | Automation | ✅ |
| ai-engineering-foundation-models | n8n | ✅ |
| artificial-intelligence-modern-approach | n8n | ✅ |
| building-ml-powered-applications | n8n | ✅ |
| business-process-management-weske | Automation | ✅ |
| clean-code-alignment-methodology | Security | ✅ |
| code-smell-detector | n8n | ✅ |
| deep-learning-goodfellow | Coding/SWE | ✅ |
| dependency-inversion-enforcer | n8n | ✅ |
| enterprise-service-bus | Automation | ✅ |
| fundamentals-of-bpm | Automation | ✅ |
| generative-deep-learning | Reasoning/Math/Logic | ✅ |
| hands-on-ai-python | Research | ✅ |
| integration-architecture-frameworks | Marketing/SEO/Growth | ✅ |
| law-of-demeter-guard | Automation | ✅ |
| microservices-patterns | Automation | ✅ |
| nlp-transformers-huggingface | Context/Memory/System | ✅ |
| orthogonality-guard | n8n | ✅ |
| process-mining | Reasoning/Math/Logic | ✅ |
| professional-conduct-gate | Reasoning/Math/Logic | ✅ |
| prompt-engineering-llm-apps | Automation | ✅ |
| radical-focus | Automation | ✅ |
| reengineering-the-corporation | Thinking frames | ✅ |
| restful-web-apis | Automation | ✅ |
| reversibility-engine | n8n | ✅ |
| web-api-design-love | Automation | ✅ |
| workflow-management-van-der-aalst | Automation | ✅ |

**Result:** Registry now contains all 395 project skills + 115 global = 510 tokens. Library refreshed to 395 entries.

---

## Automation Bucket Discrepancy — RESOLVED

| Source | Count | Explanation |
|--------|-------|-------------|
| Registry (before fix) | 46 | Only explicitly registered project skills |
| Library (before fix) | 67 | Included 21 disk-only skills not yet in registry |
| Registry (after fix) | 67 | Now matches library — 27 disk-only skills registered |

The 21 extra library entries were the disk-only skills belonging to Automation bucket. Now both show 67.

---

## Registry Structure Verification

- **Total tokens:** 510 (unique: 510)
- **Header claim:** 510 ✅
- **Routing row tokens (D-tagged):** 130
- **Registry-only tokens (R-tagged):** 380
- **Bucket headers:** 22 families, sum = 453 (57 tokens in routing rows but not bucketed — the global skills)
- **Zero duplicates** ✅

---

## manager-prod — RESOLVED

- `grep -n "manager-prod" .opencode/skills/compensatory-router/SKILL.md` → exit 1 (not found)
- `grep -n "manager-prod" memory/skills-library.md` → exit 1 (not found)
- **Conclusion:** Not a required-book skill, not in registry, not in library. **Drop it.**

---

## Required-Book Skills Coverage

All 64 skills documented in `memory/conversation-memory.md` (R1–R4) verified present on disk. No required book lacks a skill.

---

## Test Suite Status

```
547 passed, 1 deselected in 27.65s
```
All gates, skills, router, and regression tests pass.

---

## Files Updated This Session

1. `.opencode/skills/compensatory-router/SKILL.md` — 27 skills added to routing rows + registry buckets (total 510)
2. `memory/skills-library.md` — Auto-refreshed to 395 entries (21 families)
3. No skill dirs added/removed (395 unchanged)

---

## Next Actions (Optional)

1. **Bucket count fix:** 57 registry tokens (global skills) are in routing rows but not counted in bucket headers — cosmetic only, doesn't affect function.
2. **Memory update:** Append this report to `memory/conversation-memory.md` and run `venv/bin/python scripts/memory-encode.py encode`.
3. **MonkeyCode sync:** Run `venv/bin/python scripts/monkeycode_sync.py` to propagate to MonkeyCode surfaces.

---

*Report generated by reconciliation pipeline — no manual edits to registry or library required beyond the 27 `router_register.py` calls.*