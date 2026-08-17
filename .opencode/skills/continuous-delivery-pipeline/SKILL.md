---
name: continuous-delivery-pipeline
description: "Applies Humble & Farley's Continuous Delivery to automation and software delivery: build the deployment pipeline (commit -> build -> automated tests -> staging -> production) with every commit a release candidate, configuration in the environment, deployment scripts as executable documentation, and zero-downtime release patterns (blue-green, canary, feature flags, rolling). Proves that 'done' means deployed and verified, not just merged. Use when the user says 'continuous delivery', 'deployment pipeline', 'CI/CD', 'blue-green', 'canary', 'feature flag', 'zero downtime', 'release candidate', 'Humble Farley', 'deploy to production', 'staging', 'rollback', or when software must ship fast without breaking. Pairs with: devops-handbook-flow, infrastructure-as-code, n8n-workflow-lifecycle-official, build-gates-pipeline."
---
# Continuous Delivery Pipeline (Humble & Farley)

Humble & Farley's thesis: software is releasable at the push of a button because EVERY commit goes through an automated pipeline that ends with a deployable artifact verified in a staging-like environment. 'Done' means deployed and verified - not merged.

## The Deployment Pipeline (mandatory shape)

```
Commit -> Build -> Unit tests -> Integration tests -> Staging/acceptance -> Production (zero-downtime) -> Verify
```

1. **Every commit is a release candidate.** If it reaches the end, it ships.
2. **Automated tests gate each stage** - the pipeline is the test runner, not a human.
3. **The artifact is built once and promoted** - no rebuild in production (build once, promote the same binary/JSON).
4. **Staging mirrors production** - same config, same services, same data shapes, or the pipeline is lying.
5. **Release is a repeatable script** - deployments are executable documentation, not a wiki page.
6. **Rollback is as easy as forward** - the same pipeline deploys the previous artifact.

## Zero-Downtime Release Patterns

- **Blue-green**: two environments; switch traffic after the new one passes checks. Instant rollback = switch back.
- **Canary**: send a small percentage of traffic to the new version, watch errors, then ramp. Best for risky changes.
- **Feature flags**: ship the code dark, toggle the feature at runtime. Decouples deploy from release.
- **Rolling**: update nodes incrementally; old and new run together briefly.

## Pipeline Anti-patterns (severity)

- **A1 - 'It works on my machine'** (HIGH): No pipeline; manual deploy steps. Fix: script it, artifact once.
- **A2 - Test environment drift** (HIGH): Staging differs from production. Fix: same config and data shapes.
- **A3 - Rebuild in production** (HIGH): Building the artifact at deploy time. Fix: build once, promote.
- **A4 - Big-bang release** (MEDIUM): One giant release every month. Fix: small batches, feature flags, frequent deploys.
- **A5 - Manual rollback** (MEDIUM): Rollback is a fire drill. Fix: the pipeline rolls back by deploying the previous artifact.
- **A6 - Environment-specific config in code** (MEDIUM): Connection strings/URLs hardcoded. Fix: configuration lives in the environment.

## Checklist

- [ ] Every commit produces a release candidate through the pipeline
- [ ] Automated tests gate every stage
- [ ] Artifact built once and promoted
- [ ] Staging mirrors production
- [ ] Zero-downtime pattern chosen (blue-green/canary/flags/rolling)
- [ ] Rollback = deploy previous artifact
- [ ] Config externalized to the environment

## Verification

Prove a release end-to-end: commit -> pipeline green -> deploy -> verify live -> rollback works. Run the build gates on the deliverable and require READY_FOR_DEPLOYMENT.
