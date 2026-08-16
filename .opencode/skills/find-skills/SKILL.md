---
name: find-skills
description: "Helps discover and install agent skills. **User rule (MANDATORY): runs AUTOMATICALLY in the background on EVERY request** — while any task runs, search skills.sh for a better off-the-shelf skill for the task's domain and INSTALL it silently (npx skills add, then copy to .opencode/skills/), never pausing the task or asking the user; report the install in the final answer. Only paid/high-risk (Med/High Socket/Snyk) or huge packs (>5 skills) get a one-line note instead of a blocking question. Also used when the user explicitly asks 'find a skill for X', 'is there a skill for X', or 'how do I do X'."
---

# Find Skills

This skill helps you discover and install skills from the open agent skills ecosystem.

## ⚙️ MANDATORY AUTOMATIC BACKGROUND MODE (user rule — runs on EVERY request)

While ANY task runs, resolve the task's domain against the LOCAL skill library
first, then search the open ecosystem, and only build in-house if nothing exists.
Never pause the task, never ask the user.

0. **LOCAL LIBRARY FIRST (user rule: المكتبة موجودة جوا الرواتر — لا تبحث خارجياً عما
   نملكه بالفعل)**: before ANY external search, scan `memory/skills-library.md`
   (the generated one-line index, grouped by family = router registry buckets)
   for an already-installed skill that covers the task's domain — grep the
   family headers + one-liners for the domain keywords. If a match exists:
   open its full doc at `memory/skills-docs/<name>.md`, adopt it for the task,
   and STOP (no reinstall, no external search). The router's registry
   (`compensatory-router/SKILL.md` → "## Full skill registry") is the same
   inventory in bucket form — the library is its fast-lookup one-liner view.
   Only when NO installed skill fits do you continue to step 1.
1. **Search**: `npx skills find <domain keywords of the current task>`
2. **Qualify**: install count 1K+ AND trusted owner (vercel-labs, anthropics,
   microsoft, obra, pbakaus, mattpocock, etc.). Treat <100 installs with suspicion.
3. **Install silently**: `npx skills add <owner/repo@skill>` (whole-repo `npx skills add <owner/repo>` for packs), then copy the new dir(s) from the output's `.agents/skills/` into `.opencode/skills/`, re-check frontmatter (name + description present, valid YAML).
4. **Review against our authoring standards**: before adopting, run the Review checklist from `.opencode/skills/ai-skill-authoring-standards/references/checklists.md` on the installed skill. Must pass: valid YAML frontmatter (`name` == dir slug, `description` with WHAT+WHEN+trigger phrases), no hardcoded secrets, no `subprocess`/`eval`/`exec`/`child_process` in any included scripts (a skill with those is REJECT — fix or don't adopt), content claims match the checked source. REJECTs get a one-line note; fixes are applied silently before adopting.
5. **Register in the router (this ALSO adds the library entry)**: after copying, run `venv/bin/python scripts/router_register.py <installed-skill-name> [...]` from the project root. This auto-adds a routing row (marked `(Auto-registered)`) to the proactive-stack table, appends the skill to the correct family bucket in the "## Full skill registry" section (bumping the total), AND auto-refreshes `memory/skills-library.md` so the skill gets its one-liner entry in the same family. Idempotent — re-runs skip already-present skills. This is what makes every newly installed skill reachable by the router AND searchable via the library on later requests.
6. **Adopt + report**: use the installed skill for the current task, and mention the install (and that it was router-registered + added to the library) in the final answer in one line. Do NOT come back with "should I install X?".
7. **Exceptions that only get a one-line note (never a blocking question)**: paid skills, `Med/High` Socket/Snyk risk flags, or packs larger than 5 skills.
8. **If no qualifying match exists — CREATE the skill via OUR gates** (user rule: لا نخلق عجلة ولا نترك الحاجة ناقصة): build the missing skill ourselves, then pass it through the project's build gates before registering it in the router (registration auto-adds the library entry):
   1. Write the new skill at `.opencode/skills/<slug>/SKILL.md` following the house style (valid YAML frontmatter with `name` + `description` + trigger phrases, purpose, steps, verification, pairs-with). Base it on the best-practice-first-designer research pass already done for the task.
   2. Run it through the gates: `venv/bin/python scripts/build_gates_pipeline.py .opencode/skills/<slug>/SKILL.md --no-hitl`. Must reach `READY_FOR_DEPLOYMENT` (exit 0). Fix any SECURITY / QUALITY / INTEGRITY / REASONING violations and re-run until green.
   3. Register it in the router: `venv/bin/python scripts/router_register.py <slug>` (adds the routing row + registry entry, bumps total, auto-refreshes `memory/skills-library.md`).
   4. Adopt + report it in one line (mention it was created in-house, gates-passed, router-registered, and added to the library).
   Only skip the gates pass for the (rare) case where the gate tooling itself can't parse the artifact — then at minimum re-validate frontmatter YAML and note the exemption in the report.

## When to Use This Skill (explicit user ask)

Use this skill when the user:

- Asks "how do I do X" where X might be a common task with an existing skill
- Says "find a skill for X" or "is there a skill for X"
- Asks "can you do X" where X is a specialized capability
- Expresses interest in extending agent capabilities
- Wants to search for tools, templates, or workflows
- Mentions they wish they had help with a specific domain (design, testing, deployment, etc.)

## What is the Skills CLI?

The Skills CLI (`npx skills`) is the package manager for the open agent skills ecosystem. Skills are modular packages that extend agent capabilities with specialized knowledge, workflows, and tools.

**Key commands:**

- `npx skills find [query] [--owner <owner>]` - Search for skills interactively or by keyword, optionally scoped to a GitHub owner
- `npx skills add <package>` - Install a skill from GitHub or other sources
- `npx skills update` - Update all installed skills

**Browse skills at:** https://skills.sh/

## How to Help Users Find Skills

### Step 1: Understand What They Need

When a user asks for help with something, identify:

1. The domain (e.g., React, testing, design, deployment)
2. The specific task (e.g., writing tests, creating animations, reviewing PRs)
3. Whether this is a common enough task that a skill likely exists

### Step 2: Check the Leaderboard First

Before running a CLI search, check the [skills.sh leaderboard](https://skills.sh/) to see if a well-known skill already exists for the domain. The leaderboard ranks skills by total installs, surfacing the most popular and battle-tested options.

For example, top skills for web development include:
- `vercel-labs/agent-skills` — React, Next.js, web design (100K+ installs each)
- `anthropics/skills` — Frontend design, document processing (100K+ installs)

### Step 3: Search for Skills

If the leaderboard doesn't cover the user's need, run the find command:

```bash
npx skills find [query] [--owner <owner>]
```

For example:

- User asks "how do I make my React app faster?" → `npx skills find react performance`
- User asks "can you help me with PR reviews?" → `npx skills find pr review`
- User asks "I need to create a changelog" → `npx skills find changelog`

### Step 4: Verify Quality Before Recommending

**Do not recommend a skill based solely on search results.** Always verify:

1. **Install count** — Prefer skills with 1K+ installs. Be cautious with anything under 100.
2. **Source reputation** — Official sources (`vercel-labs`, `anthropics`, `microsoft`) are more trustworthy than unknown authors.
3. **GitHub stars** — Check the source repository. A skill from a repo with <100 stars should be treated with skepticism.

### Step 5: Present Options to the User

When you find relevant skills, present them to the user with:

1. The skill name and what it does
2. The install count and source
3. The install command they can run
4. A link to learn more at skills.sh

Example response:

```
I found a skill that might help! The "react-best-practices" skill provides
React and Next.js performance optimization guidelines from Vercel Engineering.
(185K installs)

To install it:
npx skills add vercel-labs/agent-skills@react-best-practices

Learn more: https://skills.sh/vercel-labs/agent-skills/react-best-practices
```

### Step 6: Offer to Install

If the user wants to proceed, you can install the skill for them:

```bash
npx skills add <owner/repo@skill> -g -y
```

The `-g` flag installs globally (user-level) and `-y` skips confirmation prompts.

## Common Skill Categories

When searching, consider these common categories:

| Category        | Example Queries                          |
| --------------- | ---------------------------------------- |
| Web Development | react, nextjs, typescript, css, tailwind |
| Testing         | testing, jest, playwright, e2e           |
| DevOps          | deploy, docker, kubernetes, ci-cd        |
| Documentation   | docs, readme, changelog, api-docs        |
| Code Quality    | review, lint, refactor, best-practices   |
| Design          | ui, ux, design-system, accessibility     |
| Productivity    | workflow, automation, git                |

## Tips for Effective Searches

1. **Use specific keywords**: "react testing" is better than just "testing"
2. **Try alternative terms**: If "deploy" doesn't work, try "deployment" or "ci-cd"
3. **Check popular sources**: Many skills come from `vercel-labs/agent-skills` or `ComposioHQ/awesome-claude-skills`

## When No Skills Are Found

If no relevant skills exist:

1. Acknowledge that no existing skill was found
2. Offer to help with the task directly using your general capabilities
3. Suggest the user could create their own skill with `npx skills init`

Example:

```
I searched for skills related to "xyz" but didn't find any matches.
I can still help you with this task directly! Would you like me to proceed?

If this is something you do often, you could create your own skill:
npx skills init my-xyz-skill
```
