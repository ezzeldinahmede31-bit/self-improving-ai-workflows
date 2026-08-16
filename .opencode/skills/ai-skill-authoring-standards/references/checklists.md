# Design / Build / Review Checklists for AI Skills

Mechanical, pass/fail checklists derived from the global standards
(`references/standards-2026.md`). Run ALL THREE on every skill you design,
build, or review — including skills installed in the background by find-skills
and skills auto-created by the gate-complaints pipeline.

## A. Design checklist (before writing a line)

- [ ] ONE capability only (single-purpose). If the ask has 2 distinct jobs,
      split or design a router.
- [ ] Name chosen: lowercase, hyphens, ≤64 chars, matches the future directory.
- [ ] Who triggers it? Draft the 3-6 exact user phrasings that must load it.
- [ ] Is there already an installed skill covering the same triggers? If yes,
      extend it instead of duplicating (dedupe check against
      `.opencode/skills/` + router registry).
- [ ] What data does it read at runtime? Is that data fresh, owned, certified?
      (Practice 6 — the one most guides skip.)
- [ ] Which tools does it need? Smallest tightest set; can it run read-only?
- [ ] Progressive-disclosure plan: what stays in SKILL.md vs `references/` vs
      `scripts/`? Target ≤500 lines / ~5K tokens for SKILL.md.
- [ ] Side effects? If it deploys/commits/deletes/calls external APIs, plan
      `disable-model-invocation: true` + a confirmation gate.

## B. Build checklist (authoring)

- [ ] Frontmatter `name` matches directory, lowercase+hyphens, ≤64 chars.
- [ ] Frontmatter `description` ≤1024 chars, states WHAT + WHEN, trigger-rich,
      third person, specific (never "Helper for X").
- [ ] Optional fields used only when justified (`allowed-tools` tight,
      `license`, `metadata.version`, `user-invocable`, `paths`, `context: fork`).
- [ ] Body is structured: Purpose / When to use / Steps (numbered) /
      Verification / Pairs-with. No prose bloat, no code comments, no secrets.
- [ ] Any long reference lives in `references/` and is LINKED not inlined.
- [ ] A verification step exists in the body (how does the agent KNOW it worked?).
- [ ] No absolute paths that break on another machine; relative to skill dir.
- [ ] Tested against at least one REAL scenario (run it, show evidence).

## C. Review checklist (every install / every delivery)

Frontmatter:
- [ ] Valid YAML (parse without errors).
- [ ] `name` present and matches directory.
- [ ] `description` present, non-vague, has trigger phrases, ≤1024 chars.
- [ ] No `description` longer than the body (marketing-flavored smell).

Security:
- [ ] No hardcoded secrets/tokens/keys anywhere in the skill (scan for
      `sk-`, `api[_-]?key`, `secret`, `password`, `token`, private keys).
- [ ] No unbounded tool grants (`Bash(*)`, `Read(*)`, `Bash` alone) without
      justification.
- [ ] Owner/repo trustworthy (official org, 1K+ installs, stars sane).
- [ ] No exfiltration pattern (curl/pastebin/webhook to unknown host).

Correctness / hygiene:
- [ ] One purpose only (no scope creep).
- [ ] No duplicate of an installed skill (dedupe vs `.opencode/skills/`).
- [ ] No dead references (every linked file exists).
- [ ] Version + changelog present if it will change over time.
- [ ] Verification step present; real-scenario proof attached where possible.

Project gates:
- [ ] Passed `build_gates_pipeline.py` → READY_FOR_DEPLOYMENT (exit 0).
- [ ] Registered in the router (`scripts/router_register.py <slug>`).
- [ ] No secrets left in memory/audits or chat transcripts.

## D. Verdict

All checkboxes ticked → ADOPT.
Any Security box fails → REJECT / FIX before adopt (never adopt a skill with
a hardcoded secret or unbounded tool grant).
Any non-security box fails → fix the one item and re-check, then adopt.

When a checklist item reveals a gap that no installed skill fixes, record it
in the per-gate complaints ledger (`scripts/gate_complaints.py`) so find-skills
can auto-install or auto-create a fixing skill — this skill (the standards
skill) is the designated owner of that loop for skill-quality complaints.
