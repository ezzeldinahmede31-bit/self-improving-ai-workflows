#!/usr/bin/env python3
"""MonkeyCode bridge sync.

Regenerates the MonkeyCode-facing surface of this workspace so that when the
project is opened in MonkeyCode (chaitin/baizhi.cloud) everything is available
and stays in sync with the working tree:

  AGENTS.md                     - entry point: orientation + standing user rules
  .monkeycode/MEMORY.md         - distilled project memory (pointer to full file)
  .ai-ready/rules/*.md          - user's standing rules as rule files
  .ai-ready/skills -> ../.opencode/skills   (relative symlink: all skills)
  .monkeycode-ai/README.md      - config note for the .monkeycode-ai directory

Then commits via git (add + commit; push only if an upstream exists). Safe to
run on every hook: regeneration is deterministic and idempotent. Run with
--quiet when called from another script so hooks stay silent on success.

Usage:
    venv/bin/python scripts/monkeycode_sync.py [--quiet] [--no-git]
"""
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MEM_MD = ROOT / "memory" / "conversation-memory.md"
SKILLS_DIR = ROOT / ".opencode" / "skills"
AI_READY = ROOT / ".ai-ready"
AI_SKILLS_LINK = AI_READY / "skills"
MEMORY_LINE_LIMIT = 150

QUIET = "--quiet" in sys.argv
NO_GIT = "--no-git" in sys.argv


def log(msg: str) -> None:
    if not QUIET:
        print(msg)


def grab_section(src: str, title: str) -> list[str]:
    m = re.search(rf"^## {re.escape(title)}\s*$(.*?)(?=^## |\Z)", src, re.M | re.S)
    if not m:
        return []
    return [ln.rstrip() for ln in m.group(1).splitlines() if ln.strip()]


def distil_memory() -> str:
    src = MEM_MD.read_text(encoding="utf-8", errors="replace")
    out = []
    out.append("# Project Memory (MonkeyCode mirror)")
    out.append("")
    out.append(
        "> Distilled automatically by `scripts/monkeycode_sync.py`. The SOURCE OF "
        "TRUTH is the full file at `memory/conversation-memory.md` (and its compact "
        "`.bin`). Read the full file for complete history."
    )
    out.append("")
    project = grab_section(src, "Project")
    if project:
        out.append("## Project")
        out.append("")
        out.extend(project[:20])
        out.append("")
    out.append("## What this workspace is")
    out.append("")
    out.append("- Python agent system that guards, self-improves, and generates n8n")
    out.append("  workflow assets (verifying, security gating, HITL approval, key rotation).")
    out.append("- Test suite: `venv/bin/python -m pytest` (green, e2e deselected).")
    out.append("- Skill library under `.opencode/skills/` (fast index: `memory/skills-library.md`;")
    out.append("  full docs: `memory/skills-docs/`).")
    out.append("")
    out.append("## Standing user rules (verbatim, load-bearing)")
    out.append("")
    rules = [
        "1. شغّل البوابات اللي في البرمجة قبل أي build (الأمان/الجودة/التكامل/الرياضيات/"
        "التفكير) — exit 0 = READY_FOR_DEPLOYMENT فقط.",
        "2. قبل ما تسلمني أي workflow لازم تجربه ويشتغل فعلاً، وراجع أوامري واحد واحد إنها "
        "اتنفذت (n8n-delivery-verification-gate).",
        "3. لما أطلب تصميم workflow أو agent دور على الإنترنت على أفضل طريقة موجودة الأول — "
        "مش نعيد اختراع العجلة (best-practice-first-designer).",
        "4. بعد ما أقولك تبدأ: دور الأول، وبعدين ارجع اسألني التفاصيل، وبعدين نفذ بالظبط "
        "(clarify-before-execute).",
        "5. القفل: شغّل كل المهارات مع بعض حتى لو شايفهم مالهمش علاقة — psychology مطلوبة "
        "مع أي طلب (omni-request-orchestrator).",
        "6. find-skills تشتغل أوتوماتيك في الخلفية مع أي طلب، وأي مهارة جديدة تُسجَّل في "
        "الراوتر والمكتبة (router_register.py).",
        "7. أي حاجة نبنيها تعدي على نفس البوابات بنفس الجودة زي نظام Python.",
    ]
    out.extend(rules)
    out.append("")
    out.append("## Where things live")
    out.append("")
    paths = [
        ("Full conversation memory", "memory/conversation-memory.md (.bin for compact)"),
        ("Skill library index", "memory/skills-library.md"),
        ("Skill full docs", "memory/skills-docs/"),
        ("Build gates pipeline", "scripts/build_gates_pipeline.py"),
        ("Router (meta-skill)", ".opencode/skills/compensatory-router/SKILL.md"),
        ("Skill registration", "scripts/router_register.py <skill-name>"),
        ("Memory encode/decode", "scripts/memory-encode.py encode | decode"),
        ("MonkeyCode sync", "scripts/monkeycode_sync.py"),
    ]
    for name, path in paths:
        out.append(f"- **{name}:** `{path}`")
    out.append("")
    out.append("## Keep alive")
    out.append("")
    out.append("- After significant work: append to `memory/conversation-memory.md`, then run")
    out.append("  `venv/bin/python scripts/memory-encode.py encode` (which re-runs this sync).")
    out.append("- After installing a skill: run `venv/bin/python scripts/router_register.py <name>`")
    out.append("  (adds router row + library entry + re-runs this sync).")
    out.append("")
    if len(out) > MEMORY_LINE_LIMIT:
        out = out[:MEMORY_LINE_LIMIT]
        out.append("")
        out.append("_(truncated — read memory/conversation-memory.md for full)_")
    return "\n".join(out).rstrip() + "\n"


AGENTS_MD = """# AGENTS.md

> Auto-generated by `scripts/monkeycode_sync.py`. Do not edit by hand — edit the
> source memory/rules instead and re-run the sync.

## Orientation

This repository is a Python agent system that guards, self-improves, and
generates n8n workflow assets (verification, security gating, HITL approval,
key rotation). It carries a large skill library and a persistent conversation
memory. Whenever you work here, follow the sequence below.

## First, load memory and the skill library

1. **Read the project memory:** `memory/conversation-memory.md` (or decode the
   compact copy with `venv/bin/python scripts/memory-encode.py decode`). It is
   the durable brain of the workspace — never guess about past decisions.
2. **Find the right skill fast:** scan `memory/skills-library.md` (one-line
   index grouped by family). For the full doc of a chosen skill open
   `memory/skills-docs/<name>.md`.
3. **Route the task:** load `.opencode/skills/compensatory-router/SKILL.md`
   (the meta-skill that maps any request to the right skill pack).

## Standing user rules (mandatory)

These are the user's own rules. They apply to EVERY request.

1. **Gates before any build:** before creating/deploying ANY n8n workflow, AI
   agent, or automation artifact, run the pipeline:
   `venv/bin/python scripts/build_gates_pipeline.py <artifact>`.
   Exit 0 = `READY_FOR_DEPLOYMENT` only. The pipeline enforces security,
   quality, DAG integrity, math/logic, reasoning, HITL, and audit.
2. **Deliver only what is proven:** never hand over a workflow that has not
   actually RUN end-to-end. Audit the user's original commands one-by-one with
   evidence (REQ -> evidence -> PASS/FAIL). See
   `.opencode/skills/n8n-delivery-verification-gate/SKILL.md`.
3. **Best practice first:** before designing any workflow/agent, research the
   internet for the best existing implementation (n8n templates, GitHub, docs)
   and adopt it as a cited baseline — never reinvent the wheel. See
   `.opencode/skills/best-practice-first-designer/SKILL.md`.
4. **Search, then ask, then execute:** for any request: search/ground first,
   come back and ask the load-bearing details (max ~7 questions with stated
   defaults), then execute exactly the confirmed contract. See
   `.opencode/skills/clarify-before-execute/SKILL.md`.
5. **Omnipresent orchestration:** psychology and audience analysis are NEVER
   optional — even on code/n8n tasks. Run the full pipeline of
   `.opencode/skills/omni-request-orchestrator/SKILL.md`.
6. **Automatic skill discovery:** find-skills runs in the background on every
   request (search skills.sh, install silently, register in the router and
   library). Never pause the task to ask about it.
7. **Same quality bar as the Python system:** anything built passes the same
   gates with the same quality.

## Repository map

- `scripts/` — the engines: `build_gates_pipeline.py` (gates),
  `router_register.py` (skill registration), `skills_docs_generator.py`
  (library + docs), `memory-encode.py` (memory), `monkeycode_sync.py` (this).
- `memory/` — conversation memory, skill library, skill docs, audits.
- `.opencode/skills/` — the skill tree (mirrored at `.ai-ready/skills`).
- `tests/` — the pytest suite (`venv/bin/python -m pytest`).
- `opencode.jsonc` — MCP servers (n8n, apify, firecrawl, context7, gh_grep,
  youtube-transcript, playwright) and instructions.

## Working norms

- Never commit secrets. `.env`, `*.db*`, `.operator/`, `memory/.sessions/`,
  `venv/` are gitignored.
- Prefer `venv/bin/python` (absolute path) for all project scripts.
- After significant work: append to `memory/conversation-memory.md` and run
  `venv/bin/python scripts/memory-encode.py encode`.
- After installing a skill: run `venv/bin/python scripts/router_register.py <name>`.
- No emoji in user-facing output unless the user uses them.
"""

USER_RULES = {
    "project-orientation.md": """# Project orientation

This workspace is a Python agent system that guards, self-improves, and
generates n8n workflow assets (verification, security gating, HITL approval,
key rotation). It has a large skill library and a persistent conversation
memory.

- Full memory: `memory/conversation-memory.md`
- Skill index: `memory/skills-library.md`
- Build gates: `scripts/build_gates_pipeline.py`
- Test suite: `venv/bin/python -m pytest` (green)
""",
    "gates-before-deploy.md": """# Gates before deploy (user rule #1)

Before creating or deploying ANY n8n workflow, AI agent, or automation
artifact, run the user's own gate pipeline:

    venv/bin/python scripts/build_gates_pipeline.py <artifact>

Exit code 0 means `READY_FOR_DEPLOYMENT` only. The pipeline runs SECURITY,
QUALITY, INTEGRITY, PRECISION, MATH, REASONING, HITL, and AUDIT stages.
""",
    "delivery-verification.md": """# Deliver only what is proven (user rule #2)

Never hand over a workflow that has not actually RUN end-to-end with no
problems. Audit the user's original commands one-by-one with evidence:

    REQ -> evidence -> PASS/FAIL/PARTIAL

See `.opencode/skills/n8n-delivery-verification-gate/SKILL.md`. A workflow that
only "validates green" but was never executed is NOT done.
""",
    "best-practice-first.md": """# Best practice first (user rule #3)

Before designing any workflow or agent, research the internet for the best
existing implementation (n8n official templates, GitHub repos, docs,
communities) and adopt the strongest existing pattern as a cited baseline.
Only then apply the user's required modifications. Never reinvent the wheel.
See `.opencode/skills/best-practice-first-designer/SKILL.md`.
""",
    "search-ask-execute.md": """# Search, then ask, then execute (user rule #4)

For ANY request: (0) SEARCH/ground first (web / skills.sh / codebase /
memory) so questions are not asked from ignorance; (1) COME BACK with one
compact round of at most ~7 load-bearing questions, each with a stated default
(if unanswered, assume it); (2) restate a confirmation contract; (3) EXECUTE
exactly that contract; (4) verify output vs the agreed done-when.

See `.opencode/skills/clarify-before-execute/SKILL.md`. Never build on
assumptions when a question is affordable; never stall with more than one
round.
""",
    "omni-orchestration.md": """# Omnipresent orchestration (user rule #5)

The user's standing rule: 'قفل شغل كل المهارات مع بعض حتي لو انت شايف ان
ملهمش علاقة'. Psychology/audience analysis is NEVER optional — even on code
or n8n tasks. For every request run the full omni pipeline:

1. extract PURPOSE + TARGET AUDIENCE (ask once max, else assume),
2. analyze the audience's psychology with the LATEST online reports (live
   web search, never memory),
3. choose a marketing strategy matching that psychology,
4. hand the full psychological brief into the production skill,
5. verify the output against the psychology.

See `.opencode/skills/omni-request-orchestrator/SKILL.md`.
""",
    "skill-discovery.md": """# Automatic skill discovery (user rule #6)

find-skills runs automatically in the background on every request: scan the
local library first (`memory/skills-library.md`), then skills.sh; install
good hits silently (>=1K installs or trusted owner); register every new skill
in the router and library:

    venv/bin/python scripts/router_register.py <name>

If no online skill fits, build it in-house through the gates
(`scripts/build_gates_pipeline.py` on the new SKILL.md until
READY_FOR_DEPLOYMENT), then register it. Never pause the task to ask about a
background install; report in one line at the end.
""",
    "memory-protocol.md": """# Memory protocol

- SOURCE OF TRUTH: `memory/conversation-memory.md`.
- Load at session start: `venv/bin/python scripts/memory-encode.py decode`.
- After significant work: APPEND (never rewrite) to
  `memory/conversation-memory.md`, then run
  `venv/bin/python scripts/memory-encode.py encode` (re-compresses to
  `memory/conversation-memory.bin` and re-runs the MonkeyCode sync).
""",
    "no-secrets.md": """# Never commit secrets

`.env`, `*.db*`, `*.db-shm`, `*.db-wal`, `.operator/`,
`**/rotation_override.secret`, `memory/.sessions/`, `memory/.skillopt-sleep/`,
`venv/`, `__pycache__/` are gitignored. Never write API keys, tokens, or
passwords into node parameters, scripts, docs, or commits.
""",
}

MONKEYCODE_AI_README = """# .monkeycode-ai

This directory is the MonkeyCode AI config surface. MonkeyCode's dev tool is
OpenCode, which already reads `.opencode/skills` and `opencode.jsonc` natively;
this directory exists so the bridge stays explicit and auto-commit rules can
live here if the platform expects them.

- Skills: mirror at `.ai-ready/skills` (symlink to `../.opencode/skills`).
- Rules: `.ai-ready/rules/*.md` (regenerated by `scripts/monkeycode_sync.py`).
- Memory: `.monkeycode/MEMORY.md` (regenerated by the same script).
- Regenerate everything: `venv/bin/python scripts/monkeycode_sync.py`.
"""


def write(path: Path, content: str) -> bool:
    changed = not path.exists() or path.read_text(encoding="utf-8") != content
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    if changed:
        log(f"  wrote {path.relative_to(ROOT)}")
    return changed


def ensure_skills_symlink() -> None:
    AI_READY.mkdir(parents=True, exist_ok=True)
    target = os.path.relpath(SKILLS_DIR, AI_READY)  # -> '../.opencode/skills'
    if AI_SKILLS_LINK.is_symlink():
        cur = os.readlink(AI_SKILLS_LINK)
        if cur == target:
            log(f"  symlink ok .ai-ready/skills -> {cur}")
            return
        AI_SKILLS_LINK.unlink()
        log(f"  replaced .ai-ready/skills symlink (was -> {cur})")
    elif AI_SKILLS_LINK.exists():
        log("  WARN: .ai-ready/skills is a real dir; removing to symlink")
        shutil.rmtree(AI_SKILLS_LINK)
    os.symlink(target, AI_SKILLS_LINK)
    log(f"  linked .ai-ready/skills -> {target}")


def git_sync() -> None:
    if NO_GIT or not (ROOT / ".git").exists():
        log("  [git] not a git repo (or --no-git) — files written, no commit")
        return
    name = subprocess.run(["git", "config", "user.name"], capture_output=True, text=True).stdout.strip()
    email = subprocess.run(["git", "config", "user.email"], capture_output=True, text=True).stdout.strip()
    if not (name and email):
        log("  [git] no user.name/email configured — skipping commit (set identity first)")
        return
    subprocess.run(["git", "add", "-A"], cwd=ROOT, capture_output=True, text=True)
    staged = subprocess.run(["git", "diff", "--cached", "--quiet"], cwd=ROOT).returncode
    if staged != 0:
        msg = "sync: MonkeyCode bridge (AGENTS.md, MEMORY.md, rules, skills symlink)"
        r = subprocess.run(["git", "commit", "-m", msg], cwd=ROOT, capture_output=True, text=True)
        log("  [git] committed bridge changes" if r.returncode == 0
            else f"  [git] commit failed: {r.stderr.strip()[:300]}")
        up = subprocess.run(["git", "rev-parse", "--abbrev-ref", "--symbolic-full-name", "@{u}"],
                            cwd=ROOT, capture_output=True, text=True)
        if up.returncode == 0 and not QUIET:
            push = subprocess.run(["git", "push"], cwd=ROOT, capture_output=True, text=True)
            log("  [git] pushed" if push.returncode == 0 else f"  [git] push failed: {push.stderr.strip()[:200]}")
    else:
        log("  [git] nothing staged")


def main() -> int:
    log("monkeycode_sync: regenerating MonkeyCode bridge")
    n = 0
    n += write(ROOT / "AGENTS.md", AGENTS_MD)
    n += write(ROOT / ".monkeycode" / "MEMORY.md", distil_memory())
    n += write(ROOT / ".monkeycode-ai" / "README.md", MONKEYCODE_AI_README)
    for fname, content in USER_RULES.items():
        n += write(AI_READY / "rules" / fname, content)
    ensure_skills_symlink()
    if n:
        log(f"  {n} file(s) regenerated")
    git_sync()
    log("monkeycode_sync: done")
    return 0


if __name__ == "__main__":
    sys.exit(main())