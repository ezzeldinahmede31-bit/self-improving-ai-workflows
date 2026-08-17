---
name: kubernetes-operations
description: "Applies Kubernetes Up & Running (Beda, Hightower, Burns) to deploy and operate containerized workloads: the Kubernetes object model (pods, deployments, services, ingress, configmaps, secrets, namespaces), controllers and desired-state reconciliation, rolling updates and rollbacks, storage, autoscaling, multi-container patterns, and observability and security fundamentals. Use when the user says 'deploy this to Kubernetes', 'kubernetes', 'k8s', 'write a deployment manifest', 'pods and services', 'ingress', 'rolling update', 'autoscale', 'helm', 'namespaces', 'kubectl', 'container orchestration', 'why is my pod not ready', or when running n8n or any service on Kubernetes. Pairs with: n8n-self-hosting, devops-automation, infrastructure-as-code, cloud-native-patterns."
---

# Kubernetes Up & Running

Kubernetes runs on one core idea: **desired state**. You declare what should exist;
the controllers continuously reconcile reality toward that declaration. Design and
debug everything through that lens.

## When to use

- Deploying or operating any workload on Kubernetes.
- Writing or reviewing manifests (pods, deployments, services, ingress, stateful
  sets, jobs).
- Diagnosing pods stuck pending/crash-looping, or rollout failures.

## The mental model

- **Declarative, not imperative**: every object is a YAML/JSON declaration of desired
  state. `kubectl apply` makes reality match. Never "fix by hand" a live object
  permanently — change the manifest.
- **Controllers reconcile**: a Deployment's controller watches, and when a pod
  drifts (crashes, killed) it recreates to match the desired replica number. Health
  matters: define liveness (restart when dead) and readiness (traffic only when
  ready) probes.

## The objects you will use
- **Pod**: the atomic unit. You almost never create pods directly — you use a
  controller.
- **Deployment**: stateless replica management — rolling updates with `maxUnavailable`
  / `maxSurge`, rollback (`kubectl rollout undo`), and self-healing.
- **StatefulSet**: stable identity + stable storage for stateful services.
- **Service**: stable network endpoint (ClusterIP, NodePort, LoadBalancer) over pods.
- **Ingress**: host/path-based routing + TLS at the edge.
- **ConfigMap / Secret**: configuration and secrets as objects, injected via env or
  volume. Secrets in git are a defect (see `infrastructure-as-code`).
- **Namespace**: isolation and policy boundaries for teams/environments.
- **Job / CronJob**: batch and scheduled work.

## Operating discipline
- Use resource requests AND limits for CPU/memory; without them, scheduling and
  protection are guesswork.
- Rolling updates need a safe budget: don't take the whole app down at once; keep
  `minReadySeconds` so unhealthy versions do not "succeed".
- Use Horizontal Pod Autoscaler on measured metrics with sane min/max, and
  Vertical Pod Autoscaler only where supported.
- Multi-container pod patterns: sidecar (logging, proxy), adapter, ambassador —
  share the pod's network and storage, keep the main container simple.

## Observability and security
- Collect logs and metrics from every pod; readiness/liveness probes are part of
  it, but so are request-level metrics.
- Least privilege: service accounts with narrow RBAC, network policies to restrict
  traffic, secrets never in images or env logs, and images from trusted registries
  with pinned digests where it matters.

## Verification
- `kubectl get all` shows the desired state; `kubectl rollout status` confirms the
  rollout completed with zero failed replicas.
- A deliberate kill of one pod shows the controller recreating it (the reconciliation
  proof).
- The service returns healthy responses from outside after the deployment.

## Pairs with
- `n8n-self-hosting` — running n8n on this stack.
- `devops-automation` — CI/CD around the cluster.
- `infrastructure-as-code` — defining the cluster and workloads as versioned code.
- `cloud-native-patterns` — the application patterns that run well here.