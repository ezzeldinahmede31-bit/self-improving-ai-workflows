---
name: security-engineering-threat-modeling
description: "Applies Ross Anderson's Security Engineering to design systems that resist real adversaries: threat modeling (who attacks, why, with what resources), fail-safe defaults, the economics and incentives of security (attacker ROI), cryptography used correctly (never invent, use vetted schemes), protocol and distributed-systems security, and organizational/incentive failures. Use when the user says 'threat model', 'design this securely', 'who would attack this and why', 'security engineering', 'incentives and security', 'fail closed vs fail open', 'cryptography in practice', 'secure protocol design', 'security at scale', 'what should we defend first', or when a system needs security baked in, not bolted on. Pairs with: frontier-red-team-auditor, web-security-browser-internals, security-review, zero-trust-modular-decomposer."
---

# Security Engineering — Threat Modeling & Resilient Design

Anderson's reference is the anti-checklist book: security is a *design discipline*
grounded in how real adversaries behave and in the economics of attack and defense.
Every security decision is a trade-off against cost, usability, and incentives.

## When to use

- Designing any system, protocol, or distributed service from the start (security
  must be in the architecture, not added later).
- Deciding what to defend first when resources are limited.
- Reviewing a design where security was an afterthought or a "must be secure"
  blanket statement.

## The method

### 1. Threat model first (the five questions)
- Who are the adversaries? (casual, insider, professional, nation-state)
- What assets do they want, and what is each worth?
- What is their incentive / ROI for the attack? (If the defense costs more than the
  asset, the defense wins by economics.)
- What attack surface do they have? Enumerate entry points and trust boundaries.
- What happens on breach — can you detect, contain, and recover?

### 2. Fail-safe defaults
- Default to deny: unauthenticated = rejected, unknown input = invalid, unknown
  state = locked down. Open by default is a design bug.
- Design so the *failure mode is safe*: when a mechanism fails, it must fail closed
  (no access) not open (no protection).

### 3. Cryptography done right
- Never invent or modify crypto; use vetted libraries and standard schemes.
- Keys are assets: manage them with a key hierarchy (key-encryption keys), rotate,
  and never log them (see the workspace rotation-gate work in `security-review`).
- Use the primitive for its purpose: encrypt for confidentiality, HMAC for
  integrity, signatures for authenticity — and state which you are using.

### 4. Protocol and distributed-systems security
- Assume the transport is hostile: authenticate peers, protect messages in transit
  (TLS), and replay-protect where it matters (timestamps, nonces, sequence numbers).
- Every trust boundary must authenticate and authorize explicitly; cross-boundary
  calls carry credentials scoped to the minimum.
- Consider availability attacks (resource exhaustion) as security issues, not just
  integrity/confidentiality.

### 5. People and process (the often-missed layer)
- Incentives drive behavior: a security control that blocks a legitimate workflow
  will be bypassed. Design controls that fail loudly and are easy to do right.
- Include incident response in the design (what to detect, who is on call, how to
  roll back) — recovery is part of resilience.

## Verification
- A written threat model exists with named adversaries and the chosen defenses per
  entry point.
- Fail-safe default is demonstrated: remove credentials / hit the unknown input and
  confirm deny-by-default behavior.
- A security review pass (see `security-review` / `frontier-red-team-auditor`)
  found no high-severity finding left open.

## Pairs with
- `frontier-red-team-auditor` — adversarial testing of the threat model.
- `web-security-browser-internals` — the browser-side primitives layer.
- `security-review` — systematic code-level verification.
- `zero-trust-modular-decomposer` — isolate trust boundaries in the module layout.