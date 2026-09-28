---
name: egress-firewall
description: "Runtime egress firewall skill (private/metadata IP walls, all-answers DNS check, domain allow-list, scheme/port policy). Use before any outbound fetch, when a URL comes from untrusted input, or when public internet needs explicit opt-in. Trigger phrases: 'check this URL', 'egress policy', 'SSRF runtime guard', 'فحص الوجهة'."
---

# Egress Firewall (Runtime Destination Validation)

Code: `egress_firewall.py` (stdlib only). Static scans catch hardcoded
bad URLs; this guards the RUNTIME path: `check_url(url, policy)` right
before use. Walls: loopback, link-local (metadata scope), multicast,
reserved, private ranges (v4 + v6 ULA), metadata hostnames, userinfo
smuggling, off-policy schemes/ports. DNS names resolve to ALL answers
and every answer is checked. Domain allow-list is suffix-based;
public internet needs explicit opt-in.

## When to use

- Any fetch of a URL from agent output, user input, or tool results.
- Webhook destinations, callback URLs, redirect targets.
- Staging-vs-production destination separation.

## Honest limit

DNS rebinding (clean now, hostile later) cannot be fixed at check
time — re-check per connect for long-held connections (the injectable
`resolve` hook exists for exactly this).

## Verification

- `tests/test_p0a_egress.py` green (opt-in, allow-list, mixed-answer
  trap, literal private IP, loopback/metadata, userinfo, scheme/port,
  unresolvable).
- No fetch helper in new code calls the network without passing here.

## Pairs with

`agent-sandbox` (docker tier has no network at all), `policy-engine`,
`webhook-trigger-hardening`, `build-gates-pipeline`.
