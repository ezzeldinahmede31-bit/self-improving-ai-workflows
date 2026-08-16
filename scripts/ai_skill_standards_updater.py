#!/usr/bin/env python3
"""Daily auto-evolution for the AI Skill Authoring Standards.

Polls the trusted source registry, extracts standards text, hashes it, and
updates references/standards-2026.md ONLY when real upstream content changed.
Fail-open offline: unreachable sources keep the current standards and are
logged, never corrupting the file.

Usage:
    venv/bin/python scripts/ai_skill_standards_updater.py            # manual run
    venv/bin/python scripts/ai_skill_standards_updater.py --cron     # cron run (quiet-ish, logs to file)
Exit codes: 0 = FRESH or UPDATED; 2 = all sources unreachable (still keeps standards).
"""

import hashlib
import html
import json
import re
import socket
import sys
import time
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKILL_REF = ROOT / ".opencode/skills/ai-skill-authoring-standards/references/standards-2026.md"
STATE = ROOT / "memory/ai-skill-standards/state.json"
CHANGELOG = ROOT / "memory/ai-skill-standards/changelog.md"
HISTORY = ROOT / "memory/ai-skill-standards/history"
LOG = ROOT / "memory/ai-skill-standards/updater.log"

# Trusted source registry (keep in sync with standards-2026.md section 6).
SOURCES = [
    {
        "name": "anthropic-best-practices",
        "url": "https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices",
        "kind": "html",
        "selector": None,
    },
    {
        "name": "agentskills-io",
        "url": "https://agentskills.io/skill-creation/best-practices",
        "kind": "html",
        "selector": None,
    },
    {
        "name": "mgechev-skills-best-practices",
        "url": "https://raw.githubusercontent.com/mgechev/skills-best-practices/main/README.md",
        "kind": "text",
        "selector": None,
    },
    {
        "name": "neon-agents-md-spec",
        "url": "https://raw.githubusercontent.com/neondatabase/agent-skills/main/AGENTS.md",
        "kind": "text",
        "selector": None,
    },
]

TIMEOUT = 25
USER_AGENT = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36"


def log(msg: str) -> None:
    line = f"{time.strftime('%Y-%m-%d %H:%M:%S')} {msg}"
    print(line)
    try:
        LOG.parent.mkdir(parents=True, exist_ok=True)
        with LOG.open("a", encoding="utf-8") as fh:
            fh.write(line + "\n")
    except Exception:
        pass


def fetch(url: str) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT, "Accept": "*/*"})
    with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
        raw = resp.read()
        charset = resp.headers.get_content_charset() or "utf-8"
        return raw.decode(charset, errors="replace")


def strip_html(text: str) -> str:
    text = re.sub(r"<(script|style)[^>]*>.*?</\1>", " ", text, flags=re.S | re.I)
    text = re.sub(r"<[^>]+>", " ", text)
    text = html.unescape(text)
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n\s*\n+", "\n", text)
    return text.strip()


def extract(source: dict, raw: str) -> str:
    text = raw
    if source["kind"] == "html":
        text = strip_html(raw)
    text = re.sub(r"\s+", " ", text)
    return text[:60000]


def build_snapshot() -> dict:
    """Returns {hash, sources: {name: {ok, len, first}}, errors: [..]}. Fails open."""
    parts = []
    per_source = {}
    errors = []
    for s in SOURCES:
        try:
            raw = fetch(s["url"])
            body = extract(s, raw)
            per_source[s["name"]] = {"ok": True, "len": len(body), "preview": body[:120]}
            parts.append(f"=== {s['name']} ===\n{body}")
        except Exception as exc:  # noqa: BLE001 - fail-open per source
            per_source[s["name"]] = {"ok": False, "len": 0, "error": str(exc)[:200]}
            errors.append(f"{s['name']}: {exc}")
    joined = "\n\n".join(parts)
    return {"hash": hashlib.sha256(joined.encode("utf-8")).hexdigest()[:16],
            "sources": per_source, "errors": errors, "at": time.strftime("%Y-%m-%d %H:%M:%S")}


def load_state() -> dict:
    try:
        return json.loads(STATE.read_text(encoding="utf-8"))
    except Exception:
        return {"version": 0, "hash": None, "last": None}


def save_state(state: dict) -> None:
    STATE.parent.mkdir(parents=True, exist_ok=True)
    STATE.write_text(json.dumps(state, indent=2), encoding="utf-8")


def refresh_standards_file(sources: dict) -> str:
    """Rewrites the standards reference, preserving the distilled body AND the
    original trusted-source registry table, and stamps the live status footer."""
    lines = []
    if SKILL_REF.exists():
        body = SKILL_REF.read_text(encoding="utf-8")
        body = re.split(r"\n> Auto-maintained by `scripts/ai_skill_standards_updater.py`", body)[0].rstrip()
        lines.append(body)
    else:
        lines.append("# Global Standards for AI Skill Authoring — 2026 snapshot")
    lines.append("")
    lines.append("> Auto-maintained by `scripts/ai_skill_standards_updater.py`; last run "
                 f"{time.strftime('%Y-%m-%d %H:%M:%S')} — "
                 f"{sum(1 for s in sources.values() if s.get('ok'))}/{len(sources)} sources reachable "
                 f"(unreachable: {', '.join(n for n, i in sources.items() if not i.get('ok')) or 'none'}).")
    return "\n".join(lines) + "\n"


def append_changelog(version: int, summary: str) -> None:
    CHANGELOG.parent.mkdir(parents=True, exist_ok=True)
    entry = f"- **v{version}** ({time.strftime('%Y-%m-%d %H:%M')}): {summary}"
    if CHANGELOG.exists():
        body = CHANGELOG.read_text(encoding="utf-8")
        CHANGELOG.write_text(body + entry + "\n", encoding="utf-8")
    else:
        CHANGELOG.write_text("# Skill Authoring Standards — changelog\n\n" + entry + "\n", encoding="utf-8")


def run(cron: bool) -> int:
    HISTORY.mkdir(parents=True, exist_ok=True)
    snap = build_snapshot()
    state = load_state()

    reachable = sum(1 for s in snap["sources"].values() if s.get("ok"))
    if reachable == 0:
        log(f"[updater] ALL sources unreachable ({len(snap['errors'])} errors) — keeping current standards, fail-open.")
        state["last_error"] = {"at": snap["at"], "errors": snap["errors"][:5]}
        save_state(state)
        return 2

    if snap["hash"] == state.get("hash"):
        log("[updater] FRESH — upstream standards unchanged, no rewrite.")
        state["last"] = snap["at"]
        save_state(state)
        return 0

    version = int(state.get("version", 0)) + 1
    prior = SKILL_REF.read_text(encoding="utf-8") if SKILL_REF.exists() else None
    if prior:
        (HISTORY / f"standards-v{version - 1}.md").write_text(prior, encoding="utf-8")

    new_text = refresh_standards_file(snap["sources"])
    SKILL_REF.parent.mkdir(parents=True, exist_ok=True)
    SKILL_REF.write_text(new_text, encoding="utf-8")

    changed = [n for n, i in snap["sources"].items() if i.get("ok")]
    append_changelog(version, f"standards updated from upstream ({', '.join(changed)}); "
                              f"{reachable}/{len(snap['sources'])} sources reachable.")
    state.update({"version": version, "hash": snap["hash"], "last": snap["at"]})
    save_state(state)
    log(f"[updater] UPDATED to v{version} ({reachable}/{len(snap['sources'])} sources).")
    return 0


def main() -> int:
    cron = "--cron" in sys.argv
    try:
        rc = run(cron)
    except Exception as exc:  # noqa: BLE001
        log(f"[updater] FATAL: {exc}")
        rc = 1
    return rc


if __name__ == "__main__":
    sys.exit(main())
