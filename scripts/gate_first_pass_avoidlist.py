#!/usr/bin/env python3
"""Emit the current top-N n8n gate-rejection patterns from the accumulated
error DB so any workflow/agent build knows what will get it REJECTED before a
single node is placed. This is the dynamic avoid-list behind the
gate-first-pass-builder skill — it never drifts because it reads the real
rejection history.

Usage:
    venv/bin/python scripts/gate_first_pass_avoidlist.py [--top N] [--gate G] [--json]

Reads memory/n8n_error_patterns.json (kept in sync by build_gates_pipeline.py's
ErrorPatternDB). Prints a weighted, deduped list ordered by occurrence count.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ERROR_PATTERNS_PATH = ROOT / "memory" / "n8n_error_patterns.json"


def load_patterns(path: Path) -> list[dict]:
    if not path.exists():
        return []
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def emit(top: int, gate_filter: str | None, as_json: bool) -> int:
    patterns = load_patterns(ERROR_PATTERNS_PATH)
    if gate_filter:
        patterns = [p for p in patterns if p.get("gate") == gate_filter]
    # order by count desc, then most-recently-seen desc (stable tiebreak)
    patterns.sort(key=lambda p: (p.get("count", 0), p.get("last_seen", "")), reverse=True)
    ranked = patterns[:top]

    if as_json:
        print(json.dumps(ranked, indent=2, ensure_ascii=False))
        return 0

    if not ranked:
        print("No recorded gate rejection patterns (error DB empty).")
        return 0

    print(f"Top {len(ranked)} recorded n8n gate rejections (from {ERROR_PATTERNS_PATH.name}):")
    print()
    for i, p in enumerate(ranked, 1):
        gate = p.get("gate", "?")
        count = p.get("count", 0)
        pattern = p.get("pattern", "")
        print(f"  {i:>2}. [{gate:9}] x{count:<3} {pattern}")
    print()
    print("Rule: every item above is a reason a previous build was REJECTED. Design the")
    print("workflow/agent so none of them can fire, then run build_gates_pipeline.py.")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--top", type=int, default=10, help="number of top patterns to print")
    parser.add_argument("--gate", default=None, help="filter to one gate (security/quality/...)")
    parser.add_argument("--json", action="store_true", help="emit raw JSON instead of text")
    args = parser.parse_args(argv)
    try:
        return emit(args.top, args.gate, args.json)
    except Exception as exc:  # never hide the cause from the caller
        print(f"gate_first_pass_avoidlist error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
