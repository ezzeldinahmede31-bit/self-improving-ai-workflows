# Risk Classification

Use this during planning and before implementation.

## Contract

1. Every Full workflow task must classify risk before implementation.
2. Do not mark all risks as "none" by default.
3. A risk is "none" only when the current task and touched files provide evidence.
4. Any non-none risk must have a mitigation in the plan.
5. Reclassify if implementation touches new files or contracts.

## Compact Risk Line

Use this format in each step:

```text
Risk reviewed: correctness / API / data / security / performance / observability / project-fit / none
Mitigation:
```

## Risk Triggers

### Correctness

Applies when behavior changes, branching logic changes, validation changes, error handling changes, or existing tests need updates.

### API / Contract

Applies when changing public functions, routes, request/response shapes, events, schemas, CLI flags, config keys, generated types, or shared interfaces.

### Data / Migration

Applies when changing persistence, schema, migrations, backfills, indexes, data deletion, data retention, or serialization.

### Security

Applies when touching authentication, authorization, secrets, tokens, PII, user input, file paths, network calls, shell commands, SQL, templates, or admin behavior.

### Performance

Applies when touching loops over unbounded data, database queries, network calls, rendering hot paths, caching, pagination, batching, or large synchronous work.

### Observability

Applies when changing error paths, background jobs, critical flows, logging, metrics, tracing, alerting, or audit behavior.

### Project Fit

Applies when adding a new abstraction, dependency, file pattern, directory, component, service, hook, helper, or test style.

## Mitigation Examples

- Add caller updates and compatibility tests.
- Add authorization checks and forbidden-case tests.
- Add migration rollback notes.
- Replace N+1 query with batch, join, include, or equivalent project pattern.
- Reuse an existing project helper instead of creating new abstraction.
