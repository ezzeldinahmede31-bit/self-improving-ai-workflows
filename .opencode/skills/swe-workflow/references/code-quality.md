# Code Quality Bar

Use this standard when planning, implementing, and verifying code changes. Apply the closest existing project convention first; this bar fills gaps and prevents avoidable regressions.

This file defines general quality standards. Do not add framework-specific or project-specific rules here. Put project-specific rules in the target repo's `AGENTS.md`.

## Contract

1. Preserve existing behavior unless explicitly changed.
2. Prefer the smallest complete change: delete/skip unnecessary work, then use stdlib/native features, then existing helpers/dependencies, before writing custom code.
3. Follow local project patterns.
4. Reuse before creating.
5. Handle failure modes consistently.
6. Do not introduce security, data, or performance risk without mitigation.

## Correctness
- Preserve existing behavior unless the task explicitly changes it.
- Identify input/output contracts before editing.
- Handle null, empty, and error cases consistently with nearby code.
- Do not swallow errors unless existing project conventions do so.
- Do not introduce race conditions, stale state, or partial updates.

## Simplicity
- Prefer the smallest change that fully satisfies the task; delete or skip work that does not need to exist.
- Use standard library, native platform features, and existing helpers/dependencies before writing custom code.
- Do not add abstractions until there are at least two real call sites or the existing project pattern requires it.
- Avoid speculative options, flags, frameworks, or new dependencies.
- Never simplify away explicit requirements, trust-boundary validation, security, accessibility, or data-loss prevention.

## Maintainability
- Use names that reveal domain meaning, not implementation mechanics.
- Keep functions focused; split only when it improves readability.
- Keep related logic together unless the repo has a clear layering convention.
- Do not duplicate business rules across files.

## Code Smells
Use as prompts, not automatic refactor permission. Fix only smells in the task path.
- **Duplication:** one business rule appears in multiple places → reuse or extract when small and in scope.
- **Hidden side effects:** a function mutates state, performs I/O, or changes global behavior unexpectedly → make effects explicit or follow local patterns.
- **Primitive obsession:** raw strings/numbers carry domain meaning in multiple places → consider existing value objects/types before adding new ones.
- **Feature envy / Tell, Don't Ask:** code pulls data out of another object/module to make its decisions → move behavior only if it fits existing boundaries.
- **Shotgun surgery:** one change requires many unrelated edits → revisit boundaries before continuing.

## Test-First / TDD When Useful
- For new behavior, bug fixes, and refactors with clear expected behavior, prefer a failing focused test before implementation when the repo has a test framework.
- Do not force TDD for docs, config-only changes, throwaway exploration, or trivial mechanical edits.
- Use tests to pin contracts and edge cases; refactor only after behavior is protected.

## Design Quality Prompts
Apply when changing classes, services, modules, hooks, or domain logic; skip when irrelevant.
- **Single responsibility:** can this unit be explained in one sentence without "and then"?
- **Open/closed:** can the requested variant be added without editing unrelated callers?
- **Substitution:** do implementations preserve the promises of the interface/base behavior?
- **Interface shape:** do consumers depend only on methods/data they actually need?
- **Dependency direction:** does high-level policy avoid depending on low-level details when the project has layering boundaries?

## Architecture / Design Fit
- Keep boundaries aligned with existing layers, modules, domains, and dependency direction.
- Prefer vertical slices for features; avoid horizontal rewrites unless the task is explicitly architectural.
- Use design patterns only when they simplify current code; do not introduce pattern machinery speculatively.
- For broad refactors or domain-boundary changes, record the chosen boundary and tradeoff in the plan.

## Project Fit
- Match existing naming, file organization, error handling, logging, testing, and dependency patterns.
- Reuse existing helpers, components, hooks, services, and types before creating new ones.
- Do not copy known-bad legacy patterns unless required for compatibility; document the compatibility reason if you must.

## API / Schema / Contract Changes
- Identify all callers and downstream consumers.
- Preserve backward compatibility unless explicitly approved.
- Update tests, types, docs, fixtures, mocks, and examples together.
- Include migration and rollback notes for data shape changes.

## Security
- Do not log secrets, tokens, credentials, PII, or sensitive payloads.
- Validate and normalize untrusted input at boundaries.
- Check authorization before data access or mutation.
- Avoid SQL, command, path, and template injection.
- Use existing secret and configuration mechanisms.

## Performance
- Avoid unnecessary full scans, N+1 queries, repeated network calls, and large synchronous work.
- Consider pagination, batching, caching, and indexes when touching data access.
- Do not optimize speculatively; optimize when the code path or task requires it.

## Observability
- Preserve existing logging, metrics, and tracing conventions.
- Add useful logs only at boundaries or failure points.
- Do not add noisy debug logs.
