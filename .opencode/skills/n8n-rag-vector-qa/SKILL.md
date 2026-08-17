---
name: n8n-rag-vector-qa
description: "Build production RAG (retrieval-augmented generation) workflows in n8n — ingest a document corpus into a vector store and answer questions over it through a chat trigger + AI Agent. Covers the exact n8n 2.x langchain wiring (embeddings -> vectorStoreQdrant, toolVectorStore wrapper, splitter -> loader, chat trigger webhook path), the parameter names that must match the live schema (qdrantCollection, ai_embedding, ai_vectorStore, ai_textSplitter), and the structural RAG gate rules (R1-R6) so a workflow passes build_gates_pipeline.py Stage 3.45 before deploy. Use when the user says 'RAG workflow', 'chat with my documents', 'answer questions from PDFs', 'vector store QA', 'Qdrant + n8n', 'اسال الملفات', 'شات مع المستندات'. Pairs with qdrant-ops, nvidia-embeddings, n8n-schema-guardrail, incremental-generation, build-gates-pipeline, automation-known-issues-compass."
---

# n8n RAG / Vector QA Workflow

Build n8n workflows that ingest documents into a Qdrant collection and answer
questions over them, proven live on this workspace's Apple Q1.pdf pipeline
(Aug 2026): Google Drive trigger -> split -> embed -> Qdrant upsert, plus a
Chat Trigger -> Agent -> retriever QA loop.

## Architecture (the wiring that actually works)

Ingest branch (trigger -> store):
  Google Drive Trigger -> Download File -> Set (extract name/meta) ->
  Load Document (documentDefaultDataLoader) --ai_textSplitter--> Split Text
  (textSplitterRecursiveCharacterTextSplitter) --main--> NVIDIA Embeddings
  --ai_embedding--> Qdrant Insert (vectorStoreQdrant)

QA branch (chat -> agent):
  Chat Trigger -> AI Agent (n8n-nodes-langchain.agent)
    --ai_languageModel--> NVIDIA Chat Model (lmChatNvidia)
    --ai_vectorStore--> Qdrant Retrieve (vectorStoreQdrant)
    --ai_tool--> toolVectorStore wrapper (optional, for tool mode)

Key connection keys (n8n 2.x, edges owned by the *source* node):
- Embeddings node exposes `ai_embedding`; wire it INTO each vectorStore node.
- VectorStore node exposes `ai_vectorStore`; wire it into the agent OR the
  toolVectorStore wrapper.
- Loader connects to splitter via `ai_textSplitter`.
- The Chat Trigger path is the webhook URL `.../webhook/<path>/chat` (POST).
- toolVectorStore is a WRAPPER — it never embeds; the underlying
  vectorStoreQdrant owns the real embedding wiring.

## Hard-won parameter facts
- Qdrant collection name param is `qdrantCollection` (not `collectionName`) on
  `@n8n/n8n-nodes-langchain.vectorStoreQdrant`. The "Qdrant Retrieve" node is a
  second vectorStoreQdrant with mode=retrieve and the same collection.
- Model nodes are `@n8n/n8n-nodes-langchain.lmChatNvidia` / `lmChatOpenAi` —
  they DO bind a credential (nvidiaApi/openAiApi), and the P5 credential rule
  requires it (they are NOT in the no-cred allowlist).
- Split defaults: chunkSize 1000, chunkOverlap 0. Larger overlap helps
  cross-chunk answers but costs tokens/points.
- Every vector store must have an embeddings node wired in — a store with no
  embeddings is a runtime error, caught by RAG gate R1.

## Mandatory gate before deploy
Run `venv/bin/python scripts/build_gates_pipeline.py <workflow.json> --no-hitl`
and require VERDICT READY_FOR_DEPLOYMENT (exit 0). The RAG stage (3.45) checks:
  R1 FAIL  store without embeddings wired (ai_embedding)
  R2 WARN  collection name empty/placeholder
  R3 FAIL  dangling ai_vectorStore / ai_retriever refs
  R4 WARN  Qdrant upsert via POST (must be PUT) on /points
  R5 WARN  NVIDIA embeddings call without input_type
  R6 WARN  document loader present but no text splitter

## Testing live
1. Ingest once (run the Drive trigger, or a manual/one-time branch).
2. Verify the collection: `venv/bin/python scripts/rag_query.py --collection <name> --query "..."` — top hits with scores.
3. Activate the workflow and POST to the chat webhook: `POST <n8n>/webhook/<path>/chat` with `{"sessionId": "t1", "action": "sendMessage", "chatInput": "What was Apple's Q1 2024 revenue?"}`.
4. Confirm the agent answer cites the ingested source (grounded, not hallucinated).

## Failure modes
- "missing field `ids`" on upsert => used POST instead of PUT on /points.
- Store node shows red "no embeddings" => ai_embedding edge missing.
- Agent answers from general knowledge => retriever returned 0 hits; check the
  collection name matches, embeddings dimension matches the Qdrant vector size,
  and the doc was actually split+ingested (query rag_query first).
- NVIDIA 4xx on embeddings => missing `input_type` (passage/query) or batch > 2.

## Output contract
Report: collection(s) + point counts, chat webhook path, wiring summary
(embeddings->store, store->agent), gate verdict, and one live QA exchange.
