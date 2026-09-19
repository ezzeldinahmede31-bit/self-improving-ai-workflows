---
name: secure-software-lifecycle
description: "Builds security into every SDLC phase: threat modeling, safe implementation, verification. Use when the user says 'secure SDLC', 'threat modeling', 'attack surface', 'security requirements', 'code review security', 'fuzzing', 'pen test', 'security champions', or when a team needs security as process, not patching."
---

# Secure Software Lifecycle

Distilled from the Linux Foundation secure-development curriculum and SDL
practice: vulnerabilities are cheapest at requirements, priciest in
production — move every control as far left as it can live.

## Purpose

Install a repeatable lifecycle where each phase has named security
activities, owners, and exit criteria.

## The lifecycle (phase: activities -> exit gate)

1. **Requirements.** Security objectives per feature (what must NOT happen);
   compliance obligations mapped to controls; abuse cases written alongside
   use cases. Gate: every user story with trust implications has a paired
   abuse story.
2. **Design.** Threat model per component (STRIDE + attack trees for the
   crown jewels); attack-surface review (every input, connector, and
   privilege boundary listed); crypto/auth choices justified in writing;
   third-party risk assessed (maturity, vuln history, update cadence). Gate:
   model reviewed by someone who did not design the component.
3. **Implementation.** Safe-language defaults and banned-function lists;
   automated gates in CI (SAST, dependency scan, secret scan — blocking, not
   advisory); peer review with a security checklist; security champions
   embedded per team. Gate: zero blocking findings, waivers time-boxed with
   owner.
4. **Verification.** Adversarial testing scaled to risk: fuzzing harnesses on
   parsers/protocols, DAST on running apps, pen test before major releases,
   bug-bounty or vuln-disclosure channel always open. Gate: findings
   triaged by exploitability with SLAs, retest confirms closure.
5. **Release and response.** Hardened configs and signed artifacts; incident
   response plan with roles rehearsed; PSIRT-style intake for external
   reports; post-incident reviews feed new controls back into phase 1.
   Gate: rollback tested, monitoring covers the new attack surface.

## Metrics that steer (not vanity)

- Time from introduce-to-detect per severity (shortening = working).
- Reopen rate (high = broken root-cause process).
- Waiver aging (old waivers = accepted breaches in disguise).

## Verification

Program review checks: phase gates evidenced (not asserted), waiver ledger
current, response drill dated within the quarter. Process without evidence
is theater.

## Pairs with

- `security-engineering-threat-modeling` (design analysis),
  `devops-handbook-flow` (pipeline integration),
  `incident-response-ai-failures-hallucinations` (response),
  `seacord-secure-coding` (implementation rules).
