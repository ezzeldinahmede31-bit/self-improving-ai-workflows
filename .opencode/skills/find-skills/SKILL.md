---
name: find-skills
description: "Discovers and installs agent skills from the local library, the skills.sh ecosystem, the live web, and GitHub code — then verifies, registers, and adopts them. **User rule (MANDATORY): runs AUTOMATICALLY in the background on EVERY request** — while any task runs, resolve the domain locally, search the ecosystem, escalate to web/GitHub research when needed, and INSTALL silently (never pausing, never asking); report the install in the final answer. Only paid/high-risk (Med/High Socket/Snyk) or huge packs (>5 skills) get a one-line note instead of a blocking question. Also used when the user explicitly asks 'find a skill for X', 'is there a skill for X', 'how do I do X', 'we need a skill for project Y', 'download a skill for X', or 'search GitHub for an implementation of X'."
---

# Find Skills

Discover, verify, install, and adopt skills from every source we own:
local library → skills.sh ecosystem → live web → GitHub code → build in-house.
This skill is a **router, not a researcher**: it wires the specialist skills
below in a fixed ladder and never duplicates what they already do.

## ⚙️ MANDATORY AUTOMATIC BACKGROUND MODE (user rule — runs on EVERY request)

While ANY task runs, resolve the task's domain through the ladder in
§1 (L0 → L4), adopt the first level that yields a working skill, and only
build in-house if nothing exists. Never pause the task, never ask the user.

## 0. Preflight: internet + tooling (30 seconds, every run)

Before any external level, verify the pipes exist. Fail OPEN (degrade, never die):

1. **Ecosystem CLI**: `npx --yes skills --version` must print a version
   (verified: v1.7.2+ works). If npx/node is missing → skip L1, note it.
2. **Web search**: `which parallel-cli` — if present, L2 is live. If absent,
   do NOT install silently on the user's box in background mode; use L2-fallback
   (harness websearch / `curl` for single README fetches) and note
   `parallel-cli-setup` as a one-line suggestion in the final answer.
3. **GitHub**: `gh auth status` — if authenticated, L3 code search is live.
   If not, L3 degrades to unauthenticated `curl https://api.github.com`
   (60 req/hr) + web results; note `gh auth login` in one line.
4. **Offline**: if any step fails with DNS/timeout, drop to L0-only mode,
   finish the task with installed skills, and log one line
   (`find-skills: offline, local-only`). Never block the task on network.

## 1. The discovery ladder (in order, stop at first hit)

### L0 — LOCAL LIBRARY FIRST (user rule: لا تبحث خارجياً عما نملكه بالفعل)

Before ANY external search, scan `memory/skills-library.md` (the generated
one-line index, grouped by family = router registry buckets) for an
already-installed skill that covers the task's domain — grep the family
headers + one-liners for the domain keywords. If a match exists: open its
full doc at `memory/skills-docs/<name>.md`, adopt it for the task, and STOP
(no reinstall, no external search). The router's registry
(`compensatory-router/SKILL.md` → "## Full skill registry") is the same
inventory in bucket form — the library is its fast-lookup one-liner view.
Only when NO installed skill fits do you continue to L1.

### L1 — ECOSYSTEM (`npx skills`, verified working)

1. **Search**: `npx skills find <domain keywords of the current task>`
   (optionally `--owner <org>`). Prefer multi-word queries
   ("react testing" beats "testing").
2. **Qualify**: install count 1K+ AND trusted owner (vercel-labs, anthropics,
   microsoft, obra, pbakaus, mattpocock, etc.). Treat <100 installs with
   suspicion; treat Med/High Socket/Snyk flags as note-only, never silent.
3. If a qualifying skill exists → go to §2 (download + verify + install).
   If the results are thin/ambiguous → escalate to L2 BEFORE deciding
   "nothing exists".

### L2 — LIVE WEB (validates + looks beyond the index)

Wire the two strongest web skills — never raw-guess URLs
(`evidence-over-memory` is mandatory here):

1. **Fast validation** (`parallel-web-search`, DEFAULT): confirm the candidate
   skill/repo actually exists and is maintained — search
   `<skill-name> github stars updated 2026`, open the top result, cite it.
   Also use it to discover skills the index missed
   (`best <domain> claude skill github 2026`).
2. **Deep only on demand** (`parallel-deep-research`, ONLY when the user
   explicitly said 'deep/exhaustive/comprehensive'): full landscape reports,
   comparison matrices, build-vs-buy input for `dont-reinvent-the-wheel`.
3. **Read the evidence** (`firecrawl-scraper` for docs pages, `just-scrape`
   as fallback): pull the candidate's README/docs into the turn and check
   real install steps, requirements, and red flags — never trust the index
   blurb alone. Every factual claim in the final report must carry an inline
   citation (title + URL from tool output, never from memory).

### L3 — GITHUB CODE (when the skill must DO, not just describe)

If L1–L2 yield no ready skill but repos likely implement the capability:

1. **Light discovery** (`github-research` Phases 1–3 only in background mode:
   intake → discovery → ranked top-10; save Phases 4–6 deep dive for explicit
   user asks): `search_github.py --query <capability> --min-stars 50
   --sort stars`, plus Papers-With-Code lookup when the domain is
   paper-driven. Rank by the skill's composite score
   (relevance×0.4 + quality×0.35 + activity×0.25); archived/no-license →
   reject.
2. A top-ranked repo with a usable SKILL.md/package → treat as L1 hit,
   go to §2. A top-ranked repo with reusable code but no skill →
   clone shallow, extract the component, and go to §4 (build in-house
   ON TOP of the extracted code — never from zero when extraction works).

### L4 — MEDIA / FILES (attachments to a skill)

- Video-linked skills (demos, talks): `media-downloader-extractor`
  (yt-dlp) to fetch + transcribe before judging.
- PDF/spec-linked skills: fetch the doc and read it before adopting.

## 2. Download + verify + install (every L1/L3 hit)

1. **Install**: `npx skills add <owner/repo@skill>` (whole-repo
   `npx skills add <owner/repo>` for packs), then copy the new dir(s) from
   the output's `.agents/skills/` into `.opencode/skills/`. For GitHub-code
   hits: shallow-clone to `/tmp`, copy only the skill dir.
2. **Frontmatter check**: `name` == dir slug, `description` present with
   WHAT+WHEN+triggers, valid YAML. Fix silently or reject.
3. **Review against our authoring standards**: run the Review checklist from
   `.opencode/skills/ai-skill-authoring-standards/references/checklists.md`.
   Must pass: no hardcoded secrets, no `subprocess`/`eval`/`exec`/
   `child_process` in included scripts (REJECT — fix or don't adopt),
   content claims match the source read in L2, no exfiltration pattern
   (curl/pastebin/webhook to unknown host). REJECTs get a one-line note.
4. **Smoke test**: load the SKILL.md (read it), confirm its declared
   `allowed-tools`/scripts exist and run (`--help`/`--version` where
   applicable). A skill that fails smoke → note + fall through to the
   next candidate, never adopt blind.
5. **Register in the router (this ALSO adds the library entry)**: run
   `venv/bin/python scripts/router_register.py <installed-skill-name> [...]`
   from the project root. This auto-adds a routing row (marked
   `(Auto-registered)`), appends the skill to the correct family bucket in
   the "## Full skill registry", AND auto-refreshes
   `memory/skills-library.md`. Idempotent — re-runs skip present skills.
6. **Adopt + report**: use the installed skill for the current task, and
   mention the install (source level L0–L4, router-registered + library
   entry) in the final answer in one line. Do NOT come back with
   "should I install X?".
7. **Exceptions that only get a one-line note (never a blocking question)**:
   paid skills, `Med/High` Socket/Snyk risk flags, or packs >5 skills.

## 3. Project-boot mode ("we need skill X for project Y")

When the user frames the ask as a project needing a missing capability,
run the ladder with a project lens and produce a working setup, not a link:

1. L0 → L3 exactly as above, biased toward runnable code over docs.
2. After §2 install: wire the skill into the project's task (imports, config,
   first real call) and prove it runs (test output or artifact in the turn).
3. If L0–L3 all miss → §4, then wire + prove the same way.
4. Final answer states: skill name, source, what project step it now
   powers, and the proof (one line + evidence).

## 4. If no qualifying match exists — CREATE via OUR gates

(user rule: لا نخلق عجلة ولا نترك الحاجة ناقصة — build on top of L2/L3
findings, especially `best-practice-first-designer` + `dont-reinvent-the-wheel`
research already done for the task):

1. Write the new skill at `.opencode/skills/<slug>/SKILL.md` following the
   house style (valid YAML frontmatter with `name` + `description` + trigger
   phrases, purpose, steps, verification, pairs-with).
2. Run it through the gates:
   `venv/bin/python scripts/build_gates_pipeline.py .opencode/skills/<slug>/SKILL.md --no-hitl`.
   Must reach `READY_FOR_DEPLOYMENT` (exit 0). Fix violations, re-run.
3. Register: `venv/bin/python scripts/router_register.py <slug>`.
4. Adopt + report in one line (created in-house, gates-passed,
   router-registered, library entry added).
   Only skip gates if the tooling can't parse the artifact — then at minimum
   re-validate frontmatter YAML and note the exemption.

## 5. Verification (how the agent KNOWS it worked)

- [ ] L0 hit → named installed skill opened from `memory/skills-docs/` and used.
- [ ] L1/L3 hit → `npx skills add` (or clone) output exists, dir copied under
      `.opencode/skills/`, frontmatter valid, Review checklist passed, smoke
      test green, `router_register.py` re-ran clean, skill used in-task.
- [ ] L2 used → every external claim in the report has an inline citation.
- [ ] §4 path → gates exit 0 (`READY_FOR_DEPLOYMENT`) + registered + used.
- [ ] Offline → one-line `local-only` note exists, task still completed.
- [ ] Final answer contains the one-line install/adopt report (or the
      note-only exception). No silent adoptions, no unverified adoptions.

## When to Use This Skill (explicit user ask)

Use this skill when the user:

- Asks "how do I do X" where X might be a common task with an existing skill
- Says "find a skill for X", "is there a skill for X", or "download a skill for X"
- Says "we need a skill/capability for project Y" (→ §3 project-boot mode)
- Asks "can you do X" where X is a specialized capability
- Asks to search GitHub for an implementation of X (→ L3)
- Expresses interest in extending agent capabilities
- Wants to search for tools, templates, or workflows
- Mentions they wish they had help with a specific domain

## Pairs with

- `ai-skill-authoring-standards` — Review checklist on every install; design/build checklists on every §4 create.
- `compensatory-router` — the registry this skill feeds via `router_register.py`.
- `parallel-web-search` — L2 fast validation/discovery (DEFAULT web skill).
- `parallel-deep-research` — L2 deep landscape, only on explicit 'deep' asks.
- `firecrawl-scraper` / `just-scrape` — L2 evidence reading (docs/README extraction).
- `github-research` — L3 code discovery, scoring, extraction (Phases 1–3 in background).
- `media-downloader-extractor` — L4 video-linked skill evidence.
- `evidence-over-memory` — no invented URLs/counts, citations on every claim.
- `dont-reinvent-the-wheel` + `best-practice-first-designer` — build-vs-buy + baseline before any §4 create.
- `build-gates-pipeline` — §4 gate pass before any created skill ships.
