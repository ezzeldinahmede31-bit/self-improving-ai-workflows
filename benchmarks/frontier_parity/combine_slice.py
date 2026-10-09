#!/usr/bin/env python3
"""Merge slice batches into one scored artifact (no model calls, no network).

Batch 1: runs/matrix_<ts>.partial.jsonl (35 rows; its 3 FV-C01 rows are
  SUPERSEDED — graded against an unsolvable authoring bug, target 7).
Batch 2: runs/matrix_<ts>.json top-up (6 rows: fixed FV-C01 x3 + FV-A01 x3).

Writes runs/slice_final_<stamp>.json + .csv with full provenance.
Usage: venv/bin/python benchmarks/frontier_parity/combine_slice.py <partial> <topup>
"""

from __future__ import annotations

import csv
import io
import json
import sys
import time
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent


def main() -> int:
    if len(sys.argv) != 3:
        print("usage: combine_slice.py <partial.jsonl> <topup-matrix.json>")
        return 2
    partial = HERE / sys.argv[1] if not Path(sys.argv[1]).is_absolute() else Path(sys.argv[1])
    topup = HERE / sys.argv[2] if not Path(sys.argv[2]).is_absolute() else Path(sys.argv[2])
    b1 = [json.loads(l) for l in partial.read_text(encoding="utf-8").splitlines() if l.strip()]
    b2 = json.loads(topup.read_text(encoding="utf-8"))["rows"]
    for r in b1:
        r["batch"] = 1
    for r in b2:
        r["batch"] = 2
    superseded = [r for r in b1 if r["task"] == "FV-C01"]
    for r in superseded:
        r["superseded_reason"] = ("authoring bug: first case target=7 unsolvable; "
                                  "C01 re-ran fixed (target=9) in batch 2")
    rows = [r for r in b1 if r["task"] != "FV-C01"] + b2
    # Recompute all flags under current grader semantics (v1.1.1 exact-dual +
    # case-insensitive fileset): stored flags from older semantics are kept
    # as orig_* for the audit trail, never silently overwritten.
    sys.path.insert(0, str(HERE))
    sys.path.insert(0, str(HERE.parent.parent))
    import graders as _g  # noqa: E402
    from run_matrix import grade_row as _grade_row, load_tasks as _load  # noqa: E402
    _, _, _tasks = _load("tasks_v2.json")
    _by_id = {t["id"]: t for t in _tasks}
    from fixtures import build_fixtures as _build
    for r in rows:
        t = _by_id.get(r["task"])
        if t is None:
            continue
        ctx = dict(r.get("fixture_ctx", {}) or {})
        if isinstance(t.get("fixture"), dict):
            # Deterministic regeneration check: identical seeds must yield
            # byte-identical inputs. If so, grade with CURRENT builder ctx
            # (answer-key contract fixes apply); else keep stored ctx + flag.
            fresh_files, fresh_ctx = _build(t["fixture"])
            stored_files = r.get("files", {}) or {}
            identical = all(k in stored_files and stored_files[k] == v
                            for k, v in fresh_files.items())
            if identical:
                ctx = dict(fresh_ctx)
                for k, v in (t.get("grader") or {}).items():
                    if k != "kind":
                        ctx.setdefault(k, v)
                r["ctx_refreshed"] = True
            else:
                r["ctx_refreshed"] = False
        ok, v, f, note = _grade_row(t, r.get("output", ""), r.get("raw_text", ""),
                                    r.get("files", {}), ctx)
        r["orig_ok"], r["orig_value_ok"], r["orig_format_ok"], r["orig_note"] = (
            r.get("ok"), r.get("value_ok"), r.get("format_ok"), r.get("note"))
        r["ok"], r["value_ok"], r["format_ok"], r["note"] = ok, v, f, note
    by_mode_s = defaultdict(lambda: [0, 0])
    by_mode_v = defaultdict(lambda: [0, 0])
    for r in rows:
        by_mode_s[r["mode"]][1] += 1
        by_mode_v[r["mode"]][1] += 1
        if r.get("ok"):
            by_mode_s[r["mode"]][0] += 1
        if r.get("value_ok"):
            by_mode_v[r["mode"]][0] += 1
    n = len(rows)
    stamp = time.strftime("%Y-%m-%dT%H-%M-%S")
    out = {"benchmark": "frontier_parity_full slice (12 tasks x A/B/C)",
           "harness": "v1.1.1", "executed_utc": stamp,
           "status": ("partial slice: 12/44 tasks x A/B/C x ~1 rep (A01 has extra reps); "
                      "C01 batch-1 rows superseded by fixed-case batch-2 reruns"),
           "strict": {k: f"{v[0]}/{v[1]}" for k, v in sorted(by_mode_s.items())},
           "value": {k: f"{v[0]}/{v[1]}" for k, v in sorted(by_mode_v.items())},
           "strict_rate": round(sum(v[0] for v in by_mode_s.values()) / n, 4),
           "value_rate": round(sum(v[0] for v in by_mode_v.values()) / n, 4),
           "rows": rows, "superseded": superseded}
    (HERE / "runs" / f"slice_final_{stamp}.json").write_text(
        json.dumps(out, indent=1), encoding="utf-8")
    buf = io.StringIO()
    w = csv.DictWriter(buf, fieldnames=["task", "mode", "batch", "rep", "ok", "value_ok",
                                        "format_ok", "first_pass_ok", "recovered", "wall_s",
                                        "tool_uses", "token_status", "note"])
    w.writeheader()
    for r in rows:
        w.writerow({k: r.get(k) for k in w.fieldnames})
    (HERE / "runs" / f"slice_final_{stamp}.csv").write_text(buf.getvalue(), encoding="utf-8")
    print(f"slice final: strict={out['strict_rate']} value={out['value_rate']} "
          f"({n} rows, {len(superseded)} superseded) -> runs/slice_final_{stamp}.json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
