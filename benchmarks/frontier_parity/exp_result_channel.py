#!/usr/bin/env python3
"""Experiment E2: RESULT.json machine-channel validation (free tier, $0).

Question: does grading a machine-written RESULT.json file (instead of chat
text) restore strict compliance while keeping value intact?

Design:
- TREATMENT (R): mode-R prompts (task + RESULT_CONTRACT_V1), same free model.
  4 wrap-prone text tasks x 2 reps = 8 calls.
- BASELINE: banked mode-A rows for the same 4 tasks (no new calls).
- Grading identical (grade_row); channel recorded per row.

Pre-registered gates (frozen before running; see artifact):
  G1 (primary): R strict_rate >= baseline-A strict + 0.25.
  G2 (non-regression): R value_rate >= baseline-A value - 0.05.
  G3 (mechanism): every R strict PASS has channel=result_json + status valid
      (proves the channel did the work, not chat luck).
  G4 (safety): any rc outside (0, 124) halts with ERROR status, never a pass.
ADOPT the channel contract iff G1+G2+G3 hold; G4 must hold regardless.

Usage: venv/bin/python benchmarks/frontier_parity/exp_result_channel.py
"""

from __future__ import annotations

import json
import shutil
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent.parent))

import modes  # noqa: E402
from run_matrix import grade_row, load_tasks, catalog_snapshot  # noqa: E402

TASKS = ["FV-A01", "FV-T02", "FV-S01", "FV-N01"]
REPS = 2


def main() -> int:
    _, _, tasks = load_tasks("tasks_v2.json")
    by_id = {t["id"]: t for t in tasks}
    catalog = catalog_snapshot("opencode")
    stamp = time.strftime("%Y-%m-%dT%H-%M-%S")
    rows = []
    for rep in range(REPS):
        for tid in TASKS:
            t = by_id[tid]
            rec = modes.run_once(t, "R", "same_capability", "opencode",
                                 paid_ok=False, catalog_snapshot=catalog)
            rec["rep"] = rep
            ctx = dict(rec.get("fixture_ctx", {}) or {})
            ctx["channel"] = rec.get("channel", "chat")
            ctx["candidate_changed"] = rec.get("needed_normalization", False)
            ok, v, f, note = grade_row(t, rec["output"], rec.get("raw_text", ""),
                                       rec.get("files", {}), ctx)
            rec.update({"ok": ok, "value_ok": v, "format_ok": f, "note": note,
                        "outcome": modes.classify_outcome({**rec, "ok": ok, "value_ok": v})})
            rows.append(rec)
            workdir = rec.pop("workdir", None)
            if workdir:
                shutil.rmtree(workdir, ignore_errors=True)
            print(f"[{'PASS' if ok else 'FAIL'}] {tid} rep={rep} "
                  f"channel={rec.get('channel')} rj={rec.get('result_json_status')} "
                  f"value={v} format={f} wall={rec.get('wall_s')}s note={note}", flush=True)
            if rec.get("rc") not in (0, 124):
                print(f"G4 HALT: unexpected rc={rec.get('rc')} on {tid}")
                break
    out = {"experiment": "E2-result-channel", "executed_utc": stamp,
           "treatment": "mode-R (task + RESULT_CONTRACT_V1), free Muse",
           "gates": {"G1": "R strict >= baseline-A strict + 0.25",
                     "G2": "R value >= baseline-A value - 0.05",
                     "G3": "every R strict PASS via channel=result_json+valid",
                     "G4": "no rc outside (0,124)"},
           "rows": rows}
    (HERE / "runs" / f"exp_channel_{stamp}.json").write_text(
        json.dumps(out, indent=1), encoding="utf-8")
    s = sum(1 for r in rows if r["ok"])
    v = sum(1 for r in rows if r["value_ok"])
    print(f"E2 done: strict {s}/{len(rows)} value {v}/{len(rows)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
