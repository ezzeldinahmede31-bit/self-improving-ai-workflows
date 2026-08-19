---
name: docker-deep-dive
description: Applies Docker Deep Dive (Nigel Poulton) to containerized automation: containers are just processes with their own namespaces, and images are layered filesystems made of read-only layers with a thin writable layer. Covers images, containers, registries, networks, volumes, and the Dockerfile habits that produce small immutable images. Use when the user says 'containerize this', 'write a Dockerfile', or 'debug my container'.
---
# docker-deep-dive

Nigel Poulton's Docker Deep Dive teaches containers from first principles: a container is a process with its own namespaces and cgroups, and an image is a stack of read-only layers with a thin writable layer. Use this skill to design, build, debug, and secure the containers that run the automation stack, including n8n itself.

## Core principles
- Containers are not virtual machines: they share the host kernel, so isolation comes from namespaces (process, network, mount, PID, user) and limits come from cgroups.
- An image is a layered filesystem; each Dockerfile instruction adds a read-only layer, so build once and reuse layers across images.
- Containers are immutable and disposable: never patch a running container, rebuild the image and recreate it.
- The container lifecycle is create, start, pause, stop, and delete; data that must survive lives in named volumes, not in the container filesystem.
- Small images are a security and performance feature: fewer layers, smaller attack surface, faster pulls.
- Isolation is thin by design: namespaces hide resources and cgroups limit them, but the kernel and devices remain shared.
- The runtime only orchestrates; the operating system underneath must still be patched and hardened.

## Key patterns
- Minimal base images (distroless or scratch-style) built with multi-stage builds: compile in one stage, copy only the artifact into the final stage.
- One process per container, with that process as PID 1 so signals and zombie reaping behave correctly.
- A .dockerignore file to keep the build context small and to keep secrets out of layers.
- Layered caching in CI: order instructions from least to most changeable so cache hits stay high.
- Named volumes for stateful data, bind mounts for development only, and no important data on the writable layer.
- A HEALTHCHECK instruction so orchestrators know when a container is actually ready.
- Immutable tagging: use descriptive, pinned tags (and digests for production) so deploys are reproducible.

## Applying this to n8n/automation/code
- Run n8n as a pinned image tag with a healthcheck against /healthz so Docker restarts a hung instance automatically.
- Keep all n8n state (database data and the encryption key) in a named volume so an upgrade is a simple image swap.
- Give each automation worker its own container with CPU and memory cgroup limits so one runaway workflow cannot starve the host.
- Use multi-stage builds for custom n8n community-node images to ship only the node modules and the base app.
- Write logs to stdout and let the runtime collect them instead of writing log files inside the container.
- Add container labels for service, environment, and workflow so monitoring can group and trace containers.

## Hard rules
- Never run a container as root when a non-root user works.
- Never bake secrets into an image layer; inject them at runtime via environment or secret mounts.
- Never trust an unverified image; pin digests and scan images before production use.
- Always set an explicit restart policy and resource limits on every container.
- Never mount the Docker socket into an untrusted container.

## Pairs with
infrastructure-as-code, kubernetes-operations, immutable-infrastructure, cloud-native-patterns, release-it-production-hardening
