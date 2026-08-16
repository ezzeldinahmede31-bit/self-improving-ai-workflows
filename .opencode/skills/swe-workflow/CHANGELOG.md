# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [1.12.2] - 2026-07-18

### Added
- Added `npm test` validation with no npm dependencies for full YAML front matter and field types, version alignment, unsupported aliases, internal links, packaged paths, template fields, source-control safety, plan discovery/lifecycle, and mode routing.
- Expanded behavioral evaluation cases with expected and forbidden outcomes for both modes, escalation, delegated work, resume, clarification, dirty-worktree safety, and final reflection.

### Changed
- Kept the two-mode model while making Lightweight the default for localized changes and read-only review/discovery regardless of inspected-file count.
- Routed Full by implementation risk, contract impact, coupling, durable coordination, or ambiguity remaining after bounded discovery; file count is now a signal rather than an automatic trigger.
- Reduced routine ceremony with concise Lightweight triage, decision-critical clarification, one plan approval, outcome-sized steps, and single-writer/read-only-concurrency guidance.
- Updated both plan examples to the current template fields and vertical behavior slices.
- Qualified cross-host compatibility and manual installation guidance because discovery paths and host-specific behavior vary by version.

### Fixed
- Replaced unsupported tokenized path aliases with standard Agent Skills/Markdown paths and repaired remaining broken example links.
- Removed automatic staging, stashing, and committing instructions; user work now requires explicit authorization before any Git state mutation.
- Fixed active-plan discovery to scan canonical nested plans and authoritative step statuses.
- Made global reflection the sole owner of plan-level completion and required scoped fix steps for reflection-discovered edits.
- Aligned repository-level instructions with the Delegated Mode exemption and strengthened validation with malformed-front-matter and generalized Git-mutation regressions.

## [1.12.1] - 2026-06-13

### Changed
- Added a compact minimalism ladder to core and delegated quality guidance: skip/delete unnecessary work first, prefer stdlib/native/existing helpers before custom code, and keep safety/accessibility/explicit requirements intact.

## [1.12.0] - 2026-06-11

### Changed
- **SKILL.md reduced 57%** (14.8KB → 6.4KB, ~3,700 → ~1,600 tokens). Removed Anti-Patterns section (covered by templates), Reference Guide table (redundant with phase-gated loading), Plan Templates section (redundant with Contract #4), Core Constraints (redundant with Contract + Guards). Compressed Status Vocabularies and Plan Directory Structure. Tightened Behavioral Guards from 10 → 8.
- **`references/verify-step.md`** now includes Definition of Done (formerly a separate file). Always-co-loaded files merged into one.
- **`references/execute-step.md` reduced 61%** (9.7KB → 3.8KB). Removed contract bullets that restated SKILL.md guards and implementation guidelines that pointed to code-quality.md.
- **`references/checkpoint.md`** replaces `reflect-after-changes.md` + `dump-context.md` (always sequential, now one file).

### Removed
- `references/definition-of-done.md` — merged into `verify-step.md`.
- `references/reflect-after-changes.md` — merged into `checkpoint.md`.
- `references/dump-context.md` — merged into `checkpoint.md`.
- `references/plan-example.md` — relocated to `examples/plan-example.md` (not a runtime reference).

## [1.11.0] - 2026-06-10

### Added
- **Delegated Mode (Multi-Agent).** New section in `SKILL.md` that lets child agents skip triage, plan creation, and the pre-edit gate when they receive a focused task from an orchestrator with explicit scope and success criteria. Detection is agent-agnostic — any LLM self-applies based on context, no platform-specific hooks required.
- **`references/delegated-guards.md`** — standalone behavioral guards and code quality bar for orchestrators that want minimal-overhead injection into child agents. Works across Pi, Claude Code, Cursor, Codex, Gemini, and any platform that supports injecting text into a child's context.
- **Subagent / Multi-Agent Orchestration** section in `README.md` documenting orchestrator vs delegated child roles, three injection strategies, and platform examples.

## [1.10.0] - 2026-06-05

### Added
- Added lightweight evidence discipline across the canonical guard, execution gate, task overview template, and Definition of Done so agents label key repo claims as Verified, Assumption, Unknown, or Recommendation.
- Added anti-shortcut safeguards for smaller LLMs: evidence-before-edit, no-guessed-facts handling, evidence-gap completion blockers, and visible skipped-check reasons.
- Added bounded command-output guidance with `/tmp` raw-output storage and a compact `Command`/`Exit`/`Output`/`Summary`/`Freshness` evidence schema.
- Added conditional Spec-Lite fields, optional gate triggers, quality-checklist dedupe, lifecycle state ownership, and a compact final response standard.
- **Directory-based plan structure.** Plans now live in `plans/<YYYY-MM-DD>-<slug>/` with a task overview at `plan.md` and individual step files in `steps/step-N.md`. Date-prefixed slugs ensure chronological sorting; one file per step keeps each unit small enough to fit cleanly in smaller LLMs' context windows.
- **`references/task-overview-template.md`** — canonical skeleton for `plan.md` (task overview only: Goal, Assumptions, Design Decisions, Steps Overview table, Working Set, Verified Facts, Implementation Log).
- **`references/step-template.md`** — canonical skeleton for each `steps/step-N.md` (10 required fields, 20–40 lines per step).
- **Plan-level status vocabulary** (`DRAFT │ ACTIVE │ COMPLETED │ ARCHIVED`) introduced alongside the existing step-level vocabulary (`PENDING │ IN_PROGRESS │ COMPLETED │ BLOCKED`). Plan status describes lifecycle; step status describes execution state. New "Status Vocabularies" section in `SKILL.md` makes the distinction explicit.
- New "Plan Directory Structure" and "Status Vocabularies" top-level sections in `SKILL.md`.
- Inline status documentation comment in `references/task-overview-template.md` so the template itself explains the lifecycle values.

### Changed
- **`SKILL.md`** front-matter `description` rewritten to point at the two new templates and updated path conventions; YAML indentation normalized to 2-space throughout.
- **`AGENTS.md`** updated with the new directory structure diagram and pre-edit gate rules.
- **`README.md`** structure tree, multi-agent handoff section, and Full workflow paragraph updated to reflect the directory layout.
- **`references/execute-step.md`** updated: select step by reading `steps/step-N.md`, mark `IN_PROGRESS` in the step file, and sync `plan.md`.
- **`references/plan-example.md`** rewritten as a directory-layout example showing both `plan.md` (task overview) and individual step files.

### Removed
- Removed repo-map and runtime plan indexes from the active workflow, examples, resume/persist guidance, and shipped reference files. Task-local `plan.md`, step files, and optional `context.md` are now the only workflow state surfaces.
- **`references/plan-template.md`** — superseded by `task-overview-template.md` (overview) + `step-template.md` (per-step).
- Runtime plan state reference docs and examples — markdown plan/step files are now the source of truth.

### Fixed
- Stray trailing backticks in `references/plan-example.md` example bullets.
- Indentation drift in `README.md` structure tree, `SKILL.md` triage block code fence, and `SKILL.md` description folded scalar.
- Missing `plan.md` entry in the `SKILL.md` Plan Directory Structure tree.
- Path placeholder `plans/<task>/...` in `references/step-template.md` corrected to `plans/<YYYY-MM-DD>-<slug>/...` to match the convention used everywhere else.

## [1.9.2] - 2026-05-21

### Added
- Added optional SOLID-inspired code smell, test-first/TDD, design-quality, and architecture-fit prompts to `references/code-quality.md`.
- Added planning/execution hooks so architecture and design-quality guidance is applied only for broad refactors, domain logic, or boundary changes.

## [1.9.1] - 2026-05-21

### Added
- Added explicit **Think in code** behavioral guidance in `SKILL.md` to prefer concise computed results for aggregate analysis over raw dumps.
- Added explicit **Tool-use heuristics** behavioral guidance in `SKILL.md` to prefer targeted search/scoped reads/bounded output.
- Added planning-phase heuristics in `references/create-plan.md` for targeted reads and script-based aggregate analysis.
- Added execution-phase heuristics in `references/execute-step.md` for bounded tool output and computed summaries.
- Clarified `README.md` opening text to explicitly expand `SWE` as Software Engineering Workflow.

## [1.9.0] - 2026-05-11

### Added
- `references/definition-of-done.md` as a final completion gate for scope, correctness, project fit, validation, and final response requirements.
- `references/command-discovery.md` so agents discover validation commands from repo evidence instead of guessing.
- `references/risk-classification.md` for compact step-level risk review and mitigation.
- `references/project-agents-template.md` for optional target-repo `AGENTS.md` setup.
- `examples/evaluation-prompts.md` for optional workflow evaluation prompts.

### Changed
- Added concise `SKILL.md` reference-loading rules while keeping detailed quality guidance in reference files.
- Added a compact Validation Commands section and risk/mitigation quality prompts to the plan template.
- Documented production code-quality setup and repository bloat-control rules.

## [1.8.0] - 2026-05-10

### Added
- `references/code-quality.md` as a reusable quality bar covering correctness, simplicity, maintainability, project fit, contracts, security, performance, and observability.
- Per-step Quality Checklist in `references/plan-template.md`, `SKILL.md`, and the worked plan example so agents record existing-pattern, contract, reuse, edge-case, and risk review before completion.

### Changed
- Strengthened `references/execute-step.md` with a Quality Gate Before Editing and implementation blockers tied to the reusable quality bar.
- Strengthened `references/verify-step.md` with explicit contract, security, data safety, performance, project-fit review rows and a final Quality Review gate.
- Updated planning docs and README structure references to include the reusable quality bar consistently.

## [1.7.0] - 2026-05-03

### Added
- **Contract blocks** at the top of every reference file (first 5-10 rules). A low-thinking agent reading only the first 20-30 lines of any reference now gets every critical gate.
- **Design Decisions table** in the plan template. UX, schema, component, and API contract choices must be surfaced for user confirmation during planning — not assumed silently.
- **Design confirmation gate** in execute-step. Design-sensitive steps verify approach matches existing conventions or the Design Decisions table before implementing.
- **Design convention discovery** in create-plan. When a task touches UI, schema, or API, the agent searches for existing patterns, shared components, and reusable code before planning.
- **Reuse-before-create behavioral guard** (§4 in SKILL.md). Agents must search for existing equivalents before creating new components, utilities, or schema patterns; evidence of the search goes in Verified Facts.
- **Design discipline behavioral guard** (§5 in SKILL.md). Silent design choices are prohibited; design decisions must be confirmed by the user.
- **Bullet quality standard** in create-plan. Every plan bullet must name a tool (`edit`/`write`/`bash`), a file path, and the specific change.
- **Concrete example placeholders** in plan-template.md. Step fields now show realistic examples (tool-prefixed plan bullets, exact validation commands, explicit step dependencies, outcome sentences).
- **`references/plan-example.md`** — a complete, realistic 3-step filled-in plan example for low-thinking agents to copy from.
- **Append-only rule** for Context & Learnings in the plan template.
- **Silent design assumptions** anti-pattern added to SKILL.md.

### Changed
- All 11 reference files restructured with Contract blocks front-loaded as first section.
- Total reference file lines compressed from 1833 to 1086 (−41%) while adding new design discipline content. Verbose sections (examples, tables, repeated checklists) tightened without losing critical rules.
- Behavioral guard §4 "Code quality" split into §4 "Reuse before create" + §5 "Design discipline"; original code quality aspects covered by existing guards §1/§3/§6.
- Plan template `Deliverables` now includes "After this step: [observable outcome]" guidance.
- Plan template `Prerequisites` now includes "Files to modify:" and explicit step dependency examples.
- Plan file format contract rule updated to mention Design Decisions table.
- Clarification phase now includes design decision identification (require-clarification.md).
- Strengthened the Full workflow clarification gate (from pre-v1.7.0 commit): plans must use `Open Questions: None.`, unresolved questions must be asked in chat before plan creation/finalization or execution.

## [1.6.1] - 2026-04-30

### Changed
- Strengthened all-code-task behavioral guards with evidence-first, language-agnostic quality guidance: verify paths/imports/dependencies, avoid degraded correctness patterns, run formatter/format-checker when present, and fix introduced issues before completion.
- Added task-local Working Set and Verified Facts sections to the Full workflow plan template so agents record evidence for files, APIs, dependencies, conventions, and tests instead of relying on guesses.
- Reframed `plans/repo-map.md` as optional advisory project memory, not a mandatory file inventory; planning, execution, verification, persistence, resume, context dump, and reflection now prioritize task-local evidence and current-workspace verification.
- Updated README and the email-validation worked example to make `plans/context.md` and `plans/<task>.md` primary, with `plans/repo-map.md` optional/advisory.

## [1.6.0] - 2026-04-26

### Changed
- **Skill `description` rewritten as an enforceable contract (845 chars).** The advertised description — the only part of the skill guaranteed to be in an agent's context — now explicitly instructs the agent to `read` SKILL.md, emit the triage block with the exact four labels, and use `references/plan-template.md` verbatim for Full-mode plans. It also names common violation shapes (freeform plans, inline `[STATUS]` headers, skipping triage).
- **SKILL.md restructured to front-load enforceable content.** First section is now "Contract" — a 16-line minimum-compliance block covering triage, Full-workflow triggers, pre-edit gate, plan file format, and one-step-at-a-time. The WRONG vs RIGHT anti-pattern block is promoted above Full Workflow. A third anti-pattern — "Triage skipped because the task seemed simple" — was added.
- The inline plan skeleton in SKILL.md was extracted to `references/plan-template.md` to remove duplication and give agents a concrete copy target.

### Added
- `references/plan-template.md` — canonical `plans/<task>.md` skeleton with a required-fields checklist and a violations list. Plans must copy this file verbatim.
- `plans/` is now gitignored. Plan files are local session state, not published artifacts.

## [1.5.1] - 2026-04-26

### Added
- Behavioral guards persistence note: guards are active for the entire session, not just the first response.
- Step decomposition anti-pattern in SKILL.md: WRONG (horizontal slices) vs RIGHT (vertical slices).
- Vertical-slice step sizing guide in `create-plan.md` with visual comparison.
- Grilling intensity for clarification: walk each branch of the design tree, provide recommended answers, explore codebase instead of asking when possible.

## [1.5.0] - 2026-04-26

### Changed
- **Restructured SKILL.md for agent compliance.** Plan format and step format are now inlined directly in SKILL.md so agents get the required output structure on the first read. Previously the plan template was 3 hops away (SKILL.md → create-plan.md → plan-template.md), causing 72% of plans to be non-compliant.
- SKILL.md reduced from 248 to 150 lines while adding the inlined plan format.
- Behavioral guards condensed from multi-bullet sections to one-line summaries.
- Added WRONG vs RIGHT anti-pattern comparison for plan format.
- Reference files are now supplementary (consulted when needed), not sequential prerequisites.
- `create-plan.md` updated to reference SKILL.md for plan format instead of deleted template file.

### Removed
- `assets/` directory and all template files (`plan-template.md`, `context-template.md`, `repo-map-template.md`). Content is now inlined in SKILL.md and respective reference files.
- Operating Modes table, Full workflow decision test, Skill Chain diagram, "Why Full Workflow Works" section, and Compact Variant section from SKILL.md (content preserved in condensed form or reference files).

## [1.4.2] - 2026-04-26

### Fixed
- Fixed issue where agent would write only the first phase to the plan file when user says "start with phase 1" after approving a multi-phase plan in chat. Plan file now explicitly requires ALL steps for ALL phases before execution begins.
- Added Full Workflow Guard: plan file missing steps for later phases blocks execution until completed.

## [1.4.1] - 2026-04-26

### Changed
- Strengthened workflow guidance to require focused tests for new utilities/functions/modules when a test framework exists.
- Strengthened verification guidance to run configured pre-commit hooks and quality gates, including lefthook, before marking work complete.

## [1.4.0] - 2026-04-24

### Added
- Mandatory workflow triage in `SKILL.md`, requiring agents to declare Lightweight or Full mode before code-task edits.
- Explicit Full workflow triggers for broad cleanup, lint/type/build/test cleanup, refactors, file deletion/moves, backend + UI changes, API/config contracts, source-of-truth docs, ambiguous scope, and tasks expected to touch more than 3 files.
- Full workflow pre-edit hard stop requiring a plan, an `IN_PROGRESS` step, and an edit mapped to that step before task target files are changed.
- Compact Full workflow guidance for broad cleanup/refactor/lint tasks.
- `AGENTS.md` repo-level instruction template to make workflow expectations visible outside the skill file.

### Changed
- Updated `README.md` to document triage-first behavior and stronger Full workflow expectations.
- Updated package metadata and included `AGENTS.md` in the package file list.

## [1.3.1] - 2026-04-24

### Added
- Behavioral Guards that apply to all code-related tasks: think before coding, simplicity first, surgical changes, and goal-driven execution.

### Changed
- Reframed the skill into lightweight and full workflow modes so simple coding tasks use behavioral guidance without creating plan files.
- Updated package metadata to describe behavioral guards plus the structured planning workflow.

## [1.3.0] - 2026-04-17

### Added
- `LICENSE` file (MIT).
- `CHANGELOG.md`.
- `package.json` with project metadata.
- `references/verify-step.md` — consolidated validation + testing + diff review into a single gate.
- `examples/add-email-validation/` — worked example showing populated `plan.md`, `repo-map.md`, and `context.md` mid-task.

### Changed
- **Consolidated references.** `validate-step.md`, `enforce-tests.md`, and `review-diff.md` merged into `verify-step.md` (three passes, one gate). `protect-code.md` folded into `execute-step.md` as a rules-of-thumb section. Net reduction: 4 files, ~460 lines.
- **Rewrote `SKILL.md`** (288 → ~180 lines): removed duplicated tables, simplified the skill chain diagram, deduped content with README.
- **Rewrote `README.md`** (247 → ~110 lines): stripped duplication with `SKILL.md`; README now focuses on install, purpose, and pointers.
- **Tightened `resume-workflow.md`** (340 → ~240 lines): compressed example, replaced prose with tables, removed duplicated "why" sections.
- **Simplified repo-map sync in `persist-plan.md`:** single-source procedure now lives in `maintain-repo-map.md`; other references link to it instead of repeating.
- Removed duplicate Status Values and File Relationships sections from `persist-plan.md` (canonical versions live in `SKILL.md`).
- Bumped version to `1.3.0`.

### Fixed
- Typo: "syncronized" → "synchronized" in `references/persist-plan.md`.

## [1.2.1] - 2026-03-21

### Added
- Guard clause in `SKILL.md` to prevent over-invocation of the workflow on
  simple tasks (single-file edits, quick fixes, clear requests, etc.).
- "Handling Partial Answers" section in `require-clarification.md` so the
  agent re-asks unanswered questions instead of assuming.

## [1.2.0] - 2026-03-21

### Added
- **Context & Learnings** section in plans so decisions, gotchas, and
  patterns survive across sessions.
- Step isolation (explicit Prerequisites / Deliverables) enabling fresh
  sessions to pick up any step.
- Plan progress reminders after each step to prevent drift.
- Plan drift detection after unplanned work (bug fixes, user adjustments).
- Expanded documentation and workflow structure for context management.

### Changed
- Repo Map discipline is now enforced: a step cannot pass validation or be
  marked COMPLETED until the repo map reflects all touched files.
- Clarification workflow tightened — explicit user confirmation required
  before moving to planning.

## [1.0.0] - 2026-03-21

### Added
- Initial release of the SWE workflow skill for coding agents.
- Core references: `require-clarification`, `create-plan`, `execute-step`,
  `validate-step`, `enforce-tests`, `review-diff`, `protect-code`,
  `persist-plan`, `dump-context`, `maintain-repo-map`,
  `reflect-after-changes`, `global-reflection`, `resume-workflow`.
- Templates: `plan-template.md`, `repo-map-template.md`,
  `context-template.md`.

[Unreleased]: https://github.com/ex-git/swe-workflow/compare/v1.12.2...HEAD
[1.12.2]: https://github.com/ex-git/swe-workflow/compare/v1.12.1...v1.12.2
[1.12.1]: https://github.com/ex-git/swe-workflow/compare/v1.12.0...v1.12.1
[1.12.0]: https://github.com/ex-git/swe-workflow/compare/v1.11.0...v1.12.0
[1.11.0]: https://github.com/ex-git/swe-workflow/compare/v1.10.0...v1.11.0
[1.10.0]: https://github.com/ex-git/swe-workflow/compare/v1.9.2...v1.10.0
[1.9.2]: https://github.com/ex-git/swe-workflow/compare/v1.9.1...v1.9.2
[1.9.1]: https://github.com/ex-git/swe-workflow/compare/v1.9.0...v1.9.1
[1.9.0]: https://github.com/ex-git/swe-workflow/compare/v1.8.0...v1.9.0
[1.8.0]: https://github.com/ex-git/swe-workflow/compare/v1.7.0...v1.8.0
[1.7.0]: https://github.com/ex-git/swe-workflow/compare/v1.6.1...v1.7.0
[1.6.1]: https://github.com/ex-git/swe-workflow/compare/v1.6.0...v1.6.1
[1.6.0]: https://github.com/ex-git/swe-workflow/compare/v1.5.1...v1.6.0
[1.5.1]: https://github.com/ex-git/swe-workflow/compare/v1.5.0...v1.5.1
[1.5.0]: https://github.com/ex-git/swe-workflow/compare/v1.4.2...v1.5.0
[1.4.2]: https://github.com/ex-git/swe-workflow/compare/v1.4.1...v1.4.2
[1.4.0]: https://github.com/ex-git/swe-workflow/compare/v1.3.1...v1.4.0
[1.3.1]: https://github.com/ex-git/swe-workflow/compare/v1.3.0...v1.3.1
[1.3.0]: https://github.com/ex-git/swe-workflow/compare/v1.2.1...v1.3.0
[1.2.1]: https://github.com/ex-git/swe-workflow/compare/v1.2.0...v1.2.1
[1.2.0]: https://github.com/ex-git/swe-workflow/compare/v1.0.0...v1.2.0
[1.0.0]: https://github.com/ex-git/swe-workflow/releases/tag/v1.0.0
