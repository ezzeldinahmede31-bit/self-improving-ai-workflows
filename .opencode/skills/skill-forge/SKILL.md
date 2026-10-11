---
name: skill-forge
description: "Builds production-ready skills FOR THIS workspace by orchestrating the world's best skill-building tools: Anthropic skill-creator (eval/benchmark engines), obra writing-skills (TDD), Skill_Seekers (docs-to-draft), plus house gates and router registration. Fixes the known public complaints (silent benchmarks, non-triggering descriptions, stale indexes). Use when the user says 'ابني مهارة', 'اعمل skill', 'build a skill', 'forge a skill', 'skill from docs', 'evaluate my skill', 'benchmark this skill', or 'why doesn't my skill trigger'."
---

# Skill Forge

The workspace-native skill factory. It does NOT re-implement what the top-10
world tools already do — it **orchestrates** them and adapts their output to
this workspace (`.opencode/skills/` layout, house gates, router + library),
with deterministic scripts that fix the complaints people report about those
tools. Even a tool built for Claude is bent here to build for US with the
same features.

## The 10 sources (downloaded + verified 2026-10-11, in `/tmp/skillforge-sources/`)

| # | Tool | Role in the forge |
|---|------|-------------------|
| 1 | `anthropics/skill-creator` (official plugin) | Eval/Improve/Benchmark ENGINES: `run_eval`, `aggregate_benchmark`, `improve_description`, 4 agents (Executor/Grader/Comparator/Analyzer), eval-viewer |
| 2 | `obra/superpowers writing-skills` (installed) | METHOD: TDD-for-skills — baseline RED (agent fails w/o skill) → GREEN (complies) → refactor loopholes |
| 3 | `Skill_Seekers` v3.10.0, isolated venv `/tmp/sf-venv` (15K stars) | DOCS→DRAFT engine: 18 source types → skill draft + conflict detection (`create --target opencode`-family flow, review output before adopt) |
| 4 | VSCode Claude Skills Toolkit (DavidFarris) | FEATURES merged: interactive Q&A intake, health-check, trust-scan, ZIP packaging, sync-to-folder |
| 5 | `01clauding/claude-skill-generator` | Factory pattern: /build flows + auto-validate + auto-ZIP |
| 6 | `metaskills/skill-builder` | Templates + `converting-sub-agents-to-skills` pattern |
| 7 | `ruvnet/ruflo` skill-builder spec (910 lines) | Full-spec reference for frontmatter/progressive-disclosure rules |
| 8 | `martinholovsky` generator | Domain-pack pattern (setup scripts that install skill bundles) |
| 9 | agentskills.io + Anthropic frontmatter spec | LAW: spec-six fields, 1536-char listing cap, packaging rules |
| 10 | NVIDIA eval tiers + Academy troubleshooting | METHOD: `evals.json` tiers + trigger-fix ladder (description → load → conflict → runtime) |

## Complaints people report → how the forge fixes them

1. **Silent benchmark failures** ([skill-creator #1383]: layout mismatch, inverted delta, pipe crash) → `forge_benchmark.py` asserts non-empty inputs (loud fail) and fixes delta sign as with-minus-without; single canonical layout enforced by `forge_validate.py`. POSIX-only; no `select()`-on-pipes.
2. **Skills never trigger** (budget overflow drops descriptions; ~50% auto-trigger) → `forge_eval.py` trigger battery (coverage ≥0.80 required) + description budget guard (≤1024 chars) + pushy-description rule.
3. **Vague descriptions** → eval misses print exact suggested additions; max 2 improve iterations, then human wording.
4. **Stale indexes** (skills.sh listed a removed skill — seen live) → L2 live-verify before adopt (reuse `find-skills` ladder); never adopt blind.
5. **Context bloat, no unload** → progressive disclosure enforced (body ≤500 lines, refs linked not inlined).
6. **Faith-based shipping** → no library entry without eval PASS + gates READY_FOR_DEPLOYMENT.

## Pipeline (run in order, stop on first red)

0. **Intake** (VSCode-toolkit pattern): 3-6 questions — WHAT the skill does, WHEN it triggers (exact user phrasings, Arabic+English), what DONE looks like, what it must NEVER do. Write answers down; they become the eval battery.
1. **Draft** — pick ONE source mode:
   - **from-scratch**: write draft SKILL.md in house style (purpose/steps/verification/pairs-with).
   - **from-docs** (Skill_Seekers): `/tmp/sf-venv/bin/skill-seekers create <url|repo|pdf> --target claude` then ADAPT output: move SKILL.md to `.opencode/skills/<slug>/`, rewrite paths/frontmatter to house style, delete Claude-only upload bits. Review every generated claim (seekers output is a draft, not truth).
   - **from-repo** (metaskills pattern): extract a working component + wrap with trigger-rich SKILL.md.
2. **Validate**: `venv/bin/python .opencode/skills/skill-forge/scripts/forge_validate.py .opencode/skills/<slug>` → must print VALID (exit 0). Fix, re-run.
3. **Eval (obra TDD-lite)**: write `phrases.txt` (5-15 real phrasings from intake, incl. Arabic ones), run `forge_eval.py <dir> phrases.txt` → PASS (coverage ≥0.80). Baseline check: confirm NO installed skill already covers it (`find-skills` L0) — RED proof.
4. **Benchmark** (skill-creator engine pattern): collect `with.jsonl` / `without.jsonl` (LLM-as-judge runs in-turn, skill-creator Grader), run `forge_benchmark.py` → delta_pass_rate ≥ 0 required for library entry.
5. **Improve** (max 2 rounds): eval misses → sharpen description → re-run steps 2-4.
6. **Gates + register**: `build_gates_pipeline.py <SKILL.md> --no-hitl` → READY_FOR_DEPLOYMENT; `router_register.py <slug>` (adds library entry). `.gates-ack.json` sidecar only for reviewed false positives.
7. **Adopt + report**: use the skill once in a real turn; one-line report (source mode, eval score, delta, registered).

## Verification (agent KNOWS it worked when)

- [ ] `forge_validate.py` prints VALID (exit 0).
- [ ] `forge_eval.py` prints PASS with coverage number.
- [ ] `forge_benchmark.py` wrote `benchmark.json/md` with signed delta (no silent empties).
- [ ] Gates verdict READY_FOR_DEPLOYMENT; router row + library entry exist.
- [ ] The skill was invoked successfully in one real turn (evidence quoted).

## Pairs with

- `skill-creator` — deep eval/improve/benchmark engines this pipeline drives.
- `writing-skills` — TDD discipline behind step 3.
- `find-skills` — L0 dedupe + L2 live-verify; adopts finished skills.
- `ai-skill-authoring-standards` — checklists behind the validator.
- `build-gates-pipeline` + `router_register.py` — ship + register.
