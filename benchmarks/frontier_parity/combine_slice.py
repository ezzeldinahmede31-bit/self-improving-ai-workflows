#!/usr/bin/env python3
"""Merge N batch artifacts into one scored artifact (no model calls, no network).

Inputs: any mix of runs/matrix_<ts>.partial.jsonl and runs/matrix_<ts>.json.
What it does per row:
 1. drops rows matching --drop TASKID (recorded in `superseded` with reason);
 2. tags batch = source file order (1-based);
 3. refreshes ctx: regenerates deterministic fixtures; when regenerated INPUT
    files are byte-identical to the stored ones, grades with CURRENT builder
    ctx (answer-key contract fixes apply); else keeps stored ctx. Task grader
    params always OVERWRITE fixture ctx (mirrors modes.setup_workdir);
 4. recomputes (ok, value_ok, format_ok, note) with current graders; originals
    kept as orig_* — never silently overwritten;
 5. writes runs/<label>_<stamp>.json + .csv with strict/value summaries.

Usage:
  venv/bin/python benchmarks/frontier_parity/combine_slice.py --label slice_final \
    --tasks-file tasks_v2.json --drop "FV-C01:authoring bug target=7; fixed rerun in batch 2" \
    runs/a.partial.jsonl runs/b.json
"""

from __future__ import annotations

import argparse
import csv
import io
import json
import sys
import time
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent.parent))


def load_rows(path: Path) -> list[dict]:
    if path.suffix == ".jsonl":
        return [json.loads(l) for l in path.read_text(encoding="utf-8").splitlines() if l.strip()]
    return json.loads(path.read_text(encoding="utf-8"))["rows"]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--label", default="combined")
    ap.add_argument("--tasks-file", default="tasks_v2.json")
    ap.add_argument("--drop", action="append", default=[],
                    help="'TASKID:reason' — rows dropped to superseded")
    ap.add_argument("files", nargs="+")
    args = ap.parse_args()

    import graders as _g  # noqa: E402,F401
    from run_matrix import grade_row as _grade_row, load_tasks as _load  # noqa: E402
    from fixtures import build_fixtures as _build  # noqa: E402

    _, _, _tasks = _load(args.tasks_file)
    by_id = {t["id"]: t for t in _tasks}
    drops = {}
    for spec in args.drop:
        tid, _, reason = spec.partition(":")
        tid = tid.strip()
        if "@" in tid:
            name, _, batch = tid.partition("@")
            drops[(name.strip(), int(batch))] = reason.strip() or "superseded"
        else:
            drops[(tid, None)] = reason.strip() or "superseded"

    def dropped(task: str, batch: int):
        if (task, batch) in drops:
            return drops[(task, batch)]
        return drops.get((task, None))

    rows, superseded = [], []
    for bi, f in enumerate(args.files, 1):
        p = HERE / f if not Path(f).is_absolute() else Path(f)
        for r in load_rows(p):
            t = by_id.get(r.get("task"))
            if t is None:
                print(f"REFUSED: task {r.get('task')} not in {args.tasks_file}")
                return 2
            reason = dropped(r.get("task"), bi)
            if reason:
                r["batch"] = bi
                r["superseded_reason"] = reason
                superseded.append(r)
                continue
            ctx = dict(r.get("fixture_ctx", {}) or {})
            spec = t.get("fixture")
            if isinstance(spec, dict):
                fresh_files, fresh_ctx = _build(spec)
                stored_files = r.get("files", {}) or {}
                identical = all(k in stored_files and stored_files[k] == v
                                for k, v in fresh_files.items())
                if identical:
                    ctx = dict(fresh_ctx)
                    r["ctx_refreshed"] = True
                else:
                    r["ctx_refreshed"] = False
            g = t.get("grader") if isinstance(t.get("grader"), dict) else None
            if g:
                for k, v in g.items():
                    if k != "kind":
                        ctx[k] = v  # task pins win (mirrors setup_workdir)
            ok, v, fm, note = _grade_row(t, r.get("output", ""), r.get("raw_text", ""),
                                         r.get("files", {}), ctx)
            r["orig_ok"], r["orig_value_ok"], r["orig_format_ok"], r["orig_note"] = (
                r.get("ok"), r.get("value_ok"), r.get("format_ok"), r.get("note"))
            r["ok"], r["value_ok"], r["format_ok"], r["note"] = ok, v, fm, note
            r.setdefault("batch", bi)  # never collapse an existing batch tag
            r["src"] = Path(f).name
            rows.append(r)

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
    out = {"benchmark": f"frontier combine {args.label}",
           "harness": "v1.1.1+", "executed_utc": stamp,
           "status": f"combined {n} rows from {len(args.files)} batches; "
                     f"{len(superseded)} superseded",
           "strict": {k: f"{v[0]}/{v[1]}" for k, v in sorted(by_mode_s.items())},
           "value": {k: f"{v[0]}/{v[1]}" for k, v in sorted(by_mode_v.items())},
           "strict_rate": round(sum(v[0] for v in by_mode_s.values()) / max(n, 1), 4),
           "value_rate": round(sum(v[0] for v in by_mode_v.values()) / max(n, 1), 4),
           "rows": rows, "superseded": superseded}
    (HERE / "runs" / f"{args.label}_{stamp}.json").write_text(
        json.dumps(out, indent=1), encoding="utf-8")
    buf = io.StringIO()
    w = csv.DictWriter(buf, fieldnames=["task", "mode", "batch", "rep", "ok", "value_ok",
                                        "format_ok", "first_pass_ok", "recovered", "wall_s",
                                        "tool_uses", "token_status", "note"])
    w.writeheader()
    for r in rows:
        w.writerow({k: r.get(k) for k in w.fieldnames})
    (HERE / "runs" / f"{args.label}_{stamp}.csv").write_text(buf.getvalue(), encoding="utf-8")
    print(f"combined: strict={out['strict_rate']} value={out['value_rate']} "
          f"({n} rows, {len(superseded)} superseded) -> runs/{args.label}_{stamp}.json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
