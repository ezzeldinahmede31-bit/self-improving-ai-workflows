#!/usr/bin/env python3
"""forge_benchmark.py — with-skill vs without-skill comparison.

Fixes skill-creator issue #1383 (silent empty benchmarks, inverted delta):
- asserts BOTH grading files are non-empty (loud fail otherwise),
- asserts delta sign = mean(with) - mean(without) (never flipped),
- reports mean +/- stddev, min, max per config.

Usage:
  venv/bin/python .opencode/skills/skill-forge/scripts/forge_benchmark.py \
      with.jsonl without.jsonl --skill-name <slug>

Each JSONL: one {"pass": 0|1, "seconds": f, "tokens": n} per line.
Writes benchmark.json + benchmark.md next to with.jsonl. Exit 0 on success.
"""
import argparse
import json
import math
import sys
from pathlib import Path


def load(p: Path) -> list[dict]:
    rows = [json.loads(l) for l in p.read_text(encoding="utf-8").splitlines()
            if l.strip()]
    if not rows:
        print(f"INVALID: {p} is empty — refusing silent benchmark "
              f"(issue #1383)")
        sys.exit(1)
    for r in rows:
        if "pass" not in r:
            print(f"INVALID: {p} rows need a 'pass' key")
            sys.exit(1)
    return rows


def stats(vals: list[float]) -> dict:
    n = len(vals)
    mean = sum(vals) / n
    sd = math.sqrt(sum((v - mean) ** 2 for v in vals) / (n - 1)) if n > 1 else 0.0
    return {"n": n, "mean": round(mean, 4), "stddev": round(sd, 4),
            "min": round(min(vals), 4), "max": round(max(vals), 4)}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("with_jsonl")
    ap.add_argument("without_jsonl")
    ap.add_argument("--skill-name", default="")
    a = ap.parse_args()
    w, b = load(Path(a.with_jsonl)), load(Path(a.without_jsonl))
    out = {
        "skill": a.skill_name,
        "with_skill": {
            "pass_rate": stats([float(r["pass"]) for r in w]),
            "seconds": stats([float(r.get("seconds", 0)) for r in w]),
            "tokens": stats([float(r.get("tokens", 0)) for r in w])},
        "without_skill": {
            "pass_rate": stats([float(r["pass"]) for r in b]),
            "seconds": stats([float(r.get("seconds", 0)) for r in b]),
            "tokens": stats([float(r.get("tokens", 0)) for r in b])},
    }
    # delta sign: with MINUS without. Positive pass delta = skill helps.
    out["delta_pass_rate"] = round(
        out["with_skill"]["pass_rate"]["mean"] -
        out["without_skill"]["pass_rate"]["mean"], 4)
    outdir = Path(a.with_jsonl).parent
    (outdir / "benchmark.json").write_text(json.dumps(out, indent=1))
    (outdir / "benchmark.md").write_text(
        f"# Benchmark: {a.skill_name or 'skill'}\n\n"
        f"- with_skill pass_rate: {out['with_skill']['pass_rate']}\n"
        f"- without_skill pass_rate: {out['without_skill']['pass_rate']}\n"
        f"- **delta_pass_rate (with-minus-without): "
        f"{out['delta_pass_rate']:+.4f}**\n"
        f"  (positive = skill helps; negative = skill hurts)\n")
    print(f"delta_pass_rate: {out['delta_pass_rate']:+.4f} "
          f"(n={len(w)} vs {len(b)})")
    print(f"wrote {outdir/'benchmark.json'} {outdir/'benchmark.md'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
