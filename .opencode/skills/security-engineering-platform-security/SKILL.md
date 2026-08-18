---
name: security-engineering-platform-security
description: "Applies the platform-security chapters of Ross Anderson's Security Engineering to harden the environment around an application: privilege separation and least privilege, capabilities, sandboxing and container isolation, the trusted computing base (TCB), network perimeter and firewall reasoning, TLS done correctly, and the economics that decide where defense is worth the cost. Use when the user says 'harden the platform', 'privilege separation', 'least privilege', 'capabilities', 'sandbox', 'container isolation', 'trusted computing base', 'firewall design', 'defense in depth', 'attacker economics', 'platform security', 'secure the host', 'Anderson security engineering', or when an application needs the environment beneath it made attack-resistant. Pairs with: security-engineering-threat-modeling, security-and-hardening, web-security-browser-internals, applied-cryptography-engineering, build-gates-pipeline."
---

# Platform Security

Threat modeling says *who attacks and why*; platform security says *what the
attack can reach*. The platform layer decides the blast radius of any single
compromise, so its design rules are about containment, not just prevention.

## When to use

- Hardening a host, container, VM, or cloud deployment before or during a
  security review.
- Splitting a large service into smaller, less privileged processes.
- Choosing whether sandboxing, containers, or capabilities are worth their
  operational cost for a given risk.

## Privilege separation and least privilege

- Each component runs with the fewest privileges it needs and no more.
- Break a privileged process into smaller pieces so that an exploit in one
  piece cannot inherit the privileges of the others (like a web server split
  from the privileged helper that binds low ports).
- Every privilege a component carries is a liability the whole system pays for.

## Capabilities and access control

- A capability is a reference that itself grants access. Possession of the
  token is the authorization; losing it removes access without a central
  revocation sweep.
- Prefer fine-grained roles and capabilities over one all-powerful account; a
  single superuser key is a single point of total compromise.

## Sandboxing and containers

- Sandboxes and containers shrink what a compromised process can do. They do
  not remove the need to patch, and an escape is always worth assuming in the
  threat model.
- Harden the runtime itself: run as a non-root user, drop unnecessary kernel
  capabilities, read-only root filesystem, and no privileged mounts.
- Keep the host and orchestration control plane as separate trust zones from
  the workloads they run.

## The trusted computing base (TCB)

- The TCB is the set of components that must be correct for the security
  guarantees to hold: kernel, hypervisor, boot chain, and the trusted services.
- Shrink the TCB: the smaller the trusted surface, the fewer components an
  attacker must be locked out of and the fewer places a bug is catastrophic.

## Network perimeter and firewalls

- Perimeter defenses are layered, not absolute. A firewall that allows the app
  traffic is a filter, not a wall; assume traffic can reach the app.
- Use network segmentation as the same idea as privilege separation at the
  network layer: database and secrets networks should be reachable only from
  the services that legitimately need them.

## TLS done correctly

- Always terminate TLS; never accept plaintext secrets over the network.
- Pin certificates where the client can be pinned, validate hostnames, and keep
  cipher suites to modern forward-secure configurations.
- TLS protects the wire, not the endpoints; the platform layer is what makes an
  endpoint worth attacking or not.

## Defense economics

- Security investment should match attacker ROI: spend where an attacker's
  cheap action meets your expensive asset.
- If compromise of one account costs you little, protect it proportionally; if
  a single key compromises everything, that key is the priority target.

Pairs with: security-engineering-threat-modeling (what to defend and why),
security-and-hardening (code-level hardening), web-security-browser-internals
(the web surface), applied-cryptography-engineering (crypto used correctly),
build-gates-pipeline (the enforcement gate).
