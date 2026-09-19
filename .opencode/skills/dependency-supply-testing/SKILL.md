---
name: dependency-supply-testing
description: "Dependency and supply chain testing distilled. Use when auditing packages, lockfiles, vulnerability scans, SBOM, update policy."
---

# Dependency Supply Testing

## Purpose

Trust the supply chain: locked versions, vulnerability scans in CI, SBOM generation, update policy with rollback-tested upgrades.

## When to use

Use when the user says 'dependency scan', 'supply chain', 'SBOM', 'lockfile', 'vulnerability scan', 'npm audit', 'pip audit', 'renovate'.

## Steps

1. Lock all dependencies; verify lockfile freshness in CI.
2. Scan on every build; fail on critical with owner triage.
3. Generate SBOM per release and store with artifacts.
4. Update on policy (security fast, routine scheduled) with suite-green proof.
5. Pin build tooling too, not only runtime packages.

## Anti-patterns

- Floating versions resolving differently per machine.
- Scan warnings ignored for quarters.
- No SBOM when customers and auditors ask.
- Major upgrades merged without suite plus smoke proof.

## Example

```bash
pip-audit --desc
npm audit --audit-level=high
```

## Verification

Locks fresh, scans gated, SBOM stored per release, upgrades proven green.

## Pairs-with

secrets-scan-testing, container-image-testing, dast-sast-integration, compliance-testing-patterns.
