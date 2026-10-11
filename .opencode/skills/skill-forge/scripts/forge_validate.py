#!/usr/bin/env python3
"""forge_validate.py — deterministic validator for workspace skills.

Merges: anthropics/skill-creator quick_validate.py + VSCode-toolkit
health-check/trust-scan + house Review checklist + Academy troubleshooting
ladder. Loud failures only (never silent pass).

Usage:
  venv/bin/python .opencode/skills/skill-forge/scripts/forge_validate.py <skill-dir>

Exit 0 = VALID, 1 = INVALID (reasons printed, one per line).
"""
import re
import sys
import yaml
import json
from pathlib import Path

# Patterns live in forge_patterns.json (data, not code) so this scanner can
# never match its own regex source — the self-match class of false positives
# is structurally impossible.
_PAT = json.loads((Path(__file__).parent / "forge_patterns.json")
                  .read_text(encoding="utf-8"))
SECRET_PAT = re.compile(_PAT["secret"], re.IGNORECASE)
DANGER_PAT = re.compile(_PAT["danger"], re.IGNORECASE)
EXFIL_PAT = re.compile(_PAT["exfil"], re.IGNORECASE)

HOUSE_FRONTMATTER_EXTRA = {
    "user-invocable", "argument-hint", "context", "agent", "compatibility",
    "version", "author",
}
SPEC_SIX = {"name", "description", "license", "compatibility", "metadata",
            "allowed-tools"}


def fail(msg, errs):
    errs.append(msg)


def main() -> int:
    if len(sys.argv) != 2:
        print("usage: forge_validate.py <skill-dir>")
        return 1
    errs: list[str] = []
    d = Path(sys.argv[1])
    md = d / "SKILL.md"
    if not md.is_file():
        print("INVALID: SKILL.md not found")
        return 1
    text = md.read_text(encoding="utf-8")
    m = re.match(r"^---\n(.*?)\n---\n", text, re.S)
    if not m:
        fail("frontmatter: missing opening --- block", errs)
        print("INVALID:\n- " + "\n- ".join(errs))
        return 1
    try:
        fm = yaml.safe_load(m.group(1))
    except yaml.YAMLError as e:
        print(f"INVALID:\n- frontmatter: bad YAML: {e}")
        return 1
    if not isinstance(fm, dict):
        print("INVALID:\n- frontmatter: must be a YAML mapping")
        return 1

    name = fm.get("name", "")
    if name != d.name:
        fail(f"frontmatter: name '{name}' != directory '{d.name}'", errs)
    if not re.fullmatch(r"[a-z0-9-]{1,64}", str(name or "")):
        fail("frontmatter: name must be lowercase-hyphens, <=64 chars", errs)
    desc = fm.get("description", "")
    if not desc or len(str(desc)) < 20:
        fail("frontmatter: description missing/too vague", errs)
    if len(str(desc)) > 1024:
        fail(f"frontmatter: description {len(str(desc))} chars > 1024 "
             f"(house cap; spec listing truncates at 1536)", errs)
    low = str(desc).lower()
    if not any(w in low for w in ("use when", "used when", "when the user",
                                  "use this skill when", "trigger")):
        fail("frontmatter: description lacks WHEN/trigger phrasing", errs)
    unknown = set(fm.keys()) - SPEC_SIX - HOUSE_FRONTMATTER_EXTRA
    if unknown:
        fail(f"frontmatter: unknown keys {sorted(unknown)} "
             f"(breaks spec packaging)", errs)

    body = text[m.end():]
    nlines = body.count("\n") + 1
    if nlines > 500:
        fail(f"body: {nlines} lines > 500 (split into references/)", errs)
    for need in ("verification", "pairs"):
        if need not in body.lower():
            fail(f"body: missing '{need}' section", errs)

    for f in sorted(d.rglob("*")):
        if f.is_file() and f.suffix in (".md", ".py", ".js", ".cjs", ".sh",
                                         ".json", ".yml", ".yaml", ".txt"):
            rel = f.relative_to(d)
            # The scanner's own signature database is trusted input shipped
            # with the tool (reviewed definitions, not scanned content).
            if rel == Path("scripts/forge_patterns.json"):
                continue
            try:
                c = f.read_text(encoding="utf-8", errors="replace")
            except OSError:
                continue
            if SECRET_PAT.search(c):
                fail(f"security: possible secret in {rel}", errs)
            if EXFIL_PAT.search(c):
                fail(f"security: exfiltration pattern in {rel}", errs)
            if f.suffix in (".py", ".js", ".cjs", ".sh") and DANGER_PAT.search(c):
                fail(f"security: risky code-execution call in {rel}", errs)
            if len(c) > 200_000:
                fail(f"hygiene: {rel} unusually large "
                     f"({len(c)} chars)", errs)

    if errs:
        print("INVALID:\n- " + "\n- ".join(errs))
        return 1
    print(f"VALID: {d.name} "
          f"(desc {len(str(desc))} chars, body {nlines} lines)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
