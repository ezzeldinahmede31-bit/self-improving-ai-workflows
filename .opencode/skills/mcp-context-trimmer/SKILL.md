---
name: mcp-context-trimmer
description: "Sort, summarize, and trim outputs returned from MCP tools / API responses before passing them to the next workflow node, to avoid context-window exhaustion and slowdowns. Use whenever a workflow node (HTTP, MCP client, LLM, scraper) could return large payloads that must be condensed."
---

# MCP Context Trimmer

Protects the LLM context window and keeps large payloads from dragging execution.

## Rules
1. **Default trim**: never forward a raw API/MCP response that exceeds ~500 tokens
   of useful data into an LLM without summarizing it first.
2. **Extraction over summarization** where possible: pull only the fields the next
   node needs (e.g., from a huge JSON → `name, website, email, size`).
3. Use a Code node (or the LLM chain itself) to:
   - Deduplicate by a stable key.
   - Keep top-N after sorting by a relevance score.
   - Truncate list fields to a max (e.g., 50 items for a Telegram preview).
4. For multi-item LLM classification: batch in chunks of ≤ threshold, and only forward
   the batch summary + qualifying records downstream (an early Filter node BEFORE the LLM).

## Where to place the trimmer
- Immediately after any HTTP / MCP / scraper node that returns variable-size data.
- Before any AI Agent / LLM node (token budget).
- Before creating attachments for Telegram/email.

## Sort-first policy
When a payload has many candidate records but only N are wanted:
1. Score / filter by required criteria (country, size, valid email, verified MX).
2. Sort by descending quality.
3. Slice to the requested limit.
4. Forward only the slice.

## Practical thresholds
- Telegram preview text: ≤ ~3500 chars.
- HTTP JSON forwarded to LLM: ≤ ~7000 chars (~2k tokens), else chunk+summarize.
- CSV/XLSX export: no trim (but dedupe first).

## Optimization benefits (report)
- Tokens saved vs raw = X%.
- Executions faster because downstream only sees the essentials.

## Failure checks
- [ ] No node passes unbounded raw API dumps into an LLM.
- [ ] Dedupe happens BEFORE cost-heavy processing.
- [ ] Sort → slice → forward is used wherever a limit exists.