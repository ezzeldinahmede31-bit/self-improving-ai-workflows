#!/usr/bin/env python3
"""Frontier-parity matrix runner (harness v1.0.0).

Usage:
    venv/bin/python benchmarks/frontier_parity/run_matrix.py --dry-run
    venv/bin/python benchmarks/frontier_parity/run_matrix.py --modes A --repeats 1 --tasks FP-R01
    venv/bin/python benchmarks/frontier_parity/run_matrix.py --modes A,B,C --repeats 2   # free only
    venv/bin/python benchmarks/frontier_parity/run_matrix.py --modes D --paid-ok --paid-cap-usd 5  # PAID

Rules enforced here (not in prompts):
- sealed tasks (prompt=null) are REFUSED, never run.
- mode D (Fable 5.1, paid) requires --paid-ok AND --paid-cap-usd; aborts past cap.
- mode C repairs use grader notes only (execution feedback), max 2 repairs.
- artifacts: JSON + CSV under benchmarks/frontier_parity/runs/ with benchmark
  version, timestamp, catalog snapshot, settings, per-attempt rows.
- NEVER writes a verdict (parity/superiority). Verdicts come from the final
  evaluation against acceptance_v1.json on the FULL battery only.
"""

from __future__ import annotations

import argparse
import csv
import io
import json
import shutil
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT / "benchmarks" / "frontier_parity"))

import graders  # noqa: E402
import modes  # noqa: E402

HERE = Path(__file__).resolve().parent
RUNS = HERE / "runs"

FABLE_EST_PER_CALL_USD = 0.05  # conservative pre-run estimate; real cost from stats deltas


def load_tasks() -> list[dict]:
    return json.loads((HERE / "tasks_v1.json").read_text(encoding="utf-8"))["tasks"]


def catalog_snapshot(opencode_bin: str) -> dict:
    """Live catalog entries for the two pinned models (trusted metadata)."""
    try:
        out = subprocess.run([opencode_bin, "models", "--verbose"],
                             capture_output=True, text=True, timeout=60)
    except Exception as exc:  # noqa: BLE001
        return {"error": f"catalog unreadable: {exc.__class__.__name__}"}
    snap: dict = {}
    import re
    for m in re.finditer(r"^(opencode/[^\s]+)\n(\{.*?\n\})", out.stdout, re.M | re.S):
        mid = m.group(1)
        if mid in (modes.MUSE_FREE, modes.FABLE_51):
            try:
                d = json.loads(m.group(2))
                snap[mid] = {"status": d.get("status"), "cost": d.get("cost"),
                             "limit": d.get("limit"),
                             "toolcall": (d.get("capabilities") or {}).get("toolcall"),
                             "reasoning": (d.get("capabilities") or {}).get("reasoning"),
                             "temperature": (d.get("capabilities") or {}).get("temperature")}
            except ValueError:
                snap[mid] = {"parse_error": True}
    return snap


def stats_snapshot(opencode_bin: str) -> dict:
    try:
        out = subprocess.run([opencode_bin, "stats", "--models"],
                             capture_output=True, text=True, timeout=60)
        return {"ok": out.returncode == 0, "text": (out.stdout or "")[-2000:]}
    except Exception as exc:  # noqa: BLE001
        return {"ok": False, "text": f"stats unreadable: {exc.__class__.__name__}"}


def grade_record(rec: dict) -> dict:
    ok, note = graders.grade(rec["task"], rec["output"],
                             {"fixture_total": rec.get("fixture_total")})
    rec["ok"] = bool(ok)
    rec["note"] = str(note)
    return rec


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--modes", default="A",
                    help="comma list among A,B,C,D")
    ap.add_argument("--variant", default="same_capability")
    ap.add_argument("--repeats", type=int, default=1)
    ap.add_argument("--tasks", default="",
                    help="comma task ids; default = all non-sealed pilot tasks")
    ap.add_argument("--dry-run", action="store_true",
                    help="validate tasks/modes/graders without spawning any model")
    ap.add_argument("--paid-ok", action="store_true")
    ap.add_argument("--paid-cap-usd", type=float, default=0.0)
    ap.add_argument("--opencode-bin", default="opencode")
    ap.add_argument("--max-repairs", type=int, default=2)
    args = ap.parse_args()

    all_tasks = load_tasks()
    wanted = [t.strip() for t in args.tasks.split(",") if t.strip()]
    tasks = [t for t in all_tasks if not t.get("held_out")
             and (not wanted or t["id"] in wanted)]
    if wanted and len(tasks) != len(wanted):
        print(f"REFUSED: unknown task ids: {sorted(set(wanted) - {t['id'] for t in tasks})}")
        return 2
    modelist = [m.strip() for m in args.modes.split(",") if m.strip()]
    if any(m not in ("A", "B", "C", "D") for m in modelist):
        print("REFUSED: modes must be among A,B,C,D")
        return 2
    if "D" in modelist and not (args.paid_ok and args.paid_cap_usd > 0):
        print("REFUSED: mode D is PAID — pass --paid-ok and --paid-cap-usd > 0")
        return 2

    if args.dry_run:
        n = 0
        for t in tasks:
            for m in modelist:
                modes.build_prompt(m, t, args.variant)  # raises on sealed/unknown
                if t["id"] not in graders.GRADERS:
                    print(f"REFUSED: {t['id']} has no registered grader")
                    return 2
                n += 1
        print(f"dry-run OK: {len(tasks)} tasks x {modelist} valid, "
              f"{n} prompt builds, graders registered, nothing spawned")
        return 0

    catalog = catalog_snapshot(args.opencode_bin)
    stats_before = stats_snapshot(args.opencode_bin)
    stamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H-%M-%S")
    rows: list[dict] = []
    paid_est = 0.0
    for rep in range(args.repeats):
        for t in tasks:
            for m in modelist:
                if m == "D":
                    paid_est += FABLE_EST_PER_CALL_USD * (1 + args.max_repairs)
                    if paid_est > args.paid_cap_usd:
                        print(f"BUDGET STOP: projected paid spend past cap "
                              f"({args.paid_cap_usd}); matrix halted, partial results kept")
                        break
                try:
                    rec = modes.run_once(t, m, args.variant, args.opencode_bin,
                                         paid_ok=args.paid_ok, catalog_snapshot=catalog)
                except modes.Refused as exc:
                    print(f"REFUSED: {exc}")
                    return 2
                rec["rep"] = rep
                rec["attempt"] = 0
                grade_record(rec)
                first_ok = rec["ok"]
                rec["first_pass_ok"] = first_ok
                # C-mode repair loop: grader notes only, bounded
                attempt = 0
                while m == "C" and not rec["ok"] and attempt < args.max_repairs:
                    attempt += 1
                    try:
                        prompt = modes.build_prompt(m, t, args.variant,
                                                    repair_note=f"grader: {rec['note']}")
                    except modes.Refused as exc:  # noqa: BLE001 - cannot happen post-check
                        rec["repair_error"] = str(exc)
                        break
                    import tempfile
                    workdir = tempfile.mkdtemp(prefix="fp_repair_")
                    fixture_total = None
                    try:
                        if t.get("needs_workdir_fixtures"):
                            fixture_total = modes.make_t01_fixtures(workdir)
                        argv = [args.opencode_bin, "run", "--dir", workdir,
                                "-m", modes.model_for(m), "--format", "json",
                                "--title", f"fp-{t['id']}-{m}-r{attempt}", prompt]
                        t0 = time.time()
                        try:
                            proc = subprocess.run(argv, capture_output=True, text=True,
                                                  timeout=t.get("timeout_s", 180))
                            wall = round(time.time() - t0, 2)
                            raw_out, rc = proc.stdout or "", proc.returncode
                        except subprocess.TimeoutExpired:
                            wall = round(time.time() - t0, 2)
                            raw_out, rc = "", 124
                        texts, tool_uses, errors, usage, keys = modes._extract_text_events(raw_out)
                        raw_text = "\n".join(texts).strip()
                        normalized, changed = modes.normalize_output(t["id"], raw_text)
                        rec[f"repair{attempt}_ok"], rec[f"repair{attempt}_note"] = graders.grade(
                            t["id"], normalized, {"fixture_total": fixture_total})
                        rec[f"repair{attempt}_wall_s"] = wall
                        rec[f"repair{attempt}_tool_uses"] = tool_uses
                        if rec[f"repair{attempt}_ok"]:
                            rec["output"] = normalized
                            rec["ok"] = True
                            rec["note"] = f"recovered on repair {attempt}"
                            rec["attempt"] = attempt
                    finally:
                        shutil.rmtree(workdir, ignore_errors=True)
                rec["recovered"] = bool(not first_ok and rec["ok"])
                rows.append(rec)
                workdir = rec.pop("workdir", None)
                if workdir:
                    shutil.rmtree(workdir, ignore_errors=True)
                status = "PASS" if rec["ok"] else "FAIL"
                print(f"[{status}] {t['id']} mode={m} rep={rep} "
                      f"first={first_ok} wall={rec.get('wall_s')}s "
                      f"tokens={rec.get('token_status')} note={rec.get('note')}", flush=True)

    stats_after = stats_snapshot(args.opencode_bin)
    RUNS.mkdir(parents=True, exist_ok=True)
    artifact = {
        "benchmark": "frontier_parity_pilot",
        "harness": modes.HARNESS_VERSION,
        "batter_version": "tasks_v1 1.0.0",
        "executed_utc": stamp,
        "settings": {"modes": modelist, "variant": args.variant,
                     "repeats": args.repeats, "max_repairs": args.max_repairs,
                     "paid_ok": args.paid_ok, "paid_cap_usd": args.paid_cap_usd,
                     "paid_est_usd": round(paid_est, 4)},
        "catalog": catalog,
        "stats_before": stats_before, "stats_after": stats_after,
        "rows": rows,
    }
    (RUNS / f"matrix_{stamp}.json").write_text(json.dumps(artifact, indent=1), encoding="utf-8")
    buf = io.StringIO()
    w = csv.DictWriter(buf, fieldnames=["task", "mode", "variant", "model", "rep",
                                        "ok", "first_pass_ok", "recovered", "wall_s",
                                        "tool_uses", "token_status", "needed_normalization",
                                        "note"])
    w.writeheader()
    for r in rows:
        w.writerow({k: r.get(k) for k in w.fieldnames})
    (RUNS / f"matrix_{stamp}.csv").write_text(buf.getvalue(), encoding="utf-8")
    n_pass = sum(1 for r in rows if r["ok"])
    print(f"matrix done: {n_pass}/{len(rows)} passed -> runs/matrix_{stamp}.json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
