---
name: n8n-deployment-ops-guard
description: Guards n8n deployment and production operations that gates cannot see. Use after any workflow PUT, after any reboot or reconnect, before live traffic, and when wiring dashboards, probes, or patient-facing contracts.
---

# n8n Deployment Ops Guard

Workflows fail after delivery for reasons no static gate observes: stale
dispatch registrations, dead instances, expired OAuth, inactive error
workflows, dirty probes, and slow or leaky patient-facing replies. This skill
is the operations checklist that runs after the gates pass and before live
traffic flows. Every rule below maps to a real incident with a live proof.

## 1. Publish after every PUT

- n8n 2.30+ separates draft from published. A PUT on an active workflow
  returns 200 `started` with zero executions until the new graph is
  published: deactivate then activate (or restart) after every update, then
  re-probe. A `started` response with no execution row means stale
  registration, never success.

## 2. Survive reboots and reconnects

- n8n does not reactivate workflows after a host reboot. Keep a reactivate
  script (healthz wait plus activate-by-ID) on `@reboot` cron, and verify
  with one status call per workflow after every restart.
- Container recreations drop network memberships and env flags. After any
  recreate, verify: shared-network attachment (Redis reachability from inside
  n8n, never localhost assumptions), required env flags, and the real
  instance version. Never trust validator or model-list suggestions above the
  installed version; only live responses prove a model, node version, or
  credential binding.

## 3. Credential and integration health

- OAuth tokens expire silently and poison every downstream verdict (all slots
  read `taken`, all lookups read empty). Check integration health directly
  (list-window probe) before any race or load test, and keep the
  error-means-unknown path separate from the busy path: API failures release
  unverified claims and answer honestly, never `taken`.
- The error workflow must be attached AND active, with the real execution
  payload shape. An inactive error workflow is equivalent to none — prove it
  once with a throwaway failing workflow, then delete the throwaway.

## 4. Probe hygiene

- Probes use synthetic chat ids only, one fresh id per tap-style test
  (fixed ids get eaten by dedup), and cleanup deletes by chat attribution so
  real user rows survive. Test side effects (events, keys, tallies, pings)
  are zeroed right after the run: empty calendar, clean keys, zeroed tallies,
  deleted probe executions. Nothing scheduled or pending may remain.

## 5. Latency contract

- Acknowledge in under two seconds (typing indicator or placeholder), then
  deliver the final reply by editing the placeholder in place, with a plain
  fallback send and an owner alert only when both legs fail. Cap model turns
  structurally (small maxTokens) and cap hangs with executionTimeout.

## 6. Reply quality contract

- Agent terminals never send raw. A usability gate (reply length plus leak
  pattern) routes empty, truncated, deliberation, or gibberish output to a
  deterministic apology plus staff ping.
- Patient-facing contract strings live in the target language at the source
  (sub-workflow replies included); the agent never translates on the fly.
  Keep machine data in whatever language the model handles best and let the
  contract carry the patient words. Attribution footers stay off on every
  user-facing send node.
- Prices render digit by digit from the live catalog read; day and hour
  facts ship from a bilingual source and get proven on a fresh session, so a
  stale memory echo cannot survive a prompt fix.

## 7. Data lifecycle and delete safety

- Durable facts (visits, invites) live in an append-only table; volatile
  keys (locks, dedup, sessions, tallies) live in Redis with explicit TTLs.
  A cleanup lane never deletes a record before its durable write is proven
  (Visit Logged gate); failures park for retry, never for loss.
- Delete lanes handle the already-deleted tombstone (Google answers deleted
  events with `status=cancelled`, not 404): re-delete reports already-gone
  with frozen tallies, while normal deletes tally exactly once.

## 8. Verification

- Run the gates until READY_FOR_DEPLOYMENT, validate 0 errors and 0
  warnings on the instance, then walk this checklist top to bottom against
  live executions before declaring production. Pairs with:
  gate-first-pass-builder, n8n-runtime-semantics-guard,
  automation-known-issues-compass, n8n-delivery-verification-gate,
  n8n-e2e-test-runner.
