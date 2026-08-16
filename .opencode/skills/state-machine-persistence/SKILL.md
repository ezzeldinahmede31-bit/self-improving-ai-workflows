---
name: state-machine-persistence
description: "Design n8n automations as recoverable state machines: persist multi-turn or long-running state (conversation context, job progress, dedupe keys) to Supabase, Redis, or a file DB so nothing is lost when webhooks/executions fail or restart. Use when building multi-turn chat, batch jobs, or any stateful automation."
---

# State Machine Persistence

Prevents data loss across executions and enables resumable, idempotent automations.

## Decision tree for where to store state
- Low volume / single node instance → **file DB** at a path inside the n8n data
  volume (e.g., `/home/node/.n8n/state.json`). Read via Code node `fs`, write atomically (write tmp + rename).
- High volume / multi-user / concurrent → **Redis** (n8n built-in or external). Use
  a dedicated key per chat/user: `chat:{telegramUserId}`.
- Ideally → **Supabase**/Postgres when available: table with
  `id, key (unique), payload jsonb, updated_at`.

## Persist these always
- Multi-turn conversation context (user id, last step, extracted params).
- Dedupe keys (domain, email hash) so repeats do not re-insert.
- Job progress (processed_count, current page/cursor) for long batch exports.
- Retry-safe cursor for pagination/API loops.

## Pattern: write-behind with and-then
1. On state change: write new state first (durable), THEN do side effect
   (send message / insert row). So a crash never loses the intent.
2. On read: tolerate missing state (default {}) and stale state (validate schema/version).
3. Use atomic file writes: write `state.json.tmp` then `rename` to `state.json`.
4. For Redis: `HSET`/`SET` with TTL for session contexts; JSON serialize the payload.

## Idempotency keys
- Compute a stable key per unit of work (e.g., `sha256(email|domain|date)`).
- Before insert: lookup key; if exists → skip (log `duplicate`).
- Store key with a `processed_at` timestamp for analytics.

## Multi-turn chat (Telegram/WhatsApp) specifics
- Key = chat id. Payload = {step, params:{country,size,limit}, history:[...]}.
- On each message: load state, run intent parser, update state, render next prompt.

## Acceptance checklist
- [ ] State write happens BEFORE irreversible side effects.
- [ ] Reads tolerate missing/stale state without crashing.
- [ ] Dedupe keys effective across executions (not per-run).
- [ ] File writes are atomic (tmp + rename).
- [ ] Job can resume after failure from last known cursor/count.