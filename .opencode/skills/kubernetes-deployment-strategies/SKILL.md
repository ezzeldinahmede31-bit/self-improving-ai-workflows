---
name: kubernetes-deployment-strategies
description: Applies the deployment and operations guidance of Kubernetes: Up & Running (Beda, Hightower, Burns): choose and run the right update strategy — rolling, blue-green, or canary — with readiness and liveness probes, resource requests, and safe rollback, so application updates never take the service down. Use when the user says 'deployment strategy', 'rolling update', 'blue-green deployment', 'canary release', 'rollback', 'readiness probe', 'liveness probe', 'update a deployment', 'zero-downtime deploy', 'strategy type', 'maxUnavailable', 'replicas', or when releasing new versions of a service on Kubernetes. Pairs with: kubernetes-operations, infrastructure-as-code, cloud-native-patterns, devops-handbook-flow.
---

# Kubernetes Deployment Strategies

Transfers the update and operations guidance of Kubernetes: Up & Running (Beda, Hightower, Burns) to shipping changes safely: pick the right rollout strategy, wire probes so the platform knows the app is healthy, and roll back without drama.

## When to use
- Releasing a new version of a deployed workload.
- Choosing how aggressive or conservative an update should be.
- Diagnosing failed rollouts and doing safe rollbacks.

## The strategy ladder
1. Rolling update (default): the controller replaces pods gradually; `maxUnavailable` and `maxSurge` tune the pace. Best default for most services.
2. Blue-green: stand up the new version fully, validate, then switch traffic. Good when the old version must stay hot for an instant rollback.
3. Canary: expose the new version to a small fraction of traffic, observe, then widen. Best when traffic-based telemetry is rich.
4. Recreate: acceptable only for jobs or workloads that cannot run two versions simultaneously.

## Probes that make updates safe
- readiness probe gates traffic: a pod that fails readiness is removed from Service endpoints, so a bad new version stops receiving requests.
- liveness probe restarts hung pods.
- Use the readiness probe as the real rollout gate; a deployment can be "done" while every new pod is unready.

## Resource and rollback hygiene
- Set requests/limits so scheduling and eviction behave predictably.
- Record the rollout cause and know the exact command to revert to the prior revision.
- Verify a rollback actually restores traffic before calling it done.

## Verification discipline
- During a rollout, assert that the Service keeps serving (no request failures) across the transition.
- Test rollback on a deliberately broken image and confirm old behavior returns.

## Pairs with
kubernetes-operations, infrastructure-as-code, cloud-native-patterns, devops-handbook-flow.