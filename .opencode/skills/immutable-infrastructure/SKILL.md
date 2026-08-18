---
name: immutable-infrastructure
description: Applies Kief Morris' Infrastructure as Code principle of immutability to provision and operate environments: treat servers as disposable, build them from a golden pipeline instead of drifting configuration, promote the same artifact across environments, and replace-in-place rather than patch. Use when the user says 'immutable infrastructure', 'disposable servers', 'golden image', 'pipeline to provision', 'no config drift', 'rebuild instead of patch', 'environment promotion', 'reproducible environment', 'IaC', or when configuration drift or patch-on-patch makes environments unreproducible. Pairs with: infrastructure-as-code, continuous-delivery-pipeline, devops-handbook-flow, ansible-automation.
---

# Immutable Infrastructure

Transfers Kief Morris' immutability discipline to any environment that must be reproducible: provision through a pipeline, never patch a living server, and promote the same artifact from staging to production.

## When to use
- Environments that drift apart because they were configured by hand.
- Deployments that fail because the machine differs from the artifact.
- Teams that cannot reproduce a bug because the server state is a mystery.

## The immutable principle
- A server is a disposable unit; once it is created it is never patched or tuned by hand.
- Any change is a new provisioning run producing a new server, then traffic moves to the new unit.
- Configuration is code; the environment's truth is the repository, not the machine.

## The provisioning pipeline
- Bake the artifact (image, container, package set) in a pipeline that runs the same steps every time.
- Store artifacts immutably and version them; a deploy is a reference to a versioned artifact.
- Run automated verification inside the pipeline so a broken artifact never reaches an environment.

## Environment promotion
- Promote the identical artifact across dev, staging, and production; only configuration values differ.
- Keep the promotion path short and repeatable so production is exercised the same way as earlier stages.
- Guard promotion with gates that require real verification evidence.

## Replacing instead of patching
- Treat a faulty server as failed and replace it; the fix lives in the provisioning code, not in a shell session.
- Keep instance state (logs, metrics) external so a server can be destroyed and rebuilt without data loss.

## Verification discipline
- Reproduce any environment from the pipeline on a clean box and assert the result matches the golden artifact.
- Periodically destroy and rebuild a production-like environment to prove the pipeline, not the patch history.

## Pairs with
infrastructure-as-code, continuous-delivery-pipeline, devops-handbook-flow, ansible-automation.