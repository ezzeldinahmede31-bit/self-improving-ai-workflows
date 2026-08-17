---
name: infrastructure-as-code
description: "Applies Kief Morris' Infrastructure as Code: define all infrastructure (servers, networks, config) as versioned, reviewable, testable code — provisioning, composing, and deploying as a pipeline; immutable servers; environment promotion; and treating infrastructure failures as code bugs. Use when the user says 'infrastructure as code', 'IaC', 'terraform', 'Ansible', 'provision servers', 'immutable infrastructure', 'environment promotion', 'infrastructure pipeline', 'reproduce this server', 'config management', 'drift', 'idempotent provisioning', or when standing up or reproducing environments that must be repeatable. Pairs with: devops-automation, ansible-automation, kubernetes-operations, cloud-native-patterns."
---

# Infrastructure as Code

Morris' thesis: infrastructure is software. If you cannot rebuild an environment
from code in minutes, you do not own it — you are renting a mystery. The practices
make environments reproducible, reviewable, and disposable.

## When to use

- Standing up or changing any server, network, or environment more than once.
- Reproducing a broken environment after an incident.
- Turning a hand-configured box into something a team can change safely.

## The core practices

### 1. Everything is code
- Servers, networks, load balancers, and their configuration live as versioned code
  in the same repo discipline as the app. Every change is a code review; every
  revert is a git revert.
- Secrets are injected at runtime (env/secret store), never stored in the code.

### 2. Define once, reuse everywhere
- Modules: reusable building blocks (a web-server module, a database module) with
  parameters. No copy-paste of a hand-crafted config.

### 3. Immutable servers
- Treat servers as disposable: build a new image/artifact and replace, do not SSH
  in and mutate a running box. Drift is the enemy — an "unexpectedly different"
  server is a bug.

### 4. The pipeline: provision → compose → deploy
- **Provision**: create the base compute/network (Terraform, cloud APIs).
- **Compose**: install and configure the stack on the provisioned base (Ansible,
  images, config management).
- **Deploy**: push the application onto the composed environment.
- Each stage is scripted, idempotent (re-running converges, does not duplicate), and
  safe to run repeatedly.

### 5. Environment promotion
- Promote the same artifacts through dev → staging → prod; environments differ only
  by configuration, never by content. What was tested is what ships.

### 6. Test the infrastructure
- Lint and validate configs in CI, run syntax/plan checks (e.g. `terraform plan`),
  and smoke-test a freshly provisioned environment automatically.

## Verification
- A clean rebuild from code reproduces the environment with zero manual steps
  (the reproduction test).
- Re-running the provisioning scripts is idempotent (no drift, no errors).
- A change is applied via a code review + pipeline, not by editing a live box.

## Pairs with
- `devops-automation` — the pipeline mechanics.
- `ansible-automation` — the compose/configuration layer.
- `kubernetes-operations` — cluster-level declarative infrastructure.
- `cloud-native-patterns` — application patterns that fit disposable environments.