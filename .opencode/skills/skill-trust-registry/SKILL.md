---
name: skill-trust-registry
description: "Skill trust registry skill (sealed identity/version/hash/permissions/risk store, load verdicts ok/review/unknown/tamper). Use when loading any skill, onboarding a new one, or triaging a modified skill file. Trigger phrases: 'trust this skill', 'skill verdict', 'registry check', 'سجل الثقة'."
---

# Skill Trust Registry (Load Nothing Unknown)

Code: `skill_trust.py` (stdlib only). Each skill resolves to an entry:
id, version, author/source, sha256 of SKILL.md, permission allow-list,
risk tier (low/medium/high), signature, last-verified stamp. The file
is HMAC-sealed; a broken seal fails closed to empty (all unknown).
`check_load()` returns ok / review (high risk needs a human) /
unknown / tamper (hash drift).

## When to use

- Every skill load path should consult this registry first.
- Onboarding: `register()` hashes + stamps + seals.
- Incident: re-verify hashes; tamper verdict quarantines.

## Verification

- `tests/test_p0b_trust.py` green (roundtrip, tamper trap, broken
  seal fails closed, high-risk review, unknown handling).
- No skill loads as trusted without a fresh hash match.

## Pairs with

`supply-chain-security` (hash source), `skill-supply-chain-guard-adapter`
(vetting before register), `find-skills` (gated installs),
`build-gates-pipeline`.
