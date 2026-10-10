#!/usr/bin/env python3
"""Experiment E1: format-contract ablation (free tier, $0).

Question: does ONE added prompt block (a strict reply contract, nothing else)
raise strict-format compliance without regressing value-correctness?

Design (ablation, single variable):
- BASELINE: banked mode-A rows for 6 wrap-prone tasks (strict ~0, value ~1).
- TREATMENT (E1): identical mode-A prompts + FORMAT_CONTRACT_V1 appended.
  Same model, same tasks, same graders, same timeouts. 3 reps each.
- Metrics: strict rate (primary), value rate (must not regress), mean wall.
- Verdict rule (pre-registered): ADOPT iff strict improves by >= 0.25 absolute
  with value delta >= -0.05 and no new error classes; else REJECT.
- Writes runs/exp_format_<stamp>.json. Never touches frozen batteries.

Usage: venv/bin/python benchmarks/frontier_parity/exp_format.py
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

FORMAT_CONTRACT_V1 = (
    "# Reply contract (E1): your ENTIRE reply must consist of exactly the "
    "requested artifact and nothing else — no greeting, no narration, no "
    "explanation, no markdown fences, no trailing commentary. An exact-match "
    "validator grades the reply; any extra text fails the task even when the "
    "computed value is right."
)

TASKS = ["FV-A01", "FV-T02", "FV-S01", "FV-N01", "FV-U02", "FV-X02"]
REPS = 3


def main() -> int:
    _, _, tasks = load_tasks("tasks_v2.json")
    by_id = {t["id"]: t for t in tasks}
    catalog = catalog_snapshot("opencode")
    stamp = time.strftime("%Y-%m-%dT%H-%M-%S")
    rows = []
    for rep in range(REPS):
        for tid in TASKS:
            t = by_id[tid]
            prompt = t["prompt"] + "\n\n" + FORMAT_CONTRACT_V1
            workdir, ctx = modes.setup_workdir(t)
            try:
                att = modes.spawn_attempt("opencode", modes.MUSE_FREE, prompt,
                                          workdir, f"expE1-{tid}-r{rep}",
                                          t.get("timeout_s", 180))
                texts, tool_uses, errors, usage, keys = modes._extract_text_events(
                    att["raw_out"])
                raw = "\n".join(texts).strip()
                norm, changed = modes.normalize_output(tid, raw, t)
                ok, v, f, note = grade_row(t, norm, raw, modes.snapshot_workdir(workdir)[0], ctx)
                rec = {"task": tid, "mode": "E1", "rep": rep, "model": modes.MUSE_FREE,
                       "prompt_sha": modes.prompt_hash(prompt), "raw_text": raw[:2000],
                       "output": norm[:2000], "needed_normalization": changed,
                       "wall_s": att["wall"], "tool_uses": tool_uses, "errors": errors[:3],
                       "token_status": "MEASURED" if usage else "UNMEASURED",
                       "ok": ok, "value_ok": v, "format_ok": f, "note": note,
                       "catalog": catalog}
                rows.append(rec)
                print(f"[{'PASS' if ok else 'FAIL'}] {tid} rep={rep} value={v} "
                      f"format={f} wall={att['wall']}s note={note}", flush=True)
            finally:
                shutil.rmtree(workdir, ignore_errors=True)
    out = {"experiment": "E1-format-contract", "executed_utc": stamp,
           "treatment": "mode-A prompt + FORMAT_CONTRACT_V1 (single variable)",
           "verdict_rule": "ADOPT iff strict>=baseline+0.25 and value_delta>=-0.05",
           "rows": rows}
    (HERE / "runs" / f"exp_format_{stamp}.json").write_text(
        json.dumps(out, indent=1), encoding="utf-8")
    s = sum(1 for r in rows if r["ok"])
    v = sum(1 for r in rows if r["value_ok"])
    print(f"E1 done: strict {s}/{len(rows)} value {v}/{len(rows)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
