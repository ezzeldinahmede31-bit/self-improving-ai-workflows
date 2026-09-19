---
name: safe-mode-gating
description: "Ship a global SAFE_MODE kill-switch in every consequential workflow: env-gated If branches around destructive, costly, or external-write nodes so end-to-end tests run without real-world side effects. Use when a workflow sends messages, writes records, charges, publishes, or calls paid APIs and must be testable in production topology without consequences. Pairs with deploy-signoff-governance, human-approval-gates, n8n-error-boundary-architect, eip-workflow-patterns (Control Bus)."
---

# Safe-Mode Gating

Test the live topology with the blast radius off.

## Sources (adopted baselines)

- kspandian32 Enterprise-n8n-Architectures: Global SAFE_MODE toggle across
  outreach, publishing, file moves — env-based If branches bypassing costly
  actions during tests (EIP Control Bus in practice).
- studiomeyer-io/n8n-workflows: opt-in production nodes gated by env vars,
  default-off so imports boot clean; same gating discipline, inverted default.
- EIP Control Bus: steer behavior without edits; separate deployment from
  release.

## 1. Pattern (identical everywhere)

One `Global Config` Set node at the top exposing `safeMode` (from env var,
default TRUE/safe). Before EVERY destructive/costly/external-write node, one
If: `safeMode?` → true branch logs the WOULD-BE action (target, payload hash,
reason) and skips; false branch executes. Naming convention fixed:
`SAFE: <action> bypassed`. No silent skips — every bypass writes an audit line
or it did not happen.

## 2. Coverage rule

Gate ALL of: outbound messages, record writes/deletes, charges/payments,
publishes/posts, paid API/LLM calls above trivial cost, credential-scoped
actions. Read-only probes and internal logs stay ungated (observability must
work in safe mode — that is the point).

## 3. Lifecycle

Default safe on import and in staging. Production flip is a Tier-2 sign-off
item (see deploy-signoff-governance) with the evidence packet. CI asserts:
every node tagged destructive has a safe branch upstream (grep the JSON).
Rehearse the flip quarterly: safe→live→safe on staging, confirm audit lines
then real effects.

## 4. Anti-patterns

Per-node ad-hoc flags with different names (use ONE convention); safe mode
that also mutes observability (blind testing); permanent "temporary" bypasses
(schedule deletion); testing only the safe path and assuming the live path
(shape-parity check: both branches reviewed, live branch executed at minimum
once on staging with fixtures).

## Verification

With safe ON: full execution completes, zero external side effects, audit log
shows every bypass. With safe OFF on staging fixtures: real effects appear
exactly once (idempotency holds). Both runs recorded.
