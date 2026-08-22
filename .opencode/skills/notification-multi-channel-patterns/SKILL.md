---
name: notification-multi-channel-patterns
description: "Delivers alerts across email/chat/SMS/push with per-channel formatting. Use for alerts."
---

# Multi-Channel Notification Patterns

One message rarely fits all channels.

## Workflow
1. Map severity -> channel set.
2. Per-channel renderer from canonical payload.
3. Respect quiet hours except critical.
4. Route by preference/on-call, track delivery.

## Core Rules
- Chat for awareness, SMS/phone for critical, email for record.

## Pairs with
- `telegram-bot`, `slack-bot`, `scheduled-digest-aggregation`
