#!/usr/bin/env python3
"""GateSkillInvoker — mandatory-skill enforcement for the build gates.

The user-requested design ("every gate must PROVE its mandatory router skills
were invoked and returned a result, otherwise the gate refuses") cannot be
naively built on a `router_dispatch()` call: in this system there IS no
runtime skill dispatcher. Skills are Markdown instruction files
(`.opencode/skills/<name>/SKILL.md` or global `~/.claude/skills/`) that the
*agent* loads via the `skill` tool when a task matches; the gates are
deterministic Python that runs headless in the pipeline. A Python function
cannot "call" a Markdown skill and receive a result.

So "the mandatory skill was invoked" is split into the two halves that are
ACTUALLY verifiable:

  1. READINESS (deterministic, always runs, fail-closed): every mandatory
     skill must be installed (project OR global skills dir), its SKILL.md
     frontmatter must parse and declare the expected `name`, and the router
     (`compensatory-router/SKILL.md`) must be able to route to it. A skill
     that is missing, unparseable, or unroutable CANNOT be consulted, so the
     gate BLOCKS — it never "continues as if nothing happened".

  2. ACTUAL LOAD (only the agent can prove it): skill invocation happens in
     the agent's context, so the pipeline accepts `--skills-loaded
     <manifest.json>` — a manifest of the skills the agent REALLY loaded
     during the build. When a manifest is supplied, every mandatory skill
     must appear in it; a missing entry is a hard BLOCK ("load security-review
     before this can pass"). When no manifest is supplied (pure headless run)
     only READINESS is enforced; the stage reports that actual loads are
     unverifiable, never pretending they happened.

Verdict contract (shared by all callers):
  ALL_SKILLS_PASSED        — every mandatory skill ready (+ loaded, if manifest)
  MANDATORY_SKILL_FAILURE  — at least one mandatory skill is NOT ready/loaded
                             -> the gate must refuse (BLOCK, risk >= 40, HITL)
  NO_MANDATORY_SKILLS      — gate has no mandatory skills in the mapping
"""

from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PROJECT_SKILLS = ROOT / ".opencode" / "skills"
GLOBAL_SKILLS = Path.home() / ".claude" / "skills"
ROUTER_PATH = PROJECT_SKILLS / "compensatory-router" / "SKILL.md"

# Each gate's MANDATORY skills — the gate cannot give a final verdict unless
# every one of these is ready (and, when a manifest is supplied, actually loaded).
GATE_MANDATORY_SKILLS: dict[str, list[str]] = {
    "SECURITY": [
        "security-review",
        "security-and-hardening",
        "frontier-red-team-auditor",
        "n8n-credential-security-guard",
        "enterprise-security-gate",
    ],
    "QUALITY": [
        "n8n-validation-expert",
        "n8n-schema-guardrail",
        "critical-thinking-logical-reasoning",
    ],
    "INTEGRITY": [
        "n8n-error-boundary-architect",
    ],
    "PRECISION": [
        "automation-known-issues-compass",
        "n8n-schema-guardrail",
        "n8n-credential-security-guard",
    ],
    "REASONING": [
        "off-by-one-boundary-guard",
        "frontier-deep-reasoner",
    ],
}

ALL_GATES = list(GATE_MANDATORY_SKILLS)


class SkillInvocationError(Exception):
    """Raised when the router registry is unreadable (the routing table the
    gates trust to dispatch mandatory skills cannot be verified)."""


def find_skill(skill_name: str) -> Path | None:
    """Locate a skill's SKILL.md: project dir first, then the user's global
    `~/.claude/skills` (some n8n skills live there, e.g. n8n-validation-expert)."""
    for base in (PROJECT_SKILLS, GLOBAL_SKILLS):
        p = base / skill_name / "SKILL.md"
        if p.is_file():
            return p
    return None


def _parse_frontmatter(skill_path: Path) -> dict:
    """Lightweight frontmatter parse (skills use `---\nname: X\ndescription:...\n---`).
    We only need `name`; a missing/unclosed block means the skill cannot be
    loaded reliably => readiness FAIL."""
    try:
        text = skill_path.read_text(encoding="utf-8", errors="replace")
    except OSError as e:
        return {"error": str(e)}
    m = re.match(r"^---\s*\n(.*?)\n---", text, re.DOTALL)
    if not m:
        return {"error": "no YAML frontmatter block"}
    fm = {}
    for line in m.group(1).splitlines():
        if ":" in line:
            k, _, v = line.partition(":")
            fm[k.strip()] = v.strip().strip("\"'")
    return fm


def load_router_registry() -> list[str]:
    """Read the router SKILL.md and return the skill identifiers it references
    (backtick-quoted). Raises SkillInvocationError if the router file is
    missing — the gates trust this table to dispatch mandatory skills, so an
    unreadable router is itself a fail-closed condition."""
    if not ROUTER_PATH.is_file():
        raise SkillInvocationError(
            f"Router SKILL.md not found at {ROUTER_PATH} — cannot verify mandatory skills")
    return re.findall(r"`([a-z0-9][a-z0-9-]*[a-z0-9])`",
                      ROUTER_PATH.read_text(encoding="utf-8", errors="replace"))


def verify_skill_readiness(skill_name: str) -> dict:
    """Deterministic readiness evidence for one mandatory skill:
      exists, path, frontmatter_ok, declared_name, router_registered.
    Any of these False (except a name-mismatch, which is a warning) means the
    skill cannot be consulted -> the caller must block."""
    path = find_skill(skill_name)
    if path is None:
        return {"skill": skill_name, "exists": False, "path": None,
                "frontmatter_ok": False, "declared_name": None,
                "name_matches": False,
                "router_registered": None, "reason": "skill not installed (project or global)"}
    fm = _parse_frontmatter(path)
    declared = fm.get("name")
    return {
        "skill": skill_name,
        "exists": True,
        "path": str(path),
        "frontmatter_ok": "error" not in fm,
        "frontmatter_error": fm.get("error"),
        "declared_name": declared,
        "name_matches": bool(declared and declared.lower() == skill_name.lower()),
        "router_registered": skill_name in load_router_registry(),
    }


def run_mandatory_skills_for_gate(gate_name: str, gate_context: dict | None = None,
                                  skills_loaded: set[str] | list[str] | None = None) -> dict:
    """Main entry point, called from inside any gate before it gives a final
    verdict. Requires every mandatory skill of the gate to be READY, and — when
    `skills_loaded` (a real-agent load manifest) is provided — to have been
    ACTUALLY loaded. Any failure => MANDATORY_SKILL_FAILURE with
    verdict_override BLOCK (the gate must refuse, never continue)."""
    required = GATE_MANDATORY_SKILLS.get(gate_name, [])
    if not required:
        return {"status": "NO_MANDATORY_SKILLS", "invoked": [], "failed_skills": []}

    manifest = set(skills_loaded or [])
    manifest_provided = skills_loaded is not None
    invoked = []
    failed = []

    try:
        router = load_router_registry()
    except SkillInvocationError as e:
        # The routing table that proves dispatchability is unreadable — this is
        # itself a mandatory-skill failure: fail closed.
        return {"status": "MANDATORY_SKILL_FAILURE",
                "invoked": [{"skill": s, "status": "FAILED", "error": str(e)}
                            for s in required],
                "failed_skills": [{"skill": s, "error": str(e)} for s in required],
                "verdict_override": "BLOCK"}

    for skill in required:
        evidence = verify_skill_readiness(skill)
        problems = []
        if not evidence["exists"]:
            problems.append(evidence["reason"])
        if not evidence["frontmatter_ok"]:
            problems.append(f"SKILL.md frontmatter broken: {evidence.get('frontmatter_error')}")
        if not evidence["name_matches"]:
            problems.append(f"frontmatter name {evidence.get('declared_name')!r} != dir name {skill!r}")
        if manifest_provided and skill not in manifest:
            problems.append(f"skill not in --skills-loaded manifest — the agent must "
                            f"actually load '{skill}' (skill tool) before this gate can pass")
        if evidence["router_registered"] is False:
            evidence["router_warning"] = f"skill '{skill}' not referenced in the router table"

        if problems:
            failed.append({"skill": skill, "error": "; ".join(problems)})
            invoked.append({"skill": skill, "status": "FAILED",
                            "error": "; ".join(problems), "evidence": evidence})
        else:
            invoked.append({"skill": skill, "status": "SUCCESS", "evidence": evidence})

    if failed:
        return {"status": "MANDATORY_SKILL_FAILURE",
                "invoked": invoked, "failed_skills": failed,
                "manifest_provided": manifest_provided,
                "verdict_override": "BLOCK"}
    return {"status": "ALL_SKILLS_PASSED", "invoked": invoked,
            "manifest_provided": manifest_provided, "failed_skills": []}


def run_all_mandatory_skills(skills_loaded: set[str] | list[str] | None = None) -> dict:
    """Aggregate every gate's mandatory skills into one report for the SKILLS
    pipeline stage. FAIL if ANY gate's mandatory set failed."""
    invocations = []
    failed_gates = []
    manifest_provided = skills_loaded is not None
    for gate in ALL_GATES:
        r = run_mandatory_skills_for_gate(gate, skills_loaded=skills_loaded)
        if r["status"] == "MANDATORY_SKILL_FAILURE":
            failed_gates.append(gate)
    # A skill may be mandatory for several gates (e.g. n8n-schema-guardrail for
    # both SECURITY and PRECISION). Evidence is skill-level, so report it once.
    by_skill: dict[str, dict] = {}
    for gate in ALL_GATES:
        r = run_mandatory_skills_for_gate(gate, skills_loaded=skills_loaded)
        for entry in r["invoked"]:
            by_skill.setdefault(entry["skill"], entry)
    invocations = list(by_skill.values())
    status = "FAIL" if failed_gates else "PASS"
    violations = []
    if failed_gates:
        violations.append(f"mandatory skill invocation failed for gate(s): {', '.join(failed_gates)}")
    if not failed_gates and not manifest_provided:
        violations.append("no --skills-loaded manifest — actual agent loads are NOT verifiable "
                          "headless; readiness (installed + frontmatter + routable) verified only")
    return {"status": status, "violations": violations, "invoked": invocations,
            "failed_gates": failed_gates, "manifest_provided": manifest_provided}


if __name__ == "__main__":
    import sys
    result = run_all_mandatory_skills(
        set(sys.argv[1:]) if len(sys.argv) > 1 else None)
    print(json.dumps(result, ensure_ascii=False, indent=2))
