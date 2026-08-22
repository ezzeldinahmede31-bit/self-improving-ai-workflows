---
name: webhook-trigger-hardening
description: "Secures inbound webhooks with HMAC, timestamp freshness, replay defense, schema validation. Use for public endpoints."
---

# Webhook Trigger Hardening

Public webhook = open door unless verified.

## Workflow
1. Compute expected HMAC over raw body via provider scheme.
2. Reject stale timestamps outside freshness window.
3. Validate schema before any side effect.
4. Ack fast, process async if handler > few seconds.

## Core Rules
- Bind verification to exact bytes received.
- Never trust headers alone.

## Pairs with
- `webhook-automation`, `web-security-browser-internals`, `security-and-hardening`
