# swe-workflow

A lightweight, structured Software Engineering Workflow (SWE workflow) for AI coding agents. It targets the portable Agent Skills core and is designed for **Pi**, **Claude Code**, **Cursor**, **Codex**, and **Gemini**; discovery paths and host-specific behavior vary by version.

> Every code task starts with workflow triage. Bounded work stays lightweight; risky or coordination-heavy implementation uses a persisted plan.

## What It Does

Enforces visible workflow selection plus a disciplined process for any coding task complex enough to warrant it:

1. **Triage** — choose `Lightweight` or `Full` before target-file edits
2. **Discover/clarify** — inspect first; ask only decision-critical questions evidence cannot answer
3. **Plan** — persist Full work as ordered, independently verifiable steps
4. **Execute** — keep one active writer step while allowing independent read-only investigation/validation
5. **Verify** — re-read, test, review diff (single gate)
6. **Reflect** — catch complexity before it compounds

Every reference file front-loads a **Contract block** (first 5-10 rules) so even low-thinking agents absorb the critical gates.

In Full workflow mode, task state lives in `plans/<YYYY-MM-DD>-<slug>/plan.md` plus individual step files at `steps/step-N.md` plus `plans/context.md`.

## Why

Without structure, coding agents tend to:
- Jump straight to code without understanding the request
- Make sweeping changes that break unrelated code
- Skip testing and self-review
- Lose context across sessions

This workflow addresses all of that with a single skill, mandatory mode declaration, and persistent plan files when needed. See [`SKILL.md`](SKILL.md) for the full agent-facing specification.

## Expected Agent Behavior

For clear localized work and read-only review/discovery, the agent starts with:

```text
Workflow mode: Lightweight — <reason>; success: <outcome>; plan: no.
```

For risky, coupled, cross-session, contract-changing, or still-materially-ambiguous implementation, it starts with:

```text
Workflow mode: Full
Reason: ...
Success criteria:
- ...
Plan needed: yes
```

File count alone does not select Full. Lightweight discovery escalates before target-file edits when it uncovers Full-mode risk. In Full mode, valid plans record `Open Questions` as `None.`, surface decision-sensitive choices, and require exactly one writer step marked `IN_PROGRESS` before implementation.

## Installation

Via the [Agent Skills CLI](https://skills.sh):

```bash
# Install globally (all supported agents)
npx skills add ex-git/swe-workflow -g

# Install for a specific agent
npx skills add ex-git/swe-workflow -g --agent claude
npx skills add ex-git/swe-workflow -g --agent cursor
npx skills add ex-git/swe-workflow -g --agent pi
npx skills add ex-git/swe-workflow -g --agent codex
npx skills add ex-git/swe-workflow -g --agent gemini
```

### Manual install

Copy the skill directory to your host's documented skill location. Common locations are shown below; verify them against the current host version:

```bash
# Pi
cp -r swe-workflow ~/.pi/agent/skills/

# Claude Code
cp -r swe-workflow ~/.claude/skills/

# Cursor
cp -r swe-workflow ~/.cursor/skills/

# Codex
cp -r swe-workflow ~/.codex/skills/

# Gemini
cp -r swe-workflow ~/.gemini/skills/
```

## Structure

```
swe-workflow/
├── SKILL.md                     # Agent-facing entry point (mandatory router/contract)
├── references/                  # Supplementary detail for each workflow phase
│   ├── task-overview-template.md # Task overview skeleton — copy to plan.md verbatim
│   ├── step-template.md         # Per-step file skeleton — copy to steps/step-N.md verbatim
│   ├── code-quality.md          # Reusable code quality bar
│   ├── delegated-guards.md      # Standalone guards for child agents in multi-agent setups
│   ├── checkpoint.md            # Reflect on changes + dump context before pause
│   ├── command-discovery.md      # Validation command discovery
│   ├── risk-classification.md    # Compact risk routing rules
│   ├── project-agents-template.md # Template for target repo AGENTS.md
│   ├── require-clarification.md
│   ├── create-plan.md
│   ├── resume-workflow.md
│   ├── execute-step.md
│   ├── verify-step.md           # Includes Definition of Done
│   ├── persist-plan.md
│   └── global-reflection.md
├── examples/                    # Worked examples and behavioral evaluation cases
│   ├── evaluation-prompts.md    # Expected/forbidden behavior matrix
│   └── plan-example.md          # Current vertical-slice plan example
├── scripts/
│   └── validate.mjs             # Metadata/link/contract regression checks
├── AGENTS.md                    # Repo-level agent instructions / template
├── CHANGELOG.md
├── LICENSE
├── package.json
└── README.md
```

## Production Code Quality Setup

This skill provides the workflow contract. For production codebases, pair it with a project-level `AGENTS.md`.

Recommended setup:

1. Install `swe-workflow`.
2. Copy [`references/project-agents-template.md`](references/project-agents-template.md) into the target repo as `AGENTS.md`.
3. Fill in required commands, architecture rules, API rules, data rules, security rules, testing rules, and do-not-touch areas.
4. Test the setup with [`examples/evaluation-prompts.md`](examples/evaluation-prompts.md).

Keep `SKILL.md` small. Put project-specific rules in the target repo's `AGENTS.md`, not in this skill.

## Verification

Validate the packaged skill contract:

```bash
npm test
npm pack --dry-run
```

Repository validation requires Node.js 18+ and Ruby's standard YAML library (used for full front-matter parsing). `npm test` checks front matter and field types, version alignment, unsupported aliases, internal links, packaged paths, required template fields, Git-safety rules, nested-plan discovery, lifecycle ownership, and two-mode routing.

For behavioral evaluation, run the expected/forbidden cases in [`examples/evaluation-prompts.md`](examples/evaluation-prompts.md) and record the host/model version. A useful vague-request smoke test is:

```text
Add email validation.
```

Expected: start with Lightweight discovery, inspect the existing contract, ask only unresolved decision-critical questions, and escalate to Full before edits only when the resulting implementation meets Full criteria.

## Multi-Agent Handoffs

The task plan and context files are portable across agents. Agent A can complete steps 1–3 and dump context; Agent B reads `plans/context.md` if present, scans `plans/<YYYY-MM-DD>-<slug>/plan.md` and step statuses to find active work, verifies relevant entries in the current workspace, and picks up at step 4.

## Subagent / Multi-Agent Orchestration

This skill supports both **orchestrator** and **delegated child** roles:

| Role | What applies | What's skipped |
|------|-------------|----------------|
| **Orchestrator** (top-level agent, user-facing) | Selects Lightweight or Full; owns escalation, planning, and final verification | Nothing |
| **Delegated child** (focused task from another agent) | Behavioral Guards + Code Quality Bar | Triage block, plan creation, pre-edit gate |

### How it works

When an agent receives a focused task from an orchestrator (not an open-ended user request) with explicit scope and success criteria, it automatically enters **Delegated Mode** — defined in `SKILL.md`. No platform-specific hooks needed; the LLM self-detects based on its context.

### For orchestrator authors

Three options for child agents, from lightest to heaviest:

1. **Inject only `references/delegated-guards.md`** — minimal overhead, standalone file with behavioral guards and code quality bar. Works on any platform that supports injecting text into a child's context.
2. **Inject the full skill** — children self-detect Delegated Mode and skip the ceremony. More tokens but requires no orchestrator-side configuration.
3. **No skill injection** — rely on the orchestrator's task prompt to encode quality expectations. Least overhead, most fragile.

### Platform examples

```bash
# Pi: configure child context to inherit the skill, or inject only the guards file
# Confirm inheritance behavior against the installed orchestration extension/version

# Claude Code: reference in child context
# Cursor: include in child rules
# Codex: include in child system instructions
# Any LLM: paste references/delegated-guards.md into child context
```

## Documentation

- [`SKILL.md`](SKILL.md) — the full agent-facing workflow
- [`CHANGELOG.md`](CHANGELOG.md) — release history
- [`examples/`](examples) — worked example plans

## License

MIT — see [LICENSE](LICENSE).
