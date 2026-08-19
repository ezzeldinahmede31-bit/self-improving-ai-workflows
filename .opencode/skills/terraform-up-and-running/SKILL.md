---
name: terraform-up-and-running
description: Applies Terraform: Up and Running (Yevgeniy Brikman) to infrastructure provisioning: treat every resource as code that is plan-able, reviewable, and reproducible, with a drift-free apply loop. Covers the core workflow, state management, modules, workspaces, and the composition habits that keep terraform DRY. Use when the user says 'write terraform', 'provision infrastructure as code', or 'why did my apply drift'.
---
# terraform-up-and-running

Yevgeniy Brikman's Terraform: Up and Running is the practical manual for infrastructure as code: declare desired state, plan the change, review it, apply it, and let terraform converge drift over time. Use this skill whenever the automation stack or any of its dependencies must be provisioned reproducibly across environments.

## Core principles
- Terraform turns desired-state declarations into real infrastructure through the plan/apply loop; the plan shows every change before it happens.
- State is the source of truth: protect it with locking, back it up remotely, and never edit it by hand.
- Reproducible environments come from modules: build small, composable modules and pin versions, never copy-paste resource blocks.
- Everything is a resource graph; dependencies are inferred from references, so ordering emerges from the code.
- DRY applies to infrastructure too: variables, modules, and workspaces remove duplication.
- Small, frequent applies beat giant rare ones; the plan output makes each change reviewable.
- Never fight the tool: if a manual click creates a resource, terraform will see drift and try to reconcile it.

## Key patterns
- The three-file layout: variables.tf for inputs, main.tf for resources, and outputs.tf for the values consumers need.
- Module composition: general-purpose leaf modules composed into environment modules for dev, staging, and prod parity.
- Remote state backends with locking so two people never apply the same state file at once.
- Workspaces to run one module configuration with different variables for each environment.
- Data sources to import and reuse existing infrastructure instead of recreating it.
- Resource loops and conditionals expressed in the language itself, keeping duplication out of the config.
- The state file as the interface: store it where the whole team can access it safely, with locking enabled.

## Applying this to n8n/automation/code
- Define the n8n host, its database and queue dependencies, volumes, and reverse proxy as one module so the whole stack is reproducible.
- Store the n8n encryption key and every secret as variables backed by a secret store, never in the config files.
- Use outputs to hand the deployment pipeline the instance URL and health endpoint for post-apply verification.
- Pair apply with the build gates pipeline: run plan in the delivery pipeline and fail the build if the plan alters state unexpectedly.
- Use a data source to attach terraform-created infrastructure to workflow tests without manual configuration.
- Keep each environment in its own workspace so test and production runs never share state.

## Hard rules
- Always run terraform plan and review the diff before apply.
- Never commit state files or any state that contains secrets to version control.
- Never hand-edit resources behind terraform's back; import them instead.
- Always pin provider and module versions for reproducible applies.
- Never store plaintext secrets in tfvars or module inputs.

## Pairs with
infrastructure-as-code, immutable-infrastructure, continuous-delivery-pipeline, kubernetes-operations, devops-handbook-flow
