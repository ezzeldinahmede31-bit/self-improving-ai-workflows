---
name: n8n-mcp-workflow-builder
description: "Forces the LLM to build n8n workflows locally using the n8n MCP Server schema cache, bypassing external API documentation fetching and eliminating hardcoded keys. Use whenever generating, validating, or deploying n8n workflows."
---

# N8N MCP LOCAL WORKFLOW BUILDER

## DIRECTIVE
You must never attempt to perform direct external REST API calls or read raw
third-party Swagger docs during workflow generation. Instead, you interact
natively through the local `n8n-mcp-server` toolset using schema caching and
pre-registered credential references.

## PROTOCOL EXECUTION RULES

1. **ZERO EXTERNAL API FETCHING:**
   - Do NOT fetch or inspect external API docs for platforms (e.g., Telegram,
     Supabase, Stripe, OpenAI).
   - ALWAYS invoke the local MCP tool `n8n_get_node_schema(node_type)` to fetch
     node specifications, parameters, and inputs directly from the local schema
     cache.
   - When unsure which node exists, call `n8n_search_nodes(query)` first instead
     of guessing type strings.

2. **CREDENTIAL ID ISOLATION:**
   - NEVER request, expose, or inject real API Keys, Secrets, or Access Tokens.
   - Query available credentials using `n8n_list_available_credentials()` and
     reference them strictly via their `credentialId` or environment variable
     placeholders (`$env.VARIABLE_NAME`).
   - If a required credential type does not exist, PAUSE and tell the user which
     credential type to create — do not invent an id.

3. **MANDATORY EXECUTION PIPELINE:**
   Step 1: `n8n_get_node_schema` -> Inspect node parameters locally.
   Step 2: Construct the JSON AST payload adhering strictly to n8n Schema v2.
   Step 3: `n8n_validate_workflow_json` -> Run pre-flight syntax and connection checks.
   Step 4: `n8n_deploy_workflow` -> Deploy directly to the local n8n instance (`http://localhost:5678`).
   Step 5: `n8n_execute_and_get_result` -> Perform dry-run and capture execution logs.

## OUTPUT CONTRACT
Report after each build:
- Nodes created, with type + typeVersion confirmed via schema call.
- Credential references (id + name only, never values).
- Validation result (errors = 0 required before deploy).
- Dry-run execution status and any captured logs.