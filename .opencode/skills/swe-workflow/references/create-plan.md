# Create Plan

## Contract — Read This First

1. Full mode must be selected and decision-critical clarification complete. If a blocking decision remains, stop and ask in chat; do not re-confirm scope the user already approved.
2. Open Questions must be exactly `None.` — do not create a plan with unresolved questions.
3. Explore narrowly — read only files needed to plan; record evidence in Working Set and Verified Facts.
4. Discover design conventions — if the task touches UI, schema, or API, search for existing patterns, shared components, and reusable code before planning. Record in Verified Facts.
5. For broad refactors, domain logic, or boundary changes, apply architecture/design-quality prompts from `references/code-quality.md`; record tradeoffs in Verified Facts or Design Decisions.
6. Fill the Design Decisions table — surface every UX, schema, or API choice for user confirmation. Write `None — no design-sensitive changes.` if N/A.
7. Break into vertical slices — each step is one thin slice through all layers (types, logic, tests), independently verifiable. Never horizontal.
8. Bullet quality — every plan bullet must name an action capability (`read`/`search`/`edit`/`create`/`run` or the host equivalent), a file path or query, and the specific change/check. Include inspection/search/validation bullets when relevant; if skipped, record why.
9. Think in code for analysis — when planning requires repo-wide counts/inventories/comparisons, prefer one script/command that computes concise results over many raw reads.
10. Reuse before create — search for existing shared code before planning to create new components, utilities, or patterns. Evidence in Verified Facts.
11. Write ALL steps — the plan must contain every step for every phase. Partial plans block execution.
12. Copy [`task-overview-template.md`](task-overview-template.md) and [`step-template.md`](step-template.md) verbatim — do not invent your own format.

## Instructions

1. **Verify clarification is complete** — if any decision-critical open question remains, go back to require-clarification. Do not create a plan with unresolved decisions, and do not add a separate confirmation turn for already-approved scope.

2. **Define the plan header:**
    - **Goal:** one sentence describing what we're building
    - **Assumptions:** what we're taking for granted
    - **Open Questions:** exactly `None.`. If anything else would go here, stop and ask the user.
    - **Spec-Lite:** fill Acceptance Criteria / Non-goals / Edge Cases when triggered below; otherwise write `N/A`.
    - **Design Decisions:** fill the table or write `None — no design-sensitive changes.`

### Optional Gate Triggers

| Gate | Trigger | Output |
|---|---|---|
| Spec-Lite | Ambiguous, high-risk, user-facing, API/schema, or behavior-heavy work | Acceptance Criteria, Non-goals, Edge Cases |
| Risk review | API, data, security, performance, observability, or project-fit risk | Risk line + mitigation in step |
| Design-quality | Broad refactor, domain logic, service boundary, reusable abstraction | Tradeoff in Verified Facts or Design Decisions |
| Test-first/TDD | New behavior, bug fix, or refactor with clear expected behavior | Focused failing/protective test when framework exists |
| Command discovery | Any task requiring lint/type/test/build/CI-equivalent validation | Validation Commands table |

3. **Explore the codebase narrowly:**
    - Search for relevant files and directories with targeted `rg`/`find`/`git` commands
    - Read only files needed to plan: likely targets, direct callers/callees, nearby tests, relevant config
    - Prefer targeted reads (specific sections/line ranges) over full-file dumps unless full structure is required.
    - For aggregate questions (counts, inventories, comparisons), prefer one short script/command that computes and prints concise results.
    - **Design convention discovery** (when task touches UI, schema, or API):
      - Frontend: search for existing shared/reusable components, design tokens, layout patterns
      - Schema: search for naming conventions, relationship patterns, migration style
      - API: search for route naming, response shape, error format
    - **Architecture/design-quality review** (for broad refactors, domain logic, or boundary changes): apply `references/code-quality.md` prompts for boundaries, dependency direction, code smells, and test-first opportunities.
    - **Reuse check:** before planning to create anything new, search for existing equivalents. Record evidence ("no match found" or "existing X can be extended").
    - Record all evidence in the plan's Working Set and Verified Facts

4. **Break work into ordered vertical-slice steps:**
    - Each step produces one independently verifiable outcome; size by coherent outcome, not an arbitrary time or file-count target
    - For behavior changes, each step is a thin slice through necessary layers (types, logic, tests) rather than a horizontal phase
    - Steps must be ordered by dependency
    - All steps start as **PENDING**
    - Do not add a step whose purpose is to resolve open questions

5. **Define prerequisites and deliverables for each step:**
    - **Prerequisites:** What must be true (step deps, files to modify, design confirmations needed)
    - **Deliverables:** What this step produces + "After this step: [observable outcome]"

6. **Derive the plan directory** — date-prefixed kebab-case from the feature description (e.g., `plans/2026-06-04-add-user-auth/`)
   - Date prefix (`YYYY-MM-DD`) ensures chronological file sorting
   - Kebab-case slug is unique and readable

7. **Create the task directory:** `mkdir -p plans/<YYYY-MM-DD>-<slug>/`
   - Create a `steps/` subdirectory: `mkdir -p plans/<YYYY-MM-DD>-<slug>/steps/`

8. **Write the task overview:**
    - Copy `references/task-overview-template.md` to `plans/<YYYY-MM-DD>-<slug>/plan.md`
    - Fill in Goal, Assumptions, Open Questions, Spec-Lite, Design Decisions, Validation Commands, Steps Overview
    - Set initial status to `DRAFT`

9. **Write one step file per step:**
    - Copy `references/step-template.md` to each `plans/<YYYY-MM-DD>-<slug>/steps/step-N.md`
    - Fill all required fields in every step file
    - All steps start as **PENDING**

10. **Verify the plan:**
     - `read` each task overview and step file — confirm Goals, Assumptions, Open Questions (`None.`), Design Decisions, Steps Overview
     - Verify every non-trivial assumption is answered, recorded, or evidence-backed

11. **Present once for execution approval:** `Plan created. Open questions: none. Ready to proceed with Step 1?` This is the sole routine pre-execution approval; do not precede it with a duplicate "ready to plan" handshake.

## Mandatory Outputs

- [ ] Task directory at `plans/<YYYY-MM-DD>-<slug>/`
- [ ] Task overview at `plans/<YYYY-MM-DD>-<slug>/plan.md` with Goal, Assumptions, Open Questions (`None.`), Spec-Lite (filled or `N/A`), Design Decisions (filled or `None`)
- [ ] One step file per step: `plans/<YYYY-MM-DD>-<slug>/steps/step-N.md` — all 10 fields populated
- [ ] Working Set with evidence, Verified Facts with tool citations in plan overview
- [ ] All steps for all phases present; steps ordered by dependency
- [ ] Every plan bullet names an action capability + file path/query + specific change
- [ ] No code written yet

## Constraints

- **Do NOT write code** in this phase — plans only
- **Do NOT skip to implementation** — plan must exist first
- **Do NOT write a plan with unresolved questions** — ask in chat first
- **Do NOT use DRAFT as a loophole** — DRAFT requires completed clarification
- **Do NOT write a partial plan** — ALL steps for ALL phases required
- **Do NOT invent your own format** — copy task-overview-template.md and step-template.md verbatim
- **Do NOT create new code without a reuse check** — search for existing equivalents first; evidence in Verified Facts
- **Do NOT make silent design choices** — surface in Design Decisions table for user confirmation
- If coherent, independently verifiable outcomes cannot be defined, return to bounded discovery or clarification

### Common Scope Traps

Before writing the plan, grep for any value that must stay consistent across files:

- **Version bumps:** grep current version across SKILL.md, package.json, CHANGELOG.md, README.md
- **Renames:** grep old name; include every caller in the plan
- **Schema/column changes:** grep in migrations, models, raw SQL, type definitions
- **Config keys:** grep in `.env.example`, `config.*`, docs, tests

If grep surfaces unexpected hits, fold them into the plan or note them as out of scope in Assumptions.

## Next Step

→ Proceed to: **execute-step** (implement the first PENDING step from `steps/step-1.md`)
