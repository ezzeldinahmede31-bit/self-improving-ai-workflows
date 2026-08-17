---
name: automation-known-issues-compass
description: "The known-issues catalog + design-time checklist for n8n and Zapier: every common failure mode, its symptom, root cause and fix, encoded so that ANY automation/system design passes a pre-flight gate before a single node is placed. Covers n8n 2.x pitfalls (expression v1/v2 drift, typeVersion migrations, draft-vs-published confusion, silent webhook failures, credential/instance ambiguity, binary loss, pinned-data hijacking, execution DB retention, community-node imports, wait/timeout traps, code-node sandbox limits) and Zapier limits (task multipliers, premium app double-counting, polling minimums, free-plan path caps, silent auth expiry, no error branch on free tier, formatter/digest restrictions, webhook payload limits, Zap versioning-by-clone). Use BEFORE designing any n8n workflow or any decision about cloning to n8n, and whenever diagnosing a failing workflow or Zap. Trigger phrases: 'why does this workflow fail', 'n8n مشكلة', 'zapier limits', 'design an automation that won't break', 'pre-flight check', 'what breaks in n8n', 'is this Zap safe to clone'. Pairs with: using-n8n-mcp-skills, n8n-validation-expert, n8n-error-handling, n8n-multi-instance, n8n-syntax-v2-enforcer, n8n-schema-guardrail, zapier-system-cloner."
---

# Automation Known-Issues Compass

The permanent catalog of how n8n and Zapier actually break, so every design
avoids the trap from step zero and every failure is triaged in minutes.

## 0 — Worked live incident (log entry)

- 2026-08-14: `n8n_health_check` on our instance
  (https://ezzeldin8n.ezzeldin8n.cfd) → 502 Server Error. Diagnostic: API key
  configured, n8n version 2.69.0 (up to date), but instance NOT reachable →
  server/container likely down. Triage: check `docker ps` on the host, restart
  the container, hit /healthz. Pattern: 502 + "version: null" = instance down,
  NOT config error.

## 1 — Design-time pre-flight checklist (MANDATORY)

Run these gates before ANY n8n build:

1. **Endpoint alive**: `n8n_health_check` first — no builds against a dead instance.
2. **Instance identity**: `n8n_instances`/`get_profile` — which instance/folder am I targeting? Ambiguous writes fail closed (`INSTANCE_AMBIGUOUS`).
3. **Node schema vs installed version**: every node type + typeVersion checked against the LIVE registry (`get_node`) — never trust memory; typeVersions migrate and break parameter keys.
4. **Expression dialect**: n8n 2.x → `$input.item.json` / `$input.first().json`; legacy `$json` banned (n8n-syntax-v2-enforcer).
5. **Draft vs published**: n8n 2.30+ keeps a separate published version — an "active" workflow runs the PUBLISHED graph; edits stay draft until published. Check `mode='active'` before claiming what's live.
6. **Credentials**: only registered n8n credential IDs; getSchema → create; never inline keys (n8n-credential-security-guard). Ambiguous or missing credential = `NOT_FOUND` at runtime.
7. **Error paths**: every node that can fail gets an error output or Continue-on-fail + error workflow (n8n-error-handling) — silent failure is the #1 production bug.
8. **Webhook responses**: Respond to Webhook (manually) with correct 4xx/5xx bodies, or requests hang/fail with generic errors.
9. **Binary data**: keep `$binary` alive through transforms (Merge, paired item) or it silently vanishes (n8n-binary-and-data).
10. **Pinned data**: pin only for dev/manual test — pinned data replays in LIVE runs and masks real input; unpin before production.
11. **Retry & timeout**: `retryOnFail` + `maxTries` + `waitBetweenTries` tuned; long HTTP calls get explicit timeouts.
12. **Execution retention**: `saveDataSuccessExecution`/`saveDataErrorExecution` set or the DB balloons (default keeps everything).
13. **Large data**: >1MB payloads / >100k items — use pagination, loops, or streams; Code node context is capped (~100KB input per item in runMode).
14. **Sub-workflow reuse**: >6 nodes or repeated logic → sub-workflows with typed inputs (n8n-subworkflow-modularizer).
15. **Zapier parity** (when cloning): check the Zap's task multiplier + premium apps + polling cadence BEFORE promising cost/equivalence (Phase 3 of zapier-system-cloner).

## 2 — n8n known-issues catalog (symptom → cause → fix)

| Symptom | Root cause | Fix / skill |
|---|---|---|
| 502 on health check, version null | instance down (container/crash) | docker ps → restart → /healthz (see log §0) |
| `INSTANCE_AMBIGUOUS` on credential/workflow writes | multiple instances connected, target not pinned | pick instance first (n8n-multi-instance) |
| `NOT_FOUND` for a credential at runtime | wrong instance target OR credential scoped elsewhere | verify instance + credential list |
| "expression has a different output" / `$json is not defined` | v1/v2 dialect drift | rewrite with $input.item.json (n8n-syntax-v2-enforcer) |
| Node suddenly missing a parameter that used to exist | typeVersion changed → schema migrated | get_node versions/compare/breaking → bump typeVersion, re-map params (n8n-schema-guardrail) |
| Workflow "active" but old behavior runs | draft edited, published version untouched (2.30+ two-state) | mode='active' inspect → publish draft |
| Webhook stall / "request failed" with no error node | no Respond-to-Webhook node, or wrong HTTP status body | add Respond to Webhook w/ 200/4xx/5xx (n8n-error-handling) |
| Files/attachments empty after Merge/transform | binary dropped at transformation | keep pairedItem / extract binary late (n8n-binary-and-data) |
| Test shows old data in production runs | pinned data left on nodes | unpin all nodes before activate (n8n-pinned-data-mocking) |
| Agent tool returns "Wrong output type returned" | Code Tool must return string, not object | string result + specifyInputSchema (n8n-code-tool) |
| AI agent won't call a tool | tool name/description weak, or >1 tool same name | verb+noun names, distinct descriptions (n8n-agents) |
| Schedule fires wrong time | trigger timezone ≠ workflow timezone | set settings.timezone explicitly |
| Imported template inactive + missing nodes | community node not installed on instance | install missing community package, then activate |
| Execution succeeds but nothing happened | silent error inside branch | error outputs + error workflow + execution 'error' mode debug (n8n-debugging-official) |
| Execution store huge / slow | retention defaults save everything | set saveDataSuccess/ErrorExecution=all|none policy |
| Wait node "never resumes" | wait until time passed already / wrong unit | verify amount+unit, use continuation-time fields |
| Code node memory error on big data | sandbox context limit | runOnceForEachItem + process in chunks; or HTTP/DB |
| Response body JSON malformed in repo | expression produced string not object | JSON.parse in Code / Set node, validate with schema guardrail |
| Connection map with numeric keys / duplicates | hand-edited JSON | autofix (connection-numeric-keys / duplicate-removal) — n8n_validate_workflow |
| Qdrant upsert "missing field `ids`" | POST used on `/points` (that path is RETRIEVE) | upsert must be PUT `/collections/{name}/points?wait=true` (qdrant-ops) |
| Qdrant upsert "status" not ok | checking top-level status instead of `result.status` | read `result.status` == "completed" (rag_common.upsert_points) |
| NVIDIA embeddings 4xx | missing `input_type` or batch > 2 | input_type passage/query + batch <= 2 (nvidia-embeddings) |
| Vector store node red "no embeddings" | store node without ai_embedding wiring | wire embeddings node into store; RAG gate R1 fails this (n8n-rag-vector-qa) |
| Retrieval returns 0 hits / agent answers from general knowledge | collection name mismatch OR dim mismatch OR doc not ingested | rag_query first, check qdrantCollection + 1024-dim + points_count (qdrant-ops) |
| Store reads garbage in n8n | payload keys not `content`/`metadata` | @langchain/qdrant payload shape (rag_ingest.py) |
| RAG gate verdict `RAG_STRUCTURAL_VIOLATION` | store w/o embeddings (R1) or dangling ai_vectorStore/ai_retriever (R3) | fix wiring, re-run build_gates_pipeline Stage 3.45 (n8n-rag-vector-qa) |

## 3 — Zapier limits & pitfalls catalog (for cloning decisions)

| Zapier limit | Consequences | Clone strategy on n8n |
|---|---|---|
| Task multipliers per app (premium apps = 2×–3× tasks) | "cheap" Zaps burn tasks fast | irrelevant on self-hosted n8n — document savings |
| AI by Zapier actions priced per task | $/run grows with usage | OpenAI node (pay per token) or local model (§ gap design) |
| Polling triggers: 15-min minimum (free) / 2-min (paid) | slow reaction time | n8n Schedule Trigger can be faster, or webhook when source supports it |
| Free plan: only 3 Paths per Zap | limited branching | Switch/IF nodes unbounded |
| No error-branch on free tier | failures are silent, no retry control | error outputs + error workflow built-in (free) |
| App auth expiry → Zap stops silently | missed automations, no alert | n8n shows execution errors + notifications |
| Digest only on paid + quirks | daily digest hard to move | Code accumulate + flush schedule |
| Formatter limited operations | complex transforms need Code by Zapier | Code node = full JS/Python |
| Webhook payload ~10MB cap | big uploads fail | n8n handles larger + streaming options |
| Zap versioning = clone to change (old plans) | config drift, no CI | n8n + git-sync = real versioning |
| Task history retention (limited) | audit gaps | n8n executions + DB retention policy |
| No local execution / runs only in Zapier cloud | latency + data leaves your infra | self-hosted n8n keeps data local |

## 4 — Triage playbook (failing workflow → root cause in <10 min)

1. `n8n_health_check` (instance alive?) → 502 ⇒ §0 pattern.
2. `n8n_executions list` w/ status=error → `get` mode=error (upstream node + stack trace).
3. `n8n_validate_workflow` (schema vs live registry, connections, expressions).
4. Credential check: `n8n_manage_credentials list` → is the referenced credential on THIS instance?
5. Draft vs published: `n8n_get_workflow mode='active'` — what's actually running?
6. Reproduce manually: pin sample data → execute → compare.
7. Fix → revalidate → re-run → log what you found in the catalog (§2) if new.

## 5 — Skill map (who owns what)

- Build lifecycle: using-n8n-mcp-skills → n8n-mcp-workflow-builder → n8n-schema-guardrail → n8n-syntax-v2-enforcer
- Failure handling: n8n-error-handling, n8n-error-boundary-architect, n8n-debugging-official
- Data: n8n-binary-and-data, n8n-code-javascript / -python / -tool
- Instances/creds: n8n-multi-instance, n8n-credential-security-guard, n8n-self-hosting
- Testing/ship: n8n-pinned-data-mocking, n8n-e2e-test-runner, n8n-git-sync, n8n-autodoc-mermaid
- Zapier side: zapier-sdk, zapier-system-cloner, zapier-make-patterns, workflows-doctor

Rule: when designing ANY system, load THIS skill first (compass), then the
specialists it points to. When a NEW failure is seen, add it to §2/§3 with its
fix — the catalog grows forever.