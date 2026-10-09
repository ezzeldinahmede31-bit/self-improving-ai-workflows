#!/usr/bin/env python3
"""Deterministic re-score of a stored matrix artifact with grader v1.1.

No model calls, no network: recomputes value_ok/format_ok from stored
raw_text/output/files/fixture_ctx. Writes runs/rescore_<stamp>.json.
Proves the v1.1 calibration on already-measured rows.

Usage: venv/bin/python benchmarks/frontier_parity/rescore.py runs/matrix_<ts>.json
"""

from __future__ import annotations

import json
import sys
import time
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent.parent))

import graders  # noqa: E402
from run_matrix import grade_row, load_tasks  # noqa: E402


def main() -> int:
    if len(sys.argv) != 2:
        print("usage: rescore.py runs/matrix_<ts>.json")
        return 2
    art_path = HERE / sys.argv[1] if not Path(sys.argv[1]).is_absolute() else Path(sys.argv[1])
    art = json.loads(art_path.read_text(encoding="utf-8"))
    _, _, tasks = load_tasks(art.get("battery_version", "tasks_v1.json").split()[0])
    by_id = {t["id"]: t for t in tasks}
    rows = []
    for r in art["rows"]:
        t = by_id.get(r["task"])
        if t is None:
            print(f"REFUSED: task {r['task']} not in battery file")
            return 2
        ctx = r.get("fixture_ctx", {}) or {}
        if "fixture_total" in r and "fixture_total" not in ctx:
            ctx["fixture_total"] = r["fixture_total"]
        if r.get("recovered") and r.get("attempt", 0) > 0:
            # v1 artifacts did not store the repair attempt's raw text, so
            # post-hoc format re-verification is impossible. Value IS
            # re-verifiable from the stored (repair) output. Strict stays as
            # originally measured; format is reported UNVERIFIABLE, never guessed.
            from run_matrix import grade_row as _gr  # noqa: F401 (already imported)
            ok, v, _f, note = grade_row(t, r.get("output", ""), r.get("output", ""),
                                        r.get("files", {}), ctx)
            rows.append({"task": r["task"], "mode": r["mode"], "rep": r.get("rep"),
                         "old_ok": r.get("ok"), "strict_ok": r.get("ok"),
                         "value_ok": v, "format_ok": "UNVERIFIABLE-post-hoc",
                         "note": note + " [recovered row: format taken as measured]"})
            continue
        ok, v, f, note = grade_row(t, r.get("output", ""), r.get("raw_text", ""),
                                   r.get("files", {}), ctx)
        rows.append({"task": r["task"], "mode": r["mode"], "rep": r.get("rep"),
                     "old_ok": r.get("ok"), "strict_ok": ok,
                     "value_ok": v, "format_ok": f, "note": note})
    by_mode_s = defaultdict(lambda: [0, 0])
    by_mode_v = defaultdict(lambda: [0, 0])
    for r in rows:
        by_mode_s[r["mode"]][1] += 1
        by_mode_v[r["mode"]][1] += 1
        if r["strict_ok"]:
            by_mode_s[r["mode"]][0] += 1
        if r["value_ok"]:
            by_mode_v[r["mode"]][0] += 1
    n = len(rows)
    out = {"rescored_utc": time.strftime("%Y-%m-%dT%H-%M-%S"),
           "source": art_path.name, "harness": "v1.1-rescore",
           "strict": {k: f"{v[0]}/{v[1]}" for k, v in sorted(by_mode_s.items())},
           "value": {k: f"{v[0]}/{v[1]}" for k, v in sorted(by_mode_v.items())},
           "strict_rate": round(sum(v[0] for v in by_mode_s.values()) / n, 4),
           "value_rate": round(sum(v[0] for v in by_mode_v.values()) / n, 4),
           "rows": rows}
    dest = HERE / "runs" / f"rescore_{out['rescored_utc']}.json"
    dest.write_text(json.dumps(out, indent=1), encoding="utf-8")
    print(f"rescore: strict={out['strict_rate']} value={out['value_rate']} -> {dest.name}")
    for r in rows:
        if r["old_ok"] != r["strict_ok"]:
            print(f"  CHANGED {r['task']} {r['mode']}: stored={r['old_ok']} v1.1={r['strict_ok']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
