---
name: n8n-credential-security-guard
description: "Prevent ANY API key, secret, token, or password from being written into n8n node parameters, expressions, or Code-node source. Use ONLY whenever generating or editing n8n nodes that need authentication (HTTP, Telegram, OpenAI, Stripe, etc.). Forces exclusive use of pre-registered n8n Credential IDs."
---

# n8n Credential Security Guard

Zero API keys inside workflow JSON. EVER. This is a hard rule.

## The Rule
- Every credentialed node (HTTP, Telegram, OpenAI, Postgres, Redis, Supabase, etc.)
  MUST reference an existing n8n credential by `id` + `name` in its `credentials`
  object — NEVER inline the sensitive value.
- NO field named `apiKey`, `token`, `password`, `authorization` (with inline value),
  or `headers` containing a real secret may appear inside node `parameters` or `jsCode`.
- Code nodes that reach authenticated APIs MUST use injected credential properties
  (e.g. `const creds = await this.getCredentials('httpHeaderAuth')`) — NOT literals.

## Correct node shape
```json
{
  "type": "n8n-nodes-base.httpRequest",
  "credentials": {
    "httpHeaderAuth": {
      "id": "a1b2c3",
      "name": "My API Header Auth"
    }
  },
  "parameters": {
    "url": "https://api.example.com/v1/...",
    "options": {}
  }
}
```

## Pre-write checks (mandatory)
1. BEFORE adding any credentialed node, call n8n MCP `n8n_manage_credentials` with
   `action: list` and pick an EXISTING credential id + name.
2. If none exists: DO NOT invent one — report to the user which credential type is
   needed (e.g. "Telegram API credential") and pause until it is created in n8n UI
   or via `n8n_manage_credentials` create, then reference only its id.
3. Verify the credential type string matches the schema for that node (e.g.
   `telegramApi`, `oAuth2Api`, `httpHeaderAuth`).

## Forbidden patterns (scan every emitted JSON)
- `"apiKey": "actual-secret"`, `"token": "actual-secret"`, `"password": "..."`,
  `"secret": "..."`, `Bearer <key>`, `sk-...`, `nvapi-...`, `ghp_...`
- A Code node JS containing a literal key assignment (`const KEY = '...'`).
- Hardcoded credentials in pinnedData or mock payloads (use placeholders only).

## What to do instead
- Referential credentials: `{ "httpHeaderAuth": { "id", "name" } }`
- For test/demo values: put `YOUR_API_KEY`, `YOUR_TOKEN` placeholders and a node
  Note instructing the user to wire the real credential in the n8n UI.

## Acceptance
- [ ] No secret literal in the workflow JSON (scan aimed).
- [ ] Every credentialed node points to an existing credential id.
- [ ] Report to user: "Node X reuses credential 'Y' (#id)".