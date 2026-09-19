---
name: container-image-testing
description: "Container image testing distilled. Use when testing Docker images, base layers, vuln scans, non-root users, slim builds, signing."
---

# Container Image Testing

## Purpose

Ship minimal trustworthy images: slim bases, vulnerability scans, non-root runtime, signed provenance, behavior smoke tests.

## When to use

Use when the user says 'Docker test', 'image scan', 'Trivy', 'non-root', 'distroless', 'image signing', 'slim image'.

## Steps

1. Build from minimal bases; multi-stage away build tooling.
2. Scan layers in CI; fail on critical findings.
3. Run as non-root with read-only filesystem where possible.
4. Sign images and verify signatures at deploy.
5. Smoke-test the image (boot, health, version) before promotion.

## Anti-patterns

- `latest` tags with no digest pinning.
- Running as root by default.
- Secrets baked into layers.
- Full OS images for static binaries.

## Example

```bash
trivy image --severity HIGH,CRITICAL myapp:1.4.2
docker run --read-only --user 65532 myapp:1.4.2
```

## Verification

Scans gated, non-root enforced, signatures verified, smoke green per image.

## Pairs-with

docker-deep-dive, dependency-supply-testing, dast-sast-integration, kubernetes-operations.
