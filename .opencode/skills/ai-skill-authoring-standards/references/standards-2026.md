# Global Standards for AI Skill Authoring — 2026 snapshot

> Maintained automatically by `scripts/ai_skill_standards_updater.py` (daily).
> This file is the distilled, load-bearing core of the standards skill. Sources
> below are the TRUSTED list the updater polls; every entry cites its source.
> Do not edit by hand unless the updater is broken — the updater overwrites it.

## 0. Why these standards exist (the evidence)

- A 2026 UC Irvine study of 238 real skills found 99% carry at least one flaw a
  routine review catches (overlong SKILL.md, vague description, no versioning,
  untested, single-purpose violation).
- 26.1% of community skills carry a vulnerability; one fake skill reached
  26,000 installs before being removed (security trust layer research).
- A skill with a vague description is dead regardless of content — it never
  triggers, so it never helps.
- A bloated SKILL.md competes for the same context budget as the task itself;
  conciseness is a scarce resource the author must spend carefully.

## 1. Frontmatter — required fields

From the Agent Skills spec + Claude Platform Docs + neon agent-skills repo:

- `name` — REQUIRED. Max 64 chars. Lowercase letters, numbers, hyphens. MUST
  match the directory name exactly (folder fallback is fragile — always set it).
- `description` — REQUIRED. Max 1024 chars (Claude listing cap ~1536 with
  `when_to_use`). Must say (a) WHAT the skill does and (b) WHEN to use it, with
  explicit trigger phrases. Third person, keyword-specific, specific — never
  vague.

The description formula that works:
```
[verb-phrase: what it does]. Use when the user says "trigger1", "trigger2", or "trigger3".
```

Descriptions that FAIL (anti-patterns): `"Helper for releases"`, `"Use this skill when needed"`,
`"Deploys things"` — no triggers, no specifics, invisible to any router.

## 2. Frontmatter — optional fields (use when justified)

- `when_to_use` — extra trigger phrases appended to description (keep human
  description short + long trigger list here).
- `license` — e.g. Apache-2.0, MIT (required for publishing to a registry).
- `compatibility` — e.g. "Requires git, docker, and network access".
- `metadata: {author, version}` — versioning + ownership.
- `allowed-tools` — comma-separated tool allowlist; scope TIGHTLY
  (`Bash(git log:*)` not `Bash`). Reduces friction + hardens.
- `user-invocable: false` — hide from slash menu (silent knowledge skills).
- `disable-model-invocation: true` — MANDATORY for any skill with side effects
  (deploys, commits, deletes, external API calls): force explicit invocation.
- `model` / `effort` — override model + thinking budget ONLY when justified;
  most skills should inherit from the session.
- `context: fork` + `agent: <type>` — run read-heavy/exploratory skills in an
  isolated subagent to keep main context lean.
- `paths` — auto-load only on glob match (e.g. `**/*.tsx`).
- `hooks` — PreToolUse/PostToolUse/Stop lifecycle hooks.
- `argument-hint` / `arguments` — named positional args for slash UX.

## 3. The 6 global best practices (Anthropic + agentskills.io + Atlan 2026)

1. **Progressive disclosure** — keep SKILL.md under ~500 lines / ~5,000 tokens;
   push detail ONE level deep into `references/` and `scripts/`; link, never
   inline. A first-time reader must find the reasoning without opening every file.
2. **Discoverable descriptions** — the description is a discovery trigger, not a
   label. Third person, trigger-rich, "Use when".
3. **Single-purpose scoping** — one skill = one capability. Over-broad skills are
   hard to activate and drag wrong context. If a task has two distinct jobs,
   split into two skills (or one skill + a router).
4. **Versioning** — `metadata.version`, a CHANGELOG entry, and rollback ability.
   Without it a regressed skill cannot be reverted.
5. **Testing against real tasks** — a skill that has never run a real scenario
   fails silently. Keep `tests/` or documented live proof; run the scenario
   before declaring done.
6. **Validate data trustworthiness** — a flawless skill run against stale or
   uncertified data is still wrong. Name data ownership + freshness; fetch live
   or pin + version the data.

## 4. Security standards (OWASP-adjacent, trust-layer research)

- NEVER hardcode secrets/tokens/keys into a SKILL.md, script, or reference —
  use an env var / credential vault / `.env` (gitignored) reference instead.
- Prefer official/trusted owners (anthropics, vercel-labs, microsoft, n8n-io,
  zapier, firebase, better-auth, getsentry, obra...) when installing.
- Review any skill whose source repo has <100 stars or <1K installs with
  skepticism; run a scan for hardcoded secrets and risky tool grants
  (`allowed-tools` of `Bash`/`Bash(*)`/`Read(*)` need a justification).
- Skills that execute code must fail closed and never exfiltrate; the project's
  `build_gates_pipeline.py` SECURITY gate enforces the same rules on SKILL.md.
- New capability = new attack surface. Log installs in the skill ledger so a
  supply-chain incident is traceable.

## 5. Skill "smells" to avoid (arXiv skill-smells taxonomy, 26 named smells)

Representative top smells: description/length mismatch (marketing-flavored
description on a tiny body), dead references, duplicate skills (two skills
covering the same trigger), brittle absolute paths, no verification step,
no license, no version, unbounded tool grants, hardcoded secrets. The
review checklist flags each mechanically.

## 6. Trusted source registry (what the daily updater polls)

| Source | URL |
|---|---|
| Anthropic — Skill authoring best practices | https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices |
| Anthropic — Equipping agents with skills (engineering) | https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills |
| agentskills.io — best practices for skill creators | https://agentskills.io/skill-creation/best-practices |
| mgechev/skills-best-practices (GitHub, 2.2K★) | https://raw.githubusercontent.com/mgechev/skills-best-practices/main/README.md |
| neon database — AGENTS.md frontmatter spec | https://raw.githubusercontent.com/neondatabase/agent-skills/main/AGENTS.md |
| Claude Code frontmatter reference (all 15 fields) | https://allahabadi.dev/blogs/ai/claude-code-skills-frontmatter-complete-guide |
| skills.sh directory | https://skills.sh/ |
| Atlan — agent skill best practices 2026 | https://atlan.com/know/ai-agent/ai-agent-skills/agent-skill-best-practices/ |

The updater fetches these, extracts the standards text, hashes it, and only
rewrites this file when the content changed — so the skill evolves on its own
while staying stable between real upstream changes.

> Auto-maintained by `scripts/ai_skill_standards_updater.py`; last run 2026-08-15 05:39:34 — 4/4 sources reachable (unreachable: none).
