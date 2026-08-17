---
name: best-practice-first-designer
description: MANDATORY research-first gate before designing or building ANY n8n workflow or AI agent. Never invent the wheel — first find how the best existing implementations (n8n.io official templates, GitHub repos, skills, docs, communities, marketplace) solve exactly this task, adopt the strongest existing pattern, and only then apply the user's required modifications on top. Offline/from-memory designs are forbidden when a web pass can find better. Trigger on ANY request to 'design a workflow', 'build an AI agent', 'اعمل workflow', 'صمم agent', 'how should this automation work', 'build me a bot/agent/automation'.
---

# Best-Practice-First Designer

User's rule: **"لما اطلب منك تصمم workflow or ai agent لزم تشوف افضل طريقة ممكن تتعمل بيها علي الانترنت مثل github وباقي المواقع مش لزم تخترع العجلة من الاول وضيف انت عليه التعديلات المطلوبة"** — before designing any workflow or AI agent, find the best existing way on the internet (GitHub and other sites); don't reinvent the wheel; then add your required modifications on top.

Clean Code alignment: This skill enforces the Clean Code principle of "research first" (ground task in real context before building), "meaningful names" (ensure node names and variables are intention-revealing), "single-function nodes" (each node does one thing), "small functions" (keep nodes under 20 lines), "no duplication" (avoid reinventing existing patterns), and "command-query separation" (separate trigger from action nodes).

## Phase 0 — Inventory what we already know (30 seconds)

1. Check the internal skill stack FIRST: n8n-* skills, automation-known-issues-compass (failure catalog), zapier-system-cloner (for cloning), using-n8n-mcp-skills. If our own catalog already encodes the failure modes and best patterns for this task type, that is your baseline.
2. Load dont-reinvent-the-wheel's methodology for the build-vs-buy/reuse decision framing.

## Phase 1 — Web research pass (MANDATORY, before any node is placed)

Search the internet for existing implementations of the EXACT task. Minimum passes:

1. **n8n templates**: `n8n_search_templates` (keyword AND by_nodes AND patterns modes — a template by nodes or a pattern summary often exists for common tasks: lead capture, Telegram alerts, webhook→table, form→CRM, scraping→table, AI agent with tools).
   - If a template matches ≥70%: `n8n_get_template` full JSON and STUDY it (node types, typeVersions, expression style, error wiring, credential approach) — this is the reference design.
2. **GitHub**: `gh_grep_searchGitHub` for literal implementation patterns (`"n8n-nodes-base.telegram"`, `"n8n-nodes-base.dataTable"` usage, agent node configs) and web search for `<task> n8n workflow github`, `<task> ai agent architecture 2026`.
3. **Docs/communities**: official node docs via `n8n_get_node mode=docs`, plus search for real-world writeups (blog/newsletter/forum posts) of the same workflow shape — capture THEIR node choices and their KNOWN pitfalls.
4. **Marketplace/alts**: for agent designs check the AI-agent landscape (OpenAI Agents SDK, LangGraph, n8n langchain nodes, MCP) and for workflow tasks check whether a SaaS/ready tool already does it (per dont-reinvent-the-wheel scorecard — sometimes the answer is "don't build at all").

Record findings as a short table:

```
| Source | Found | Fit | Notes (nodes used, pitfalls) |
|--------|-------|-----|------------------------------|
| n8n template 1234 | email→Slack digest | 75% | uses IF + Merge, no error branch — we add onError |
| GitHub repo X | same scrape task | 60% | uses HTTP + Code parse, warns about responseFormat |
```

**Clean Code alignment**: Research grounds the task in real-world context before building, preventing "ivory tower" designs that violate the Clean Code principle of writing code that humans can understand.

## Phase 2 — Adopt the strongest pattern

1. Choose the ONE reference design that fits best (highest fit, most recent, most maintained).
2. **Ensure meaningful names**: Adopted nodes and variables must have intention-revealing names (Clean Code: "use intention-revealing names — variable/function names should explain why they exist and what they do").
3. **Single function per node**: Ensure each node performs exactly one responsibility (Clean Code: "single responsibility principle — classes should have only one reason to change").
4. State explicitly: "Baseline: <source>, adopted pattern: <nodes/flow>" — the design is BASED ON existing best practice, not invented.
5. Apply user modifications on top: every change they asked for is an explicit diff against the baseline (node added/removed, parameter changed, branch added).

## Phase 3 — Build and hand off

1. **Build small nodes**: Ensure each node is small and performs one function (Clean Code: "keep functions small — 20 lines or fewer, ideally 4-6 lines; one level of abstraction per function"). Avoid piling multiple responsibilities into a single node.
2. **Use meaningful names**: All node names, parameter names, and variable names must be intention-revealing (Clean Code: "pick one word per concept — don't use fetch, retrieve, and get for similar methods; use pronounsable names — makes discussion and code reviews easier").
3. **Hand off to n8n-delivery-verification-gate** — the workflow MUST be executed and verified before delivery (that gate is mandatory and separate from this one).

## Phase 4 — Report what was reused

Delivery must answer: "what did I reuse, from where, and what did I change" — so the user always knows nothing was invented from scratch when a proven pattern existed.

## Hard Rules

1. NO n8n workflow or AI agent design is produced directly from memory when the task type is common enough to have public templates/examples. Web pass FIRST.
2. If the web pass finds nothing matching (rare for common tasks), say so explicitly and justify the from-scratch design.
3. Never copy a template blindly: check its typeVersions against the installed n8n version, its expression dialect, and its error handling before adopting.
4. The adopted baseline must be cited (template ID, repo link, doc link) — unverifiable patterns are not baselines.