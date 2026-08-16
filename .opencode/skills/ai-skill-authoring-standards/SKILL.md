---
name: ai-skill-authoring-standards
description: "The GLOBAL standards gate for creating, reviewing, designing, and building ANY AI agent skill in this workspace. MANDATORY on every skill action: whenever a new skill is designed, written, installed (incl. find-skills background installs and gate-complaints auto-created skills), edited, or reviewed, this skill supplies the world-wide best practices (frontmatter rules, progressive disclosure <500 lines, trigger-rich descriptions, single-purpose scoping, versioning, real-task testing, data-trust, security against the 26% vulnerable-community-skills rate) and runs the design + build + review checklists. It also OWNS the daily auto-evolution loop: scripts/ai_skill_standards_updater.py polls trusted sources (Anthropic docs, agentskills.io, mgechev/skills-best-practices, neon frontmatter spec, skills.sh) every day via cron and updates references/standards-2026.md automatically — no user follow-up needed. Trigger phrases: 'اعمل مهارة جديدة', 'ابني مهارة', 'design a skill', 'build a skill', 'create a skill', 'skill standards', 'skill checklist', 'راجع المهارة', 'review this skill', 'هذه المهارة صح ولا لأ', 'global standards for skills', 'install a new skill', 'is this skill good'. Pairs with: find-skills, build-gates-pipeline, router_register.py, gate_complaints.py, writing-skills (obra/superpowers)."
---

# AI Skill Authoring Standards

The world-wide standards + mechanical checklists that EVERY skill in this
workspace must satisfy — design, build, and review — plus the daily
auto-evolution loop that keeps the standards current from trusted sources.

## When to use

Use on ANY skill action, without exception:
- User asks to create/design/build a skill (`اعمل مهارة`, `build a skill`).
- User asks to review/validate a skill (`راجع المهارة`, `is this skill good`).
- find-skills installs a skill in the background → run the review checklist on
  it BEFORE adopting.
- The build-gates COMPLAINTS stage auto-creates a skill → pass it through the
  design + build checklists.
- You are about to register a skill in the router.

## The full standards

`references/standards-2026.md` — the distilled global standards (frontmatter
rules, the 6 best practices, security, skill smells, trusted source registry,
house rules). Load it. It is refreshed daily by the updater; if the file is
newer than your knowledge, trust the file (evidence over memory).

## The checklists

`references/checklists.md` — Design / Build / Review / Verdict checklists.
Load and run ALL of them on the skill in question.

## Process (design → build → review → evolve)

### 1. DESIGN
1. Load `references/standards-2026.md` + `references/checklists.md`.
2. Confirm single-purpose scope; dedupe against `.opencode/skills/` and the
   router registry (no duplicate skill).
3. Draft name (lowercase, hyphens, ≤64 chars, = directory) and a trigger-rich
   `description` in the `[what it does]. Use when [triggers].` formula.
4. Plan progressive disclosure: what lives in SKILL.md (≤500 lines) vs
   `references/` vs `scripts/`.
5. Name the data it reads and confirm freshness/ownership (practice 6).
6. If side effects exist, plan `disable-model-invocation: true` + a confirm gate.

### 2. BUILD
1. Write `.opencode/skills/<slug>/SKILL.md` in house style (Purpose / When to
   use / Steps numbered / Verification / Pairs-with; valid YAML frontmatter
   with name + description).
2. Link (never inline) long reference files; keep SKILL.md lean.
3. Include a verification step — how will the agent KNOW it worked?
4. Run it against at least ONE real scenario and keep the evidence.

### 3. REVIEW (mandatory before any adopt/install/deliver)
Run the full Review checklist from `references/checklists.md`: frontmatter
validity, description quality, secret scan (sk-/api key/password/token),
tool-grant tightness, owner trust (official org + 1K+ installs), dedupe,
dead references, version/changelog, real-scenario proof. Any security failure
→ REJECT and fix before adopt.

### 4. GATES + REGISTER (project house rules)
1. `venv/bin/python scripts/build_gates_pipeline.py .opencode/skills/<slug>/SKILL.md --no-hitl`
   → must reach VERDICT READY_FOR_DEPLOYMENT (exit 0). Fix violations, re-run.
2. `venv/bin/python scripts/router_register.py <slug>` — adds the routing row
   (marked `(Auto-registered)`) + registry bucket entry + bumps the total.
3. If the skill failed review on a gap no installed skill covers, log it to
   `scripts/gate_complaints.py` (SKILL_GAP) so find-skills resolves it.

### 5. EVOLVE (daily, automatic — this is the user's key requirement)
The standards never go stale on their own. `scripts/ai_skill_standards_updater.py`
runs daily via user cron (see step 6 below) and:
1. Fetches the trusted source registry (Anthropic docs, agentskills.io,
   mgechev README, neon AGENTS.md, skills.sh, etc.).
2. Extracts the standards text, hashes it, compares to the stored snapshot.
3. Content unchanged → no-op (stable between real upstream changes).
4. Content changed → rewrites `references/standards-2026.md` from the new
   source text + appends `memory/ai-skill-standards/changelog.md` + keeps the
   prior version under `memory/ai-skill-standards/history/`.
5. Sources unreachable → keeps current standards, logs the failure, exits
   cleanly (fail-open offline, never corrupts the standards).
6. Reports one line to the next session via the changelog.

### 6. INSTALL THE DAILY CRON (do once)
```bash
# register the daily job (already done by this skill's install unless removed)
crontab -l 2>/dev/null | grep -q ai_skill_standards_updater.py || \
  (crontab -l 2>/dev/null; echo "0 5 * * * cd '/home/ezzeldin/Documents/Default Project' && './venv/bin/python' scripts/ai_skill_standards_updater.py --cron >> memory/ai-skill-standards/updater.log 2>&1") | crontab -
```
Manual run any time: `venv/bin/python scripts/ai_skill_standards_updater.py`.

## Verification

- `venv/bin/python scripts/ai_skill_standards_updater.py` exits 0 and prints
  FRESH (or UPDATED vN) — proves the auto-evolution loop is alive.
- `crontab -l | grep ai_skill_standards_updater` shows the daily job.
- The skill being reviewed passed `build_gates_pipeline.py` with READY_FOR_DEPLOYMENT
  and is registered in the router.
- `references/standards-2026.md` frontmatter-free markdown parses; changelog
  grows on real upstream change, not on every poll.

## Pairs with

- `find-skills` — route every background install through this review checklist.
- `build-gates-pipeline` — the SECURITY/QUALITY gates that make READY_FOR_DEPLOYMENT real.
- `scripts/router_register.py` — auto-registration of newly built skills.
- `scripts/gate_complaints.py` — complaints ledger for skill-quality gaps.
- `writing-skills` (obra/superpowers) — the plan→review discipline for authoring.
- `long-term-memory-retriever` — record the changelog in memory at session end.
