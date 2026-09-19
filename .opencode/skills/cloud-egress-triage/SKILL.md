---
name: cloud-egress-triage
description: "Diagnose any cloud endpoint that resets, refuses, or hangs from this box: the egress ladder (local stack, DNS, TLS handshake, proxy env, control endpoint, provider dashboard, support packet). Use when an API resets connections, a managed database is unreachable, webhooks fail only from this host, or you must prove whether the fault is local egress or provider side. Pairs with qdrant-production-readiness, n8n-deployment-ops-guard, sre-incident-response."
---

# Cloud Egress Triage

"Connection reset" is a symptom with six possible owners. Eliminate in order.

## Sources (adopted baselines)

- "The Site Reliability Workbook" (Google, O'Reilly): structured
  troubleshooting, alerting on symptoms vs causes, incident state docs.
- Qdrant official production docs + this workspace's live 104-reset case
  (2026-09-19) as the reference elimination run.

## 1. The ladder (stop at first positive)

1. Local stack: port open? (`socket.connect_ex`), right scheme (HTTPS-only
   endpoints reset plain HTTP), correct header shape (e.g. `api-key` vs
   `Authorization`)? Eliminate client bugs FIRST with the official client lib.
2. DNS: resolve the host from this box. Stale/poisoned resolver fails here.
3. TLS handshake: `openssl s_client -connect host:443` — proves TCP+TLS reach
   the provider independent of any app header. Handshake OK + app reset =
   app-layer rejection (auth/WAF/shape), not network.
4. Proxy env: `http_proxy/https_proxy/no_proxy` set on this box? A proxy that
   does not cover the target region blackholes traffic silently.
5. Control endpoint: hit a DIFFERENT endpoint in the same region/provider
   (docs page, status API). Control works + target fails = target-side
   (paused cluster, deleted resource, IP allowlist). Both fail = local egress
   or provider-wide (check status page).
6. Dashboard + support packet: provider console state, timestamps, source IP,
   full error text, elimination log of steps 1-5. Never rotate keys before
   step 6 — rotation without diagnosis is theater that can break working
   clients.

## 2. Decision table

- Steps 1-4 fail → local fault, fix on the box.
- Step 5 splits → target-side (dashboard/allowlist/billing-pause) or egress.
- All local green + dashboard green → provider support with the packet.
- Flaky/intermittent resets under load → suspect concurrency/timeout
  (see stability-patterns-production), not credentials.

## Worked case (Qdrant Cloud, 2026-09-19)

Raw urllib AND official qdrant-client 1.19.1 → `[Errno 104] reset by peer` on
`get_collections`. Eliminated through step 4 (client-side clean, lib freshly
installed). Remaining: step 5/6 — owner checks Cloud dashboard + regional
reachability. Key rotation explicitly NOT done (would be theater).

## Verification

Endpoint answers its health/collections call, or a support ticket exists with
the full packet and a case id. "It works from my laptop" is not verification —
verify FROM the host that runs the automation.
