#!/usr/bin/env python3
"""forge_eval.py — deterministic trigger-battery eval for a skill.

Fixes people's complaint #2/#3 (silent non-triggering, vague descriptions):
scores whether realistic user phrasings share vocabulary with the skill's
description, and checks the description budget. No LLM needed; LLM-as-judge
runs separately in-turn (skill-creator Grader) for semantics.

Usage:
  venv/bin/python .opencode/skills/skill-forge/scripts/forge_eval.py \
      <skill-dir> <phrases.txt>

phrases.txt: one realistic user phrasing per line (5-15 lines).
Exit 0 + PASS when coverage >= 0.8 AND budget OK, else 1 + report.
"""
import re
import sys
import yaml
from pathlib import Path

STOP = set("""a an the and or of to in on for with is are be as at by from
that this it its you your we our they he she his her i me my do does did not
no yes if then than so such can could should would will just how what when
where which who whom whose there here out up down over under can t s re ll ve
m don isn aren wasn weren hasn haven hadn doesn didn won wouldn couldn shouldn
need want help please make create get give use using used via vs etc eg ie""".split())


def words(s: str) -> set[str]:
    return {w for w in re.findall(r"[a-z0-9]{3,}", s.lower())} - STOP


def main() -> int:
    if len(sys.argv) != 3:
        print("usage: forge_eval.py <skill-dir> <phrases.txt>")
        return 1
    d = Path(sys.argv[1])
    phrases = [p.strip() for p in Path(sys.argv[2]).read_text(
        encoding="utf-8").splitlines() if p.strip()]
    if not (5 <= len(phrases) <= 30):
        print(f"INVALID: need 5-30 phrases, got {len(phrases)}")
        return 1
    m = re.match(r"^---\n(.*?)\n---\n",
                 (d / "SKILL.md").read_text(encoding="utf-8"), re.S)
    desc = str(yaml.safe_load(m.group(1)).get("description", ""))
    dw = words(desc)
    print(f"description: {len(desc)} chars, {len(dw)} signal words")
    budget_ok = len(desc) <= 1024
    print(f"budget<=1024: {'OK' if budget_ok else 'OVER (will truncate)'}")
    hits, misses = [], []
    for p in phrases:
        pw = words(p)
        overlap = (pw & dw) or {w for w in pw
                                if any(w in d or d in w for d in dw)}
        (hits if overlap else misses).append((p, sorted(overlap)))
    for p, ov in hits:
        print(f"  HIT  [{', '.join(ov[:4])}] {p}")
    for p, _ in misses:
        print(f"  MISS [] {p}")
    cov = len(hits) / len(phrases)
    print(f"coverage: {len(hits)}/{len(phrases)} = {cov:.2f} "
          f"(need >= 0.80)")
    if misses:
        missing = sorted({w for p, _ in misses for w in words(p)} -
                         {w for _, ov in hits for w in ov})
        print(f"suggested description additions: {', '.join(missing[:12])}")
    ok = cov >= 0.80 and budget_ok
    print("PASS" if ok else "FAIL")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
