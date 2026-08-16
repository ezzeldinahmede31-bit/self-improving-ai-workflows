---
name: n8n-error-boundary-architect
description: "Automatically add error handling to every n8n workflow: Error Trigger nodes, Continue On Fail with error branches, and exponential-backoff retry strategies. Use ONLY when constructing or reviewing n8n workflows, to guarantee graceful failure handling instead of a broken canvas."
---

# n8n Error Boundary Architect

Every workflow MUST ship with defensible error handling. No workflow without an
error branch is considered complete.

## Mandatory additions per workflow
### 1. Error Trigger branch
- Add an `n8n-nodes-base.errorTrigger` node.
- Wire it into an error-handling sub-path: e.g., `Error Trigger → Format Error → Notify (Telegram/Email/#errors channel)`.
- The message includes: workflow name, failing node, error message, run URL if available.

### 2. Continue On Fail (per risky node)
- For nodes that fetch external data (HTTP, Webhook trigger, Telegram receive,
  LLM, any paid API) enable `continueOnFail: true`.
- After such a node, split with an IF node on `error` metadata / `$json.error`
  so normal data flows forward and failures flow to the error path.
- Do NOT enable Continue On Fail on transformation/code nodes where a failure is
  a hard bug that must surface loudly.

### 3. Retry strategy (exponential backoff)
For each HTTP/API node (not idempotent-restricted), encode in the request:
- Backoff: first retry after 5s (HTTP 429 / 5xx), then 15s, then 45s, max 3 retries.
- On 429 specifically, respect `Retry-After` header when present.
- Never retry 4xx (client errors) except 429.

## Node wiring pattern
```
[Trigger] → [API Node cont.onFail] → IF (success?) ─yes→ [next main node]
                                          │
                                          └─no→ [Error handler subpath]
```
## Concurrency / timeout notes
- Set `requestOptions.timeout` on HTTP nodes (e.g., 30–60s); no indefinite waits.
- For long loops that retry, add a Wait node with a cap so the workflow can't spin forever.

## Acceptance checklist
- [ ] Error Trigger exists and routes to a notification path.
- [ ] External-data nodes carry `continueOnFail` and an IF branch.
- [ ] API calls have explicit timeout + backoff (5s→15s→45s, max 3).
- [ ] No infinite retry loop possible.
- [ ] Error notifications include traceable info (node name + message).