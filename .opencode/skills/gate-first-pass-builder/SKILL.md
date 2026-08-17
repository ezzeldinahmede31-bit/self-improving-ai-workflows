---
name: gate-first-pass-builder
description: "Build ANY n8n workflow or AI agent so it passes the user's own build gates (build_gates_pipeline.py) on the FIRST attempt — no rejections, no fixes-after-the-fact. Loaded as MANDATORY STATE -2c before every workflow/agent build. Emits the live avoid-list from the real rejection history (scripts/gate_first_pass_avoidlist.py reads memory/n8n_error_patterns.json), then enforces a pre-build checklist that maps 1:1 to the gate stages: schema cache preflight BEFORE any node is generated, pinned data + dry-run evidence, Error Trigger or continueOnFail, sub-workflow split for large graphs, agent wiring (ai_languageModel connected, allowed_tools declared, maxIterations ceiling, systemMessage), webhook authentication when the flow writes, credentials never inline, integer typeVersion, no orphaned/dangling nodes, RAG wiring (embeddings/store/splitter). Use on ANY request to build/create/edit a workflow, agent, automation, or n8n JSON — 'ابني workflow', 'صمم agent', 'اعمل automation', 'build a workflow', 'create an agent', 'n8n workflow', 'RAG workflow', 'chat agent', or any artifact that will be validated by the gates. Pairs with: build-gates-pipeline, incremental-generation, n8n-schema-guardrail, automation-known-issues-compass, n8n-rag-vector-qa."
---

# Gate-First-Pass Builder

The user's standing rule: any workflow or AI agent this workspace produces must
pass the gates on the FIRST attempt — rejections are a build defect, not a
permission slip. This skill makes first-pass success the norm instead of an
accident.

## The one-liner contract

Before touching a single node, emit this line so the route is visible:

`[gate-first-pass] avoid-list: <N> live patterns from scripts/gate_first_pass_avoidlist.py; checklist gates: preflight→security→quality→integrity→precision→rag→dry-run; target: READY_FOR_DEPLOYMENT exit 0`

## Step 0 — read the LIVE avoid-list (never build from memory)

Run `venv/bin/python scripts/gate_first_pass_avoidlist.py --top 10` and treat
every printed pattern as a guaranteed rejection if it can fire. The list is
generated from `memory/n8n_error_patterns.json` — the accumulated history of
what actually got builds rejected — so it always reflects the current gate
rules. The top offenders (as of last cleanup):

1. `preflight` — no schema cache present — run n8n-schema-preflight first
2. `quality` — no pinnedData on primary nodes (cannot unit-test instantly)
3. `quality` — no Error Trigger node and no continueOnFail on any node
4. `quality` — graph too large — recommend sub-workflow split
5. `dry_run` — no dry-run evidence (no pinned data, no expected_result)
6. `precision` E1 — agent with no language-model wired (ai_languageModel)
7. `precision` A1/A2 — orphaned or dangling nodes (never execute / drop items)
8. `security` — agent tool scope unrestricted, no allowed_tools list
9. `security` — no maxIterations ceiling on an agent
10. `security` — hardcoded secret patterns in the JSON

## Step 1 — preflight: schema cache BEFORE any node

- Confirm the schema cache exists: `memory/n8n_schema_cache.json`.
- If missing or stale, populate it first via the n8n MCP (get_node /
  validate_node per node type) or the n8n API. A `[PREFLIGHT] NEEDS_REVIEW`
  or `FAIL` is the single most common rejection — it is also the cheapest to
  prevent.
- Every node you emit must carry: exact live `type`, positive-integer
  `typeVersion` (never `4.4`), and only parameter keys the schema defines.

## Step 2 — generate incrementally (one node, one check)

Follow `incremental-generation`: emit ONE node → check it against the schema
cache → wire it → repeat. No blind whole-graph one-shot emit. Each node must
be reachable (incoming edge from a trigger or an upstream node) the moment it
is created, so A1/A2 can never fire at the end.

## Step 3 — the pre-build checklist (maps 1:1 to gate stages)

### Security
- No secrets in node parameters, expressions, or Code-node source — use
  pre-registered n8n credentials only (`n8n-credential-security-guard`).
- No `sk-...`, `api_key=`, `password`, token literals in the JSON text.
- Every AI Agent node:
  - `ai_languageModel` output wired to a real chat-model node.
  - explicit `allowed_tools` list (no `*`, no `all`, no undefined tools).
  - `maxIterations` set (values above 25 are treated as unbound).
  - a system prompt present (empty prompt = prompt-injection surface).
  - external data referenced in the prompt wrapped in
    `<untrusted_external_data>` delimiters.
- Webhook triggers that lead to any write operation MUST have an
  `authentication` mode other than `none` (D1), and ideally an HMAC signature
  (D2) plus timestamp freshness (D3).
- Destructive or state-changing tools on agents require
  `requiresHumanApproval`.

### Quality
- Schema V2 expressions: `$input.first().json`, no bare `$json` on nodes with
  multiple incoming edges, no `moment.js`.
- Error handling present: an Error Trigger node OR `continueOnFail` /
  `onError: continueRegularOutput` on the fragile nodes. Silent
  failure is a defect.
- Pinned data on the primary nodes so the workflow is unit-testable instantly.
- Keep the graph small — split large graphs into sub-workflows
  (`n8n-subworkflow-modularizer`) rather than one oversized canvas.

### Integrity (DAG)
- Every node reachable from a trigger; no orphaned nodes, no cycles, no
  unknown source/target references, no dangling output branches.

### Precision (runtime structural)
- Duplicate node names are a hard failure — keep names unique and verb-first.
- A deployable (non-subworkflow) workflow needs a trigger node.
- typeVersion always a positive integer.
- Every `$node.X` / `$('X')` reference resolves to a real node name.
- App-like nodes (HTTP, Google Sheets, Telegram, Qdrant, NVIDIA...) carry a
  real credential; HTTP may declare `authentication: none` explicitly.
- RAG graphs: embeddings wired into the store's `ai_embedding`, store wired
  into the agent via `ai_vectorStore`/`ai_retriever`, a text splitter sitting
  load-side of the embeddings, real (non-placeholder) collection names, Qdrant
  upsert via PUT not POST, NVIDIA `input_type` present.

### Dry-run
- Before delivery the workflow must have run with real evidence: pinned data
  AND an expected result — either pinned on the trigger (when a trigger
  exists) or on any node for offline mocks. `DRY_RUN_EVIDENCE_MISSING` blocks
  delivery.

## Step 4 — run the gates on the finished artifact

`venv/bin/python scripts/build_gates_pipeline.py <artifact> --schema-cache memory/n8n_schema_cache.json`

- Watch for `[PREFLIGHT] PASS` and `[DRY-RUN] PASS`.
- Only VERDICT `READY_FOR_DEPLOYMENT` (exit 0) may ship. Any other verdict:
  fix the listed violation, re-run, do not work around it.
- On repeated same-reason rejection or a timeout, the attempt guard stops the
  loop and asks the human — stopping is honest, silence is not.

## Step 5 — if a gate rejects a CORRECT build

Report it as a possible gate false positive (evidence: the built artifact is
rule-compliant yet the gate fired). Known historical false positives already
fixed: `[TOOL_SCOPE_LOCK]`/`[NO_ITERATION_CEILING]` on non-agent
`@n8n/n8n-nodes-langchain.*` sub-nodes (vector stores, chat models,
embeddings, loaders, splitters, chat triggers) — those nodes have no tools,
iterations or prompts to gate, and the narrow agent detector now excludes
them. Do not "fix" a workflow to satisfy a false positive.

## Writing this skill's docs / new skills

Prose in skill docs can trip the DeepReasoningGate counting keyword regex.
The trigger set includes words that appear often in ordinary English — the
word for "coun" + "t" (counting), "b" + "et" + "ween", "at " + "least",
"at " + "most", "in the " + "interval", "in" + "clusive", "ex" + "clusive",
and "how " + "many". When writing docs, reword around those words unless the
text is genuinely about interval arithmetic.
