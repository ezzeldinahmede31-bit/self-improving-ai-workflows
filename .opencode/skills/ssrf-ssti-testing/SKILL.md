---
name: ssrf-ssti-testing
description: "SSRF and SSTI testing distilled. Use when testing server-side request forgery, template injection, metadata endpoints, allow-list egress."
---

# SSRF SSTI Testing

## Purpose

Prove server-side fetching and rendering cannot reach internal targets or execute template code: allow-lists, metadata blocks, sandboxed rendering.

## When to use

Use when the user says 'SSRF test', 'SSTI test', 'template injection', 'metadata endpoint', 'allow-list egress', 'webhook fetch'.

## Steps

1. Point fetch features at internal targets; assert refusal.
2. Block cloud metadata addresses explicitly and test the block.
3. Resolve DNS then validate (TOCTOU-aware) or use allow-listed hosts.
4. Render user content in sandboxed templates with no code execution.
5. Log and alert on blocked attempts for abuse visibility.

## Anti-patterns

- Fetching arbitrary user URLs with full network access.
- DNS validated once, connected later without re-check.
- Full template engines rendering user input.
- Webhook URLs without scheme and host allow-lists.

## Example

Python:

```python
with pytest.raises(RefusedTarget):
    fetch_preview("http://169.254.169.254/latest/meta-data/")
```

## Verification

Internal targets refused, metadata blocked, rendering sandboxed, attempts logged.

## Pairs-with

security-testing-owasp-fuzz, injection-testing-patterns, dast-sast-integration, webhook-trigger-hardening.
