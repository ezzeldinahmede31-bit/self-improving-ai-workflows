# Project Agent Instructions

Copy this file into a target repo as `AGENTS.md` and fill it in.

## Purpose

This file defines project-specific rules for AI coding agents.

Agents must read this before editing code, tests, schemas, configuration, or source-of-truth documentation.

## Source of Truth

| Area | Location |
|---|---|
| Product behavior |  |
| Architecture |  |
| API contracts |  |
| Database/schema |  |
| Design system |  |
| Deployment |  |
| Security |  |
| Observability |  |

## Required Commands

| Check | Command | Required Before Done? | Notes |
|---|---|---:|---|
| Install |  | No |  |
| Typecheck |  | Yes |  |
| Lint |  | Yes |  |
| Test |  | Yes |  |
| Build |  | Yes |  |
| Format |  | If applicable |  |
| E2E |  | For user-facing flows |  |

## Architecture Rules

- Follow existing module boundaries.
- Do not move logic across layers without explicit approval.
- Prefer existing services, helpers, components, hooks, and types before creating new ones.
- Keep business rules in the existing domain/business layer.
- Do not introduce new architectural patterns without approval.

## API Rules

- Do not change request or response contracts without explicit approval.
- Update callers, tests, fixtures, mocks, generated types, and docs together.
- Preserve backward compatibility unless the task explicitly requires a breaking change.
- For new endpoints, define validation, authorization, error shape, and observability.

## Database / Migration Rules

- Every schema change needs a migration.
- Include rollback notes for destructive or hard-to-reverse changes.
- Do not drop or rename columns without a compatibility plan.
- Backfills must be idempotent or have a recovery path.
- Consider indexes for new query paths.

## Security Rules

- Validate and normalize untrusted input at boundaries.
- Check authorization before data access or mutation.
- Do not log secrets, tokens, credentials, PII, or sensitive payloads.
- Use existing secret and config mechanisms.
- Avoid SQL, command, path, template, and SSRF injection risks.

## Testing Rules

- Add or update tests for changed behavior.
- Cover happy path, edge cases, and failure cases.
- Prefer behavior-level tests over implementation-detail tests.
- Do not weaken or delete tests unless the task explicitly requires it and the reason is documented.

## Performance Rules

- Avoid N+1 queries, repeated network calls, large synchronous work, and unbounded scans.
- Use pagination, batching, caching, or indexes when the touched path requires it.
- Do not add speculative optimization.

## Do Not Touch Without Approval

- Authentication / authorization model
- Payment or billing logic
- Data deletion paths
- Deployment or infra configuration
- Public API contracts
- Large formatting-only changes
- Dependency upgrades
