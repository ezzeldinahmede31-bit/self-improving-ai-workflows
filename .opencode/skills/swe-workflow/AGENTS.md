# Agent Instructions

This repository contains the `swe-workflow` skill. `SKILL.md` is the canonical source of truth; follow it before modifying code, docs, config, or workflow files.

## Mandatory Workflow Triage

For every code-related task, the first assistant response MUST start with one of these forms:

```text
Workflow mode: Lightweight — <reason>; success: <outcome>; plan: no.
```

```text
Workflow mode: Full
Reason: <one sentence>
Success criteria:
- <what done means>
Plan needed: yes
```

## Mode Routing

Use **Lightweight** for clear localized changes, bounded investigation, and read-only review/discovery regardless of how many files are inspected.

Use **Full** before implementation when one or more applies:

- risky, destructive, or hard-to-reverse work
- API/schema/migration/security/tooling/configuration contract changes
- broad refactors, migrations, cleanup, or coupled changes across subsystems
- work requiring durable multi-session or multi-agent coordination
- material ambiguity remains after bounded repository discovery
- the user explicitly requests a persisted plan

File count and source-of-truth documentation are risk signals, not automatic Full triggers. If Lightweight discovery reveals Full criteria, stop before target-file edits, declare escalation, create/update the plan, and continue from the verified state.

## Delegated Mode Exemption

Skip the user-facing triage block, plan creation, and pre-edit gate only when all three are true:

1. The task comes from another agent/orchestrator rather than an open-ended user request.
2. Scope and success criteria or an acceptance contract are explicit.
3. The agent is operating in a focused implementer, reviewer, analyst, or researcher role.

Delegated agents follow `SKILL.md` Behavioral Guards, stay in scope, report evidence/results, and escalate unapproved decisions to the orchestrator.

## Full Workflow Pre-Edit Gate

Before any mutation of task target files in Full workflow mode:

1. A plan directory must exist under `plans/<YYYY-MM-DD>-<slug>/`
2. Exactly one writer step file must be marked `IN_PROGRESS`
3. The intended edit must map to that step's scope

Read-only discovery and workflow-bookkeeping updates (`plans/context.md`, `plans/*/plan.md`, `plans/*/steps/*.md`) are allowed before this gate is satisfied.

## Plan Directory Structure

All plans live in subdirectories for better organization and smaller-model efficiency:

```
plans/
├── context.md                           # Optional session state (overwritten each pause)
└── <YYYY-MM-DD>-<slug>/                # One directory per task
     ├── plan.md                         # Task overview, design decisions, working set
     └── steps/
          ├── step-1.md                  # Step 1: focused, self-contained
          ├── step-2.md                  # Step 2: ...
          └── step-N.md                 # Step N: ...
```

- Date-prefixed slugs (`YYYY-MM-DD-<name>`) ensure chronological file sorting
- One file per step eliminates context noise from unrelated steps
- Plan discovery uses filesystem scans of plan directories and step statuses

## Change Discipline

- Keep changes surgical and tied to the user request or current plan step.
- Verify each step with the relevant lint/type/build/test/manual check.
- Update `CHANGELOG.md` for user-visible behavior, packaging, or source-of-truth documentation changes.

## Known Pitfalls

- **SKILL.md YAML front-matter.** The `description` field (and any other scalar) must not contain bare `: ` (colon-space) sequences in plain, unquoted form — YAML parses `: ` as a map-key separator and loaders will raise `mapping values are not allowed in this context`. This is easy to hit because the description often quotes the triage labels (`Workflow mode: ...`, `Plan needed: ...`). Wrap any description that mentions `: ` in a folded block scalar (`>-`) or a double-/single-quoted string. After editing, validate by parsing the front-matter, e.g. `awk '/^---$/{c++;if(c==1)next;if(c==2)exit}c==1' SKILL.md | ruby -ryaml -e 'YAML.safe_load($stdin.read); puts "OK"'`.
- **Version bumps drift across files.** The canonical version lives in three places: `SKILL.md` front-matter `metadata.version`, `package.json` `version`, and the top `CHANGELOG.md` entry. Any bump plan must grep for the current version string and touch every hit. See `references/create-plan.md` ⨟ Common Scope Traps.

## Skill Bloat Control

- Keep `SKILL.md` focused on mandatory contract, mode routing, gates, and reference loading.
- Do not add long quality, security, performance, framework, or project-specific checklists to `SKILL.md`.
- Put phase-specific rules in `references/*.md`.
- Put optional examples in `examples/*`.
- Put target-repo-specific rules in that repo's `AGENTS.md`.
- If a rule is not required for every code task, it probably does not belong in `SKILL.md`.
