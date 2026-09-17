"""Unified skill surface for the parallel orchestrator.

A worker prompt has a hard byte budget, but the skill universe is large:
project skills (`.opencode/skills/`), global skills (`~/.claude/skills/`),
and the library index (`memory/skills-library.md` — the one-line lookup the
find-skills router scans). This module makes all three visible to every task
through one deterministic pipeline (no LLM, no embeddings):

  index   — build once per scheduler run: name -> SkillRecord
  resolve — explicit contract `skills` win; `skills_auto` fills the rest by
            keyword scoring with an adaptive threshold + diversity filter
            (SkillsInjector/DSR-lite: budget emerges per task, redundant
            skills are skipped so context is not wasted)
  render  — compact set-aware block for the worker prompt (role boundaries
            preserved: name + surface + one-liner + load path)
  manifest — `skills_manifest.json` the gates `--skills-loaded` stage enforces

Priority on name collision: project > global > library-only.
"""
from __future__ import annotations
import json
import os
import re
from dataclasses import dataclass, field

PROJECT_SKILLS_DIR = os.path.join(".opencode", "skills")
GLOBAL_SKILLS_DIR = os.path.expanduser(os.path.join("~", ".claude", "skills"))
LIBRARY_INDEX = os.path.join("memory", "skills-library.md")
MANIFEST_FILE = "skills_manifest.json"

DEFAULT_BUDGET = 6
DEFAULT_THRESHOLD = 2.0
DIVERSITY_JACCARD_CAP = 0.6

_TOKEN_RE = re.compile(r"[a-z0-9]+")
_FRONTMATTER_NAME_RE = re.compile(r"^name:\s*(.+?)\s*$", re.MULTILINE)
_FRONTMATTER_DESC_RE = re.compile(r"^description:\s*(.+?)\s*$", re.MULTILINE)
_LIBRARY_ROW_RE = re.compile(r"^- \*\*(.+?)\*\*\s*[—–-]\s*(.+?)\s*$")


@dataclass
class SkillRecord:
    name: str
    description: str = ""
    path: str | None = None
    surface: str = "library"  # project | global | library
    keywords: set[str] = field(default_factory=set)


def _tokens(text: str) -> set[str]:
    return {t for t in _TOKEN_RE.findall((text or "").lower()) if len(t) >= 3}


def _parse_skill_md(path: str) -> tuple[str | None, str]:
    try:
        with open(path, "r", encoding="utf-8", errors="ignore") as fh:
            head = fh.read(2000)
    except OSError:
        return None, ""
    m = _FRONTMATTER_NAME_RE.search(head)
    name = m.group(1).strip().strip("\"'") if m else None
    m = _FRONTMATTER_DESC_RE.search(head)
    desc = m.group(1).strip().strip("\"'") if m else ""
    return name, desc[:300]


def _scan_skill_dir(root: str, surface: str) -> dict[str, SkillRecord]:
    out: dict[str, SkillRecord] = {}
    try:
        names = sorted(os.listdir(root))
    except OSError:
        return out
    for entry in names:
        md = os.path.join(root, entry, "SKILL.md")
        if not os.path.isfile(md):
            continue
        name, desc = _parse_skill_md(md)
        name = name or entry
        rec = SkillRecord(name=name, description=desc, path=md,
                          surface=surface)
        rec.keywords = _tokens(name.replace("-", " ").replace("_", " ")) | \
            _tokens(desc)
        out[name] = rec
    return out


def _scan_library_index(repo_root: str) -> dict[str, SkillRecord]:
    out: dict[str, SkillRecord] = {}
    path = os.path.join(repo_root, LIBRARY_INDEX)
    try:
        with open(path, "r", encoding="utf-8", errors="ignore") as fh:
            lines = fh.readlines()
    except OSError:
        return out
    for line in lines:
        m = _LIBRARY_ROW_RE.match(line.strip())
        if not m:
            continue
        name, desc = m.group(1).strip(), m.group(2).strip()
        if name in out:
            continue
        rec = SkillRecord(name=name, description=desc[:300], path=None,
                          surface="library")
        rec.keywords = _tokens(name.replace("-", " ").replace("_", " ")) | \
            _tokens(desc)
        out[name] = rec
    return out


def _relink_library_paths(records: dict[str, SkillRecord],
                          project: dict[str, SkillRecord],
                          global_: dict[str, SkillRecord]) -> None:
    """Point library-only rows at a real SKILL.md when one exists."""
    for name, rec in records.items():
        if rec.surface != "library":
            continue
        if name in project:
            rec.path = project[name].path
        elif name in global_:
            rec.path = global_[name].path


def build_index(repo_root: str) -> dict[str, SkillRecord]:
    """Unified index: project > global > library-only. Deterministic order."""
    project = _scan_skill_dir(os.path.join(repo_root, PROJECT_SKILLS_DIR),
                              "project")
    global_ = _scan_skill_dir(GLOBAL_SKILLS_DIR, "global")
    library = _scan_library_index(repo_root)
    _relink_library_paths(library, project, global_)
    merged: dict[str, SkillRecord] = {}
    for source in (library, global_, project):
        merged.update(source)
    # fix surfaces for names present in multiple sources (project wins)
    for name in project:
        merged[name].surface = "project"
        merged[name].path = project[name].path
    for name in global_:
        if name not in project:
            merged[name].surface = "global"
            merged[name].path = global_[name].path
    return merged


def _task_tokens(contract: dict) -> tuple[set[str], str]:
    parts = [contract.get("role", ""), contract.get("goal", "")]
    parts += [str(o) for o in contract.get("outputs", [])]
    for f in contract.get("allowed_files", []):
        base = os.path.basename(str(f))
        stem, _ = os.path.splitext(base)
        parts.append(stem.replace("_", " ").replace("-", " ").replace(".", " "))
    blob = " ".join(parts)
    return _tokens(blob), blob.lower()


def _score(task_tokens: set[str], blob: str, rec: SkillRecord) -> float:
    overlap = len(task_tokens & rec.keywords)
    verbatim = 0
    for tok in rec.keywords:
        if len(tok) >= 5 and tok in blob:
            verbatim += 1
    return float(overlap) + 3.0 * float(min(verbatim, 3))


def _jaccard(a: set[str], b: set[str]) -> float:
    if not a or not b:
        return 0.0
    return len(a & b) / len(a | b)


def resolve_for_contract(contract: dict, repo_root: str,
                         index: dict[str, SkillRecord] | None = None,
                         budget: int | None = None,
                         threshold: float = DEFAULT_THRESHOLD
                         ) -> tuple[list[SkillRecord], dict]:
    """Returns (selected, report). Explicit `skills` are honored first
    (unknown names kept but flagged unverified); auto-fill is threshold-
    adaptive up to budget with a diversity filter. Deterministic."""
    index = index if index is not None else build_index(repo_root)
    budget = DEFAULT_BUDGET if budget is None else int(
        contract.get("skill_budget", budget))
    selected: list[SkillRecord] = []
    notes: list[str] = []
    seen: set[str] = set()

    for name in contract.get("skills", []) or []:
        name = str(name).strip()
        if not name or name in seen:
            continue
        seen.add(name)
        rec = index.get(name)
        if rec is None:
            selected.append(SkillRecord(name=name, surface="unverified"))
            notes.append(f"explicit skill '{name}' not in any index — unverified")
        else:
            selected.append(rec)

    if contract.get("skills_auto", True) and len(selected) < budget:
        task_tokens, blob = _task_tokens(contract)
        ranked = sorted(((_score(task_tokens, blob, r), r.name)
                         for r in index.values() if r.name not in seen),
                        key=lambda t: (-t[0], t[1]))
        for score, name in ranked:
            if len(selected) >= budget:
                break
            if score < threshold:
                break
            rec = index[name]
            # Single shared stop-word ("write", "with") is not evidence of
            # fit — demand two or more overlapping content tokens before
            # spending prompt budget on a skill.
            if len(task_tokens & rec.keywords) < 2:
                continue
            if any(_jaccard(rec.keywords, s.keywords) >= DIVERSITY_JACCARD_CAP
                   for s in selected if s.keywords):
                continue
            seen.add(name)
            selected.append(rec)

    report = {"selected": [s.name for s in selected], "notes": notes,
              "surfaces": {s.name: s.surface for s in selected}}
    return selected, report


def render_for_prompt(selected: list[SkillRecord]) -> str:
    """Compact set-aware block. Empty selection renders as '' (prompt unchanged)."""
    if not selected:
        return ""
    lines = ["SKILLS (load each via the skill tool BEFORE acting; "
             "they are mandatory context, not optional reading):"]
    for s in selected:
        where = s.path or "(no local copy — proceed without it)"
        desc = (s.description or "no description")[:160]
        lines.append(f"- {s.name} [{s.surface}] — {desc} — {where}")
    lines.append("If a skill has no local copy, proceed without it and note "
                 "the gap in RESULT.json notes.")
    return "\n".join(lines)


def write_manifest(work_dir: str, selected: list[SkillRecord]) -> str:
    """Write the `--skills-loaded` manifest the gates SKILLS stage enforces."""
    path = os.path.join(work_dir, MANIFEST_FILE)
    try:
        with open(path, "w", encoding="utf-8") as fh:
            json.dump({"skills_loaded": [s.name for s in selected]}, fh)
    except OSError:
        pass
    return path
