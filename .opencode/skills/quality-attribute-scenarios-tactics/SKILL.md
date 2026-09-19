---
name: quality-attribute-scenarios-tactics
description: "Turn vague -ilities into testable scenarios and proven tactics: availability, performance, security, modifiability. Use when the user says 'non-functional requirements', 'quality attributes', 'ATAM', 'tactics', 'how to measure scalability', 'المتطلبات غير الوظيفية', or needs architecture evaluated against measurable scenarios."
---

# Quality Attribute Scenarios & Tactics

Distilled from Bass et al *Software Architecture in Practice* (quality
attribute scenarios, tactics, ATAM), Rozanski & Woods viewpoints and
perspectives, *Software Architecture: Foundations, Theory, and Practice*.
"-ilities" without scenarios are horoscopes.

## The protocol

1. **Scenario-ize every -ility.** Stimulus + environment + response +
   measure. "System is scalable" becomes "100K concurrent checkouts at
   peak sustain p99 < 800ms with zero errors" — stimulus, environment,
   response, measure. No measure = not a requirement, a wish.
2. **Pick tactics per attribute.**
   - Availability: ping/echo, heartbeat, active redundancy, spare,
     checkpoint/rollback, graceful degradation.
   - Performance: control demand (rate-limit, prioritize), manage
     resources (cache, pool, schedule), bound execution (deadlines).
   - Security: authenticate, authorize, encrypt, audit, limit exposure,
     verify input at the boundary.
   - Modifiability: semantic coherence, anticipate changes, generalize
     the module, restrict dependencies, refactor-guard with fitness
     functions.
   - Testability/deployability: record/playback, sandboxing, CI gates,
     blue-green/canary, feature flags.
3. **ATAM-lite evaluation.** One workshop: utility tree (attributes ->
   scenarios, prioritized), architectural approaches mapped to
   scenarios, then risks / sensitivity points / trade-offs per approach.
   Sensitivity point = one parameter that flips a scenario's verdict.
4. **Viewpoints check.** Development, runtime, deployment, operational,
   security viewpoints — each scenario must be answerable in its
   viewpoint, or the docs are incomplete (`c4-architecture-communication`).
5. **Fitness-function lock-in.** Every scenario's measure becomes an
   automated check where possible (`fitness-function-engineering`).
   Scenarios decay into wishes within two quarters without automation.

## Verification

Quality pack ships with: scenario table (stimulus/environment/
response/measure), tactic per scenario, ATAM-lite risks + sensitivity
points + trade-offs, viewpoint coverage, automated measures. Vague
-ilities = PARTIAL, name which.

## Pairs with

- `fundamentals-of-software-architecture` (characteristics),
  `c4-architecture-communication` (viewpoints in docs),
  `fitness-function-engineering` (automated measures),
  `architecture-decision-framework` (record approach choices),
  `system-design-production-blueprint` (phase 1 requirements),
  `security-review` (security scenarios).
