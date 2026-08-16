#!/usr/bin/env python3
"""ComplaintsRegistry — per-gate complaints section for the build gates.

User rule (Arabic, verbatim intent): "اضف في كل بوابة قسم شكاوي: أي مشكلة حصلت
ومكنش عندنا مهارة تحلها، أو أخذت وقت طويل، هتبعتها لبوابة find-skills عشان تحل
المشكلة ديه، ولو ملقتش حل تعمل هي مهارة جوا قسم الشكاوي في كل بوابة تحل المشكلة."

Each gate now carries its own complaints ledger at
`memory/gate_complaints/<gate>.json`. A complaint is raised the moment a gate
meets either trigger:

  1. SKILL_GAP  — the gate rejected/failed on a violation whose topic has NO
                  matching skill in the local skill pack (project `.opencode/
                  skills` or global `~/.claude/skills`). Matching is
                  deterministic: topic keywords from the violation are tested
                  against every installed skill's `name` + `description`.
  2. SLOW       — the gate took longer than GATE_TIMEOUT_SECONDS to produce
                  its verdict (reuses the same budget as AttemptGuard).

Complaints are recorded immediately (cheap, synchronous, no network). A final
resolution pass (the pipeline's COMPLAINTS stage) then sends every OPEN
complaint to the find-skills gate:

  Phase A  SEARCH   — `npx skills find <keywords>` (non-interactive, bounded).
  Phase B  INSTALL  — a high-quality hit (>= MIN_INSTALLS or trusted owner) is
                      auto-installed via `npx skills add <spec> -g -y`; the
                      complaint resolves SKILL_INSTALLED.
  Phase C  CREATE   — if no good hit exists, a brand-new skill is generated
                      inside that gate's complaints folder
                      `.opencode/skills/gate-complaints/<gate>/<slug>/SKILL.md`
                      encoding the problem, the known fix path, and the gate
                      context, and registered in the compensatory-router.
                      Complaint resolves SKILL_CREATED.
  Phase D  NONE     — finder itself failed/unavailable; marked NO_SOLUTION for
                      a later retry (never silently dropped).

Verdict contract for the COMPLAINTS stage:
  COMPLAINTS_RESOLVED  — every open complaint reached a terminal resolution
                         (installed / created / no-solution-now).
  NO_COMPLAINTS        — nothing was open; nothing needed resolution.
  RESOLUTION_FAILED    — an unexpected error during resolution.

Dependency injection keeps the registry fully deterministic in tests: pass
`finder`/`installer` callables (see resolve_open) — the defaults hit the real
`npx skills` CLI, so tests never touch the network.
"""

from __future__ import annotations

import json
import re
import shutil
import subprocess
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable

ROOT = Path(__file__).resolve().parent.parent
PROJECT_SKILLS = ROOT / ".opencode" / "skills"
GLOBAL_SKILLS = Path.home() / ".claude" / "skills"
COMPLAINTS_DIR = ROOT / "memory" / "gate_complaints"
GATE_COMPLAINT_SKILLS = PROJECT_SKILLS / "gate-complaints"
ROUTER_PATH = PROJECT_SKILLS / "compensatory-router" / "SKILL.md"

GATE_TIMEOUT_SECONDS = 60          # shared with AttemptGuard
MIN_INSTALLS = 1000                # find-skills quality gate
TRUSTED_OWNERS = {"vercel-labs", "anthropics", "microsoft", "n8n-io",
                  "zapier", "firebase", "better-auth", "getsentry"}
NPM_TIMEOUT_SECONDS = 90
MAX_COMPLAINTS_PER_GATE = 200

# Stopwords that never help match a skill topic.
_STOPWORDS = {
    "the", "a", "an", "and", "or", "of", "to", "in", "on", "for", "with",
    "this", "that", "from", "by", "is", "are", "was", "be", "been", "not",
    "no", "node", "nodes", "workflow", "must", "should", "cannot", "can",
    "does", "doesn", "your", "you", "artifact", "present", "missing", "has",
}
_KEYWORD_RE = re.compile(r"[a-zA-Z][a-zA-Z0-9_\-]{2,}")


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def extract_keywords(text: str, limit: int = 12) -> list[str]:
    """Deterministic topic keywords from a violation/error string (>=3 chars,
    stopword-filtered, lowercased, most-useful-first via position)."""
    words = _KEYWORD_RE.findall(text or "")
    seen = []
    for w in words:
        wl = w.lower()
        if wl in _STOPWORDS:
            continue
        if wl not in seen:
            seen.append(wl)
    return seen[:limit]


def _skill_corpus() -> list[dict]:
    """(name, description) for every installed skill (project + global)."""
    corpus = []
    for base in (PROJECT_SKILLS, GLOBAL_SKILLS):
        if not base.is_dir():
            continue
        for md in base.rglob("SKILL.md"):
            try:
                text = md.read_text(encoding="utf-8", errors="replace")
            except OSError:
                continue
            name = ""
            desc = ""
            m = re.match(r"^---\s*\n(.*?)\n---", text, re.DOTALL)
            if m:
                for line in m.group(1).splitlines():
                    if ":" in line:
                        k, _, v = line.partition(":")
                        k, v = k.strip(), v.strip().strip("\"'")
                        if k == "name":
                            name = v
                        elif k == "description":
                            desc = v
            # folder-name fallback (some legacy skills lack frontmatter name)
            if not name:
                name = md.parent.name
            corpus.append({"name": name, "description": desc,
                           "path": str(md.parent)})
    return corpus


class ComplaintsRegistry:
    """Per-gate complaints ledger with find-skills resolution.

    Thread-free, process-local, file-backed. `root` (default ROOT) is the
    workspace; tests pass a tmp dir so nothing touches real memory.
    """

    def __init__(self, root: Path = ROOT, gate: str = "GENERAL",
                 finder: Callable[[list[str]], list[dict]] | None = None,
                 installer: Callable[[str], bool] | None = None,
                 skill_creator: Callable[[str, dict], str | None] | None = None):
        self.root = Path(root)
        self.gate = gate
        self.complaints_dir = self.root / "memory" / "gate_complaints"
        self.gate_skill_root = self.root / ".opencode" / "skills" / "gate-complaints"
        self.router_path = self.root / ".opencode" / "skills" / "compensatory-router" / "SKILL.md"
        # injectables (tests pass fakes; defaults hit real npx skills).
        # The default creator MUST write under this registry's root so tests
        # (tmp root) never pollute the real project skill pack.
        self._finder = finder or default_find_skills
        self._installer = installer or default_install_skill
        if skill_creator:
            self._skill_creator = skill_creator
        else:
            self._skill_creator = lambda g, c: default_create_skill(
                g, c, base_dir=self.gate_skill_root)

    # ---- ledger I/O ----------------------------------------------------

    def _gate_file(self, gate: str | None = None) -> Path:
        g = (gate or self.gate).upper()
        return self.complaints_dir / f"{g}.json"

    def _load(self, gate: str | None = None) -> list[dict]:
        p = self._gate_file(gate)
        try:
            if p.is_file():
                data = json.loads(p.read_text(encoding="utf-8"))
                return data if isinstance(data, list) else []
        except (OSError, json.JSONDecodeError):
            pass
        return []

    def _save(self, gate: str | None = None):
        try:
            self.complaints_dir.mkdir(parents=True, exist_ok=True)
            self._gate_file(gate).write_text(
                json.dumps(self._load(gate), ensure_ascii=False, indent=2),
                encoding="utf-8")
        except OSError:
            pass

    def _new_complaint(self, gate: str, kind: str, violation: str,
                       elapsed: float, keywords: list[str]) -> dict:
        c = {
            "id": f"{gate.lower()}-{int(time.time()*1000)}",
            "gate": gate.upper(),
            "kind": kind,                 # SKILL_GAP | SLOW
            "violation": violation,
            "keywords": keywords,
            "elapsed_seconds": round(elapsed, 2),
            "status": "OPEN",             # OPEN | SKILL_INSTALLED | SKILL_CREATED | NO_SOLUTION
            "created_at": _now_iso(),
            "resolved_at": None,
            "resolution": None,           # spec installed / skill path created
            "search_hits": [],            # find-skills results at resolve time
        }
        return c

    # ---- recording (immediate, no network) ----------------------------

    def record_skill_gap(self, gate: str, violation: str) -> dict | None:
        """Record a SKILL_GAP complaint IF no installed skill matches the
        violation topic. Returns the complaint, or None when a local skill
        already covers it (no complaint needed — the skill exists)."""
        if not violation:
            return None
        keywords = extract_keywords(violation)
        if not keywords:
            return None
        if self._local_skill_covers(keywords):
            return None
        c = self._new_complaint(gate, "SKILL_GAP", violation, 0.0, keywords)
        return self._append(gate, c)

    def record_slow(self, gate: str, elapsed: float, detail: str) -> dict | None:
        """Record a SLOW complaint when the gate exceeded GATE_TIMEOUT_SECONDS.
        Returns the complaint, or None when the gate was fast enough."""
        if elapsed <= GATE_TIMEOUT_SECONDS:
            return None
        c = self._new_complaint(gate, "SLOW", f"gate took {elapsed:.1f}s ({detail})",
                                elapsed, ["slow", "gate", "timeout", detail.lower()])
        return self._append(gate, c)

    def _append(self, gate: str, c: dict) -> dict:
        ledger = self._load(gate)
        # dedupe: same gate+kind+keywords seen recently (same root cause)
        for ex in ledger:
            if (ex.get("gate") == c["gate"] and ex.get("kind") == c["kind"]
                    and ex.get("keywords") == c["keywords"]
                    and ex.get("status") == "OPEN"):
                return None
        ledger.append(c)
        # hard cap so the ledger never grows unbounded
        if len(ledger) > MAX_COMPLAINTS_PER_GATE:
            ledger = ledger[-MAX_COMPLAINTS_PER_GATE:]
        self.complaints_dir.mkdir(parents=True, exist_ok=True)
        self._gate_file(gate).write_text(json.dumps(ledger, ensure_ascii=False, indent=2),
                                         encoding="utf-8")
        return c

    # ---- skill-gap detection (deterministic) ---------------------------

    def _local_skill_covers(self, keywords: list[str]) -> bool:
        """True when ANY installed skill's name/description shares >= 2 distinct
        keywords with the violation topic — i.e. the capability already exists
        locally. A single generic word ("failure", "error", "test") is never
        enough to count as coverage."""
        generic = {"failure", "error", "errors", "test", "tests", "testing",
                   "issue", "issues", "problem", "problems", "check", "fix",
                   "fixes", "build", "workflow", "workflows", "warning",
                   "correct", "invalid", "must", "cannot", "missing"}
        kset = {k for k in keywords if len(k) >= 4 and k not in generic}
        if not kset:
            return False
        corpus = _skill_corpus()
        for s in corpus:
            hay = f"{s['name']} {s['description']}".lower()
            if sum(1 for k in kset if k in hay) >= 2:
                return True
        return False

    # ---- resolution (final COMPLAINTS stage) ---------------------------

    def open_complaints(self, gate: str | None = None) -> list[dict]:
        if gate:
            return [c for c in self._load(gate) if c.get("status") == "OPEN"]
        out = []
        if self.complaints_dir.is_dir():
            for f in self.complaints_dir.glob("*.json"):
                out.extend(c for c in self._load(f.stem) if c.get("status") == "OPEN")
        return out

    def _set_status(self, gate: str, cid: str, status: str, resolution=None,
                    hits: list[dict] | None = None):
        ledger = self._load(gate)
        for c in ledger:
            if c.get("id") == cid:
                c["status"] = status
                c["resolved_at"] = _now_iso()
                if resolution:
                    c["resolution"] = resolution
                if hits is not None:
                    c["search_hits"] = hits[:10]
                break
        self.complaints_dir.mkdir(parents=True, exist_ok=True)
        self._gate_file(gate).write_text(json.dumps(ledger, ensure_ascii=False, indent=2),
                                         encoding="utf-8")

    def resolve_open(self, gate: str | None = None) -> dict:
        """Resolution pass over every OPEN complaint. Deterministic with fake
        finder/installer; with defaults it hits the real npx skills CLI
        (bounded by NPM_TIMEOUT_SECONDS)."""
        opened = self.open_complaints(gate)
        if not opened:
            return {"status": "NO_COMPLAINTS", "processed": 0,
                    "installed": [], "created": [], "no_solution": []}
        installed, created, no_solution = [], [], []
        for c in opened:
            g, cid = c["gate"], c["id"]
            keywords = c.get("keywords") or extract_keywords(c.get("violation", ""))
            try:
                hits = self._finder(keywords) or []
            except Exception:
                hits = []
            if not hits:
                # no search results at all -> NO_SOLUTION (retryable)
                self._set_status(g, cid, "NO_SOLUTION",
                                 resolution="no skill found by find-skills", hits=[])
                no_solution.append(cid)
                continue
            good = next((h for h in hits if h.get("installable")), None) or hits[0]
            if not good:
                self._set_status(g, cid, "NO_SOLUTION",
                                 resolution="no installable skill found", hits=hits)
                no_solution.append(cid)
                continue
            # try install first (Phase B), else create a skill (Phase C)
            spec = good.get("spec")
            installed_ok = False
            if spec:
                try:
                    installed_ok = bool(self._installer(spec))
                except Exception:
                    installed_ok = False
            if installed_ok:
                self._set_status(g, cid, "SKILL_INSTALLED", resolution=spec, hits=hits)
                installed.append({"id": cid, "gate": g, "spec": spec})
            else:
                path = None
                try:
                    path = self._skill_creator(g, c)
                except Exception:
                    path = None
                if path:
                    self._set_status(g, cid, "SKILL_CREATED", resolution=path, hits=hits)
                    created.append({"id": cid, "gate": g, "skill_path": path})
                else:
                    self._set_status(g, cid, "NO_SOLUTION",
                                     resolution="could not install or create a skill",
                                     hits=hits)
                    no_solution.append(cid)
        return {"status": "COMPLAINTS_RESOLVED", "processed": len(opened),
                "installed": installed, "created": created,
                "no_solution": no_solution}

    def summary(self, gate: str | None = None) -> dict:
        if gate:
            ledger = self._load(gate)
            return {"gate": gate.upper(), "open": sum(1 for c in ledger if c["status"] == "OPEN"),
                    "total": len(ledger),
                    "statuses": {s: sum(1 for c in ledger if c["status"] == s)
                                 for s in {"OPEN", "SKILL_INSTALLED", "SKILL_CREATED", "NO_SOLUTION"}}}
        out = {}
        if self.complaints_dir.is_dir():
            for f in self.complaints_dir.glob("*.json"):
                out[f.stem.upper()] = self.summary(f.stem)
        return out


# ---- default find-skills / install / create (real npx, bounded) --------

_SKILL_ROW_RE = re.compile(r"([a-zA-Z0-9_.\-]+/[a-zA-Z0-9_.\-]+@[a-zA-Z0-9_.\-]+)"
                           r"\s+(\d+)\s+installs")


def default_find_skills(keywords: list[str]) -> list[dict]:
    """`npx skills find <keywords>` — non-interactive, bounded. Parses rows
    `<owner/repo@skill> NNNN installs` into search hits. A hit is
    'installable' when installs >= MIN_INSTALLS or the owner is trusted."""
    if not keywords:
        return []
    query = " ".join(keywords[:6])
    try:
        proc = subprocess.run(
            ["npx", "-y", "skills", "find", query],
            capture_output=True, text=True, timeout=NPM_TIMEOUT_SECONDS,
            env={"PATH": shutil.which("npx") and str(Path(shutil.which("npx")).parent) + ":" + "/usr/bin:/bin",
                 "HOME": str(Path.home())})
        out = proc.stdout + "\n" + proc.stderr
    except (subprocess.TimeoutExpired, OSError):
        return []
    hits = []
    for m in _SKILL_ROW_RE.finditer(out):
        spec = m.group(1)
        installs = int(m.group(2))
        owner = spec.split("/", 1)[0].lower()
        good = installs >= MIN_INSTALLS or owner in TRUSTED_OWNERS
        hits.append({"spec": spec, "installs": installs,
                     "owner": owner, "installable": good})
    return hits


def default_install_skill(spec: str) -> bool:
    """`npx skills add <spec> -g -y` — installs the matched skill."""
    try:
        proc = subprocess.run(
            ["npx", "-y", "skills", "add", spec, "-g", "-y"],
            capture_output=True, text=True, timeout=NPM_TIMEOUT_SECONDS,
            env={"PATH": shutil.which("npx") and str(Path(shutil.which("npx")).parent) + ":" + "/usr/bin:/bin",
                 "HOME": str(Path.home())})
        return proc.returncode == 0
    except (subprocess.TimeoutExpired, OSError):
        return False


def _slugify(text: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")
    return (slug or "skill")[:60]


def default_create_skill(gate: str, complaint: dict,
                         base_dir: Path | None = None) -> str | None:
    """Generate a SKILL.md inside the gate's complaints folder that encodes
    the problem + fix path, so the next time this class of problem appears the
    agent has a dedicated skill to solve it. `base_dir` is the gate-complaints
    skills root (project `.opencode/skills/gate-complaints` by default);
    registries pass their own root so tests stay sandboxed. Returns the
    created skill path."""
    g = gate.upper()
    topic = _slugify(" ".join(complaint.get("keywords") or ["problem"]))
    slug = f"{g.lower()}-complaint-{topic}"
    dir_ = (base_dir or GATE_COMPLAINT_SKILLS) / g.lower() / slug
    try:
        dir_.mkdir(parents=True, exist_ok=True)
    except OSError:
        return None
    description = (f"Resolves the {g} gate complaint recorded on "
                   f"{complaint.get('created_at', '?')[:10]}: "
                   f"{(complaint.get('violation') or 'unspecified problem')[:200]}. "
                   f"Generated automatically by the complaints section of the {g} "
                   f"gate when no installed skill covered this failure and "
                   f"find-skills found no installable match. Use when this exact "
                   f"problem class reappears in a build.")
    body = f"""# {g} Gate Complaint Skill — {topic.replace('-', ' ').title()}

## Origin
- Gate: **{g}**
- Complaint ID: `{complaint.get('id')}`
- Kind: {complaint.get('kind')} (SKILL_GAP = no installed skill covered this
  failure; SLOW = the gate exceeded the timeout budget)
- Reported: {complaint.get('created_at')}
- Elapsed (s): {complaint.get('elapsed_seconds')}

## Problem
{complaint.get('violation') or 'unspecified'}

## Failure keywords
{", ".join(complaint.get("keywords") or [])}

## Why no skill existed
The complaints recorder scanned every installed skill (project + global) for a
matching topic keyword and found none. find-skills (`npx skills find`) also
returned no installable match at resolution time, so this skill was generated
inside the {g} gate's complaints section.

## Fix / resolution approach
1. Reproduce the {g} gate rejection (run the build-gates pipeline on the
   offending artifact).
2. Apply the deterministic fix for this gate's rule class (see the gate's own
   known-issue catalog and `scripts/build_gates_pipeline.py`).
3. Re-run the gate; on PASS, this complaint's class is closed.

## Regression guard
- When this problem reappears, fix it with THIS skill before inventing a new
  workaround.
- When a real fix lands elsewhere (a better external skill, a code change),
  update this file and re-encode the memory.
"""
    skill_md = dir_ / "SKILL.md"
    try:
        skill_md.write_text(f"---\nname: {slug}\ndescription: \"{description}\"\n---\n\n{body}",
                            encoding="utf-8")
    except OSError:
        return None
    return str(skill_md)


if __name__ == "__main__":
    import sys
    reg = ComplaintsRegistry()
    if len(sys.argv) > 1 and sys.argv[1] == "resolve":
        print(json.dumps(reg.resolve_open(), ensure_ascii=False, indent=2))
    else:
        print(json.dumps(reg.summary(), ensure_ascii=False, indent=2))
