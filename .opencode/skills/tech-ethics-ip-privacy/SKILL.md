---
name: tech-ethics-ip-privacy
description: "Resolves technology ethics: professional duty, intellectual property, and privacy. Use when the user says 'software ethics', 'ACM code', 'copyright', 'GPL vs MIT', 'patent', 'GDPR', 'data minimization', 'consent', 'algorithmic bias', 'surveillance', or when shipping anything that touches users, data, or others' code."
---

# Tech Ethics, IP & Privacy

Distilled from the OSSU ethics thread (Tavani-style engineering ethics, IP
law for engineers, privacy fundamentals): three lenses every shipped system
must pass — duty to the public, respect for others' work, respect for users'
data.

## Purpose

Make the ethical call explicitly and defensibly before code ships, not after
harm ships with it.

## Lens 1 — Professional duty

- Public safety, welfare, and honesty outrank employer and client interests
  (ACM/IEEE codes agree on the ordering). If you would not defend the
  decision in public with your name on it, do not ship it.
- Competence boundary: decline work you cannot do safely; disclose conflicts
  of interest; never silently lower a safety or quality bar under schedule
  pressure.
- Document the decision and who owned it — accountability needs a name and a
  date.

## Lens 2 — Intellectual property

- Copyright covers expression (code, text, images), not ideas; patents cover
  inventions; trademarks cover identity. Know which one your asset is.
- Licenses are the whole game in software: permissive (MIT/Apache: use with
  attribution, keep notices), copyleft (GPL: distribute derivatives under the
  same terms — understand what "derivative" and "distribution" trigger),
  proprietary (only what is granted). Audit dependencies' licenses before
  release; a single GPL file can relicense your product's obligations.
- Fair use / exceptions are narrow and jurisdiction-specific — get counsel
  for anything load-bearing, never folklore.

## Lens 3 — Privacy

- Collect the minimum data that achieves the purpose; delete on schedule;
  purpose-bind every reuse (new purpose = new consent basis).
- Threat-model the data store: breach impact assessed per field, encryption
  plus access control, anonymization validated against re-identification
  (removing names is not anonymizing).
- Regulatory baselines (GDPR-style): lawful basis, user rights (access,
  correction, deletion, portability), breach notification duty. Design these
  as features, not paperwork.

## Verification

Ship checklist: duty analysis signed, license audit clean with notices
shipped, data inventory with retention + basis per field, deletion path
tested. Any unchecked box blocks release — ethics gates are release gates.

## Pairs with

- `data-privacy-differential-privacy-v2` (technical privacy),
  `bias-fairness-mitigation-strategies` (algorithmic harm),
  `ip-protection-copyright-ai-v2` (AI-era IP), `audit-trail-compliance`.
