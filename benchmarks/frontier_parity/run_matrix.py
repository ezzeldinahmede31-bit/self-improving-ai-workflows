#!/usr/bin/env python3
"""Frontier-parity matrix runner (harness v1.1.0).

Usage:
    venv/bin/python benchmarks/frontier_parity/run_matrix.py --dry-run
    venv/bin/python benchmarks/frontier_parity/run_matrix.py --modes A --repeats 1 --tasks FP-R01
    venv/bin/python benchmarks/frontier_parity/run_matrix.py --modes A,B,C --repeats 2   # free only
    venv/bin/python benchmarks/frontier_parity/run_matrix.py --modes D --paid-ok --paid-cap-usd 5  # PAID
    venv/bin/python benchmarks/frontier_parity/run_matrix.py --tasks-file tasks_v2.json --modes A --dry-run

Rules enforced here (not in prompts):
- sealed tasks (prompt=null) are REFUSED, never run.
- mode D (Fable 5.1, paid) requires --paid-ok AND --paid-cap-usd; aborts past cap.
- mode C repairs use grader notes only (execution feedback), max 2 repairs;
  v1.1 notes distinguish VALUE_WRONG from VALUE_OK_FORMAT_BAD.
- Dual scoring: value_ok (capability) + format_ok (compliance); strict ok =
  both (file-deliverable tasks: value only, format N/A=True).
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


def load_tasks(path: str) -> tuple[str, str, list[dict]]:
    doc = json.loads((HERE / path).read_text(encoding="utf-8"))
    return doc.get("battery", "?"), doc.get("battery_version", "?"), doc["tasks"]


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
    """Full stats output (v1.1: no tail-truncation that hid the cost panel)."""
    try:
        out = subprocess.run([opencode_bin, "stats", "--models"],
                             capture_output=True, text=True, timeout=60)
        return {"ok": out.returncode == 0, "text": (out.stdout or "")[:30000]}
    except Exception as exc:  # noqa: BLE001
        return {"ok": False, "text": f"stats unreadable: {exc.__class__.__name__}"}


def grade_row(task: dict, output: str, raw: str, files: dict, ctx: dict):
    """Returns (strict_ok, value_ok, format_ok, note)."""
    gspec = task.get("grader") if isinstance(task.get("grader"), dict) else None
    if gspec is None:
        v, f, n = graders.grade2(task["id"], raw, output,
                                 {"fixture_total": ctx.get("fixture_total")})
        return (v and f), v, f, n
    kind = gspec.get("kind")
    if kind == "exact":
        return graders.grade_exact_dual(raw, output, ctx)
    if kind in ("filemodule", "fileset", "filejson"):
        ok, note = graders.FILE_GRADERS[kind](files, ctx)
        return ok, ok, True, note + " [format N/A: file deliverable]"
    if kind == "schedule":
        from fixtures import grade_schedule_ctx
        ok, note = grade_schedule_ctx(output, ctx)
    else:
        ok, note = graders.grade_generic(kind, output, ctx)
    if not ok:
        return False, False, False, f"VALUE_WRONG: {note}"
    fmt = ((raw or "").strip() == (output or "").strip())
    if fmt:
        return True, True, True, ""
    return False, True, False, "VALUE_OK_FORMAT_BAD: correct artifact wrapped in extra text"


def repair_note(task: dict, value_ok: bool, note: str) -> str:
    if value_ok and "VALUE_OK_FORMAT_BAD" in note:
        return ("grader: VALUE_OK_FORMAT_BAD — the computed value/artifact is correct, "
                "but the reply wraps it in extra prose. Reply with ONLY the requested artifact.")
    return f"grader: {note}"


def repair_visible_task(task: dict) -> dict:
    """Copy of the task whose exec grader exposes ONLY the visible repair
    subset. Hidden cases stay hidden so a repair cannot hardcode the test:
    the final grade (full cases) then measures generalization, not mimicry."""
    import copy
    t2 = copy.deepcopy(task)
    g = t2.get("grader")
    if isinstance(g, dict) and isinstance(g.get("repair_cases"), list) and g["repair_cases"]:
        g["cases"] = g["repair_cases"]
    return t2


def repair_attempt(args, task: dict, mode: str, note: str) -> dict:
    """One bounded repair in a FRESH workdir (fixtures are deterministic)."""
    prompt = modes.build_prompt(mode, task, args.variant, repair_note=note)
    workdir, fixture_ctx = modes.setup_workdir(task)
    try:
        att = modes.spawn_attempt(args.opencode_bin, modes.model_for(mode), prompt,
                                  workdir, f"fp-{task['id']}-{mode}-repair",
                                  task.get("timeout_s", 180))
        texts, tool_uses, _, _, _ = modes._extract_text_events(att["raw_out"])
        raw_text = "\n".join(texts).strip()
        normalized, _ = modes.normalize_output(task["id"], raw_text, task)
        files, _ = modes.snapshot_workdir(workdir)
        return {"raw": raw_text, "normalized": normalized, "files": files,
                "ctx": fixture_ctx, "wall": att["wall"], "tool_uses": tool_uses}
    finally:
        shutil.rmtree(workdir, ignore_errors=True)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--modes", default="A",
                    help="comma list among A,B,C,D")
    ap.add_argument("--variant", default="same_capability")
    ap.add_argument("--repeats", type=int, default=1)
    ap.add_argument("--tasks", default="",
                    help="comma task ids; default = all non-sealed tasks in file")
    ap.add_argument("--tasks-file", default="tasks_v1.json")
    ap.add_argument("--dry-run", action="store_true",
                    help="validate tasks/modes/graders (+fixtures) without spawning")
    ap.add_argument("--paid-ok", action="store_true")
    ap.add_argument("--paid-cap-usd", type=float, default=0.0)
    ap.add_argument("--opencode-bin", default="opencode")
    ap.add_argument("--max-repairs", type=int, default=2)
    ap.add_argument("--finalize-partial", default="",
                    help="finalize a .partial.jsonl into JSON+CSV without spawning")
    ap.add_argument("--resume-from", default="",
                    help="skip (task,mode,rep) combos already in this .partial.jsonl; "
                         "new rows go to a fresh stamp (merge with combine later)")
    args = ap.parse_args()

    if args.finalize_partial:
        from datetime import datetime as _dt
        p = RUNS / args.finalize_partial if not Path(args.finalize_partial).is_absolute() \
            else Path(args.finalize_partial)
        rows = [json.loads(l) for l in p.read_text(encoding="utf-8").splitlines() if l.strip()]
        stamp = _dt.now(timezone.utc).strftime("%Y-%m-%dT%H-%M-%S")
        artifact = {
            "benchmark": "frontier_parity_full (slice)", "harness": modes.HARNESS_VERSION,
            "battery_version": "tasks_v2.json 1.0.0", "executed_utc": stamp,
            "status": f"partial: finalized from {p.name} (run interrupted before end)",
            "settings": {"modes": sorted({r.get('mode') for r in rows}),
                         "variant": rows[0].get("variant") if rows else "?",
                         "note": "see source partial for per-row settings"},
            "catalog": rows[0].get("catalog", {}) if rows else {},
            "stats_before": {}, "stats_after": stats_snapshot(args.opencode_bin),
            "rows": rows,
        }
        (RUNS / f"matrix_{stamp}.json").write_text(json.dumps(artifact, indent=1), encoding="utf-8")
        buf = io.StringIO()
        w = csv.DictWriter(buf, fieldnames=["task", "mode", "variant", "model", "rep",
                                            "ok", "value_ok", "format_ok", "first_pass_ok",
                                            "recovered", "wall_s", "tool_uses", "token_status",
                                            "needed_normalization", "note"])
        w.writeheader()
        for r in rows:
            w.writerow({k: r.get(k) for k in w.fieldnames})
        (RUNS / f"matrix_{stamp}.csv").write_text(buf.getvalue(), encoding="utf-8")
        n = sum(1 for r in rows if r["ok"])
        print(f"finalized partial: {n}/{len(rows)} passed -> runs/matrix_{stamp}.json")
        return 0

    battery, bver, all_tasks = load_tasks(args.tasks_file)
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
                n += 1
            if t.get("fixture"):
                from fixtures import build_fixtures
                files, ctx = build_fixtures(t["fixture"])  # raises on unknown builder
                if not files or not ctx:
                    print(f"REFUSED: {t['id']} fixture produced empty files/ctx")
                    return 2
            gspec = t.get("grader") if isinstance(t.get("grader"), dict) else None
            if gspec is None and t["id"] not in graders.GRADERS:
                print(f"REFUSED: {t['id']} has no registered grader")
                return 2
            if gspec is not None and gspec.get("kind") not in (
                    "exact", "exec", "order", "jsonfacts", "filemodule",
                    "fileset", "filejson", "schedule"):
                print(f"REFUSED: {t['id']} unknown grader kind")
                return 2
        print(f"dry-run OK: {battery} v{bver}: {len(tasks)} tasks x {modelist} valid, "
              f"{n} prompt builds, fixtures+graders registered, nothing spawned")
        return 0

    catalog = catalog_snapshot(args.opencode_bin)
    stats_before = stats_snapshot(args.opencode_bin)
    stamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H-%M-%S")
    RUNS.mkdir(parents=True, exist_ok=True)
    partial_path = RUNS / f"matrix_{stamp}.partial.jsonl"
    partial_fh = open(partial_path, "w", encoding="utf-8")
    rows: list[dict] = []
    paid_est = 0.0
    abort_reason = ""
    done: set[tuple] = set()
    if args.resume_from:
        rp = RUNS / args.resume_from if not Path(args.resume_from).is_absolute() \
            else Path(args.resume_from)
        for line in rp.read_text(encoding="utf-8").splitlines():
            if line.strip():
                d = json.loads(line)
                done.add((d.get("task"), d.get("mode"), d.get("rep")))
        print(f"resume: skipping {len(done)} completed combos from {rp.name}")
    try:
      for rep in range(args.repeats):
        for t in tasks:
            for m in modelist:
                if (t["id"], m, rep) in done:
                    print(f"[SKIP] {t['id']} mode={m} rep={rep} (already in resume file)", flush=True)
                    continue
                if abort_reason:
                    break
                if m == "D":
                    paid_est += FABLE_EST_PER_CALL_USD * (1 + args.max_repairs)
                    if paid_est > args.paid_cap_usd:
                        abort_reason = (f"BUDGET STOP: projected paid spend past cap "
                                        f"({args.paid_cap_usd})")
                        print(abort_reason + "; matrix halted, partial results kept")
                        break
                try:
                    rec = modes.run_once(t, m, args.variant, args.opencode_bin,
                                         paid_ok=args.paid_ok, catalog_snapshot=catalog)
                except modes.Refused as exc:
                    print(f"REFUSED: {exc}")
                    partial_fh.close()
                    return 2
                rec["rep"] = rep
                ctx = rec.get("fixture_ctx", {}) or {}
                ok, v_ok, f_ok, note = grade_row(t, rec["output"], rec.get("raw_text", ""),
                                                 rec.get("files", {}), ctx)
                rec.update({"ok": ok, "value_ok": v_ok, "format_ok": f_ok,
                            "note": note, "first_pass_ok": ok, "attempt": 0})
                # C-mode repair loop: grader notes only, bounded. Each repair is
                # judged on the VISIBLE subset first; the FULL hidden set
                # decides acceptance, so hardcoding the visible test fails.
                # A repair that passes visible but fails hidden gets an
                # anti-hardcode note instead of the raw want-values.
                attempt = 0
                vis = repair_visible_task(t)
                cur_value, cur_note = rec.get("value_ok"), rec["note"]
                while m == "C" and not rec["ok"] and attempt < args.max_repairs:
                    attempt += 1
                    ratt = repair_attempt(args, t, m, repair_note(t, cur_value, cur_note))
                    okvis, _, _, notevis = grade_row(vis, ratt["normalized"], ratt["raw"],
                                                      ratt["files"], ratt["ctx"])
                    ok2, v2, f2, full_note = grade_row(t, ratt["normalized"], ratt["raw"],
                                                       ratt["files"], ratt["ctx"])
                    if okvis and not ok2:
                        # Recorded in full for the audit trail, but the NEXT
                        # repair gets NO hidden want-values (else it can
                        # hardcode them, as observed with C01 on 2026-10-09).
                        note2 = ("VISIBLE_PASS_HIDDEN_FAIL: visible checks pass but hidden "
                                 f"checks fail ({full_note})")
                        next_note = ("VISIBLE_PASS_HIDDEN_FAIL: visible checks pass but hidden "
                                     "checks fail — generalize the fix, do not hardcode "
                                     "answers to the shown examples.")
                    else:
                        note2 = notevis if not okvis else full_note
                        next_note = note2
                    rec[f"repair{attempt}_value_ok"] = v2
                    rec[f"repair{attempt}_format_ok"] = f2
                    rec[f"repair{attempt}_note"] = note2
                    rec[f"repair{attempt}_wall_s"] = ratt["wall"]
                    rec[f"repair{attempt}_tool_uses"] = ratt["tool_uses"]
                    rec[f"repair{attempt}_raw"] = ratt["raw"][:2000]
                    rec[f"repair{attempt}_output"] = ratt["normalized"][:2000]
                    if ok2:
                        rec.update({"output": ratt["normalized"], "ok": True,
                                    "value_ok": v2, "format_ok": f2,
                                    "note": f"recovered on repair {attempt}",
                                    "attempt": attempt})
                    else:
                        cur_value, cur_note = v2, next_note
                rec["recovered"] = bool(not rec["first_pass_ok"] and rec["ok"])
                rows.append(rec)
                workdir = rec.pop("workdir", None)
                if workdir:
                    shutil.rmtree(workdir, ignore_errors=True)
                partial_fh.write(json.dumps(rec, ensure_ascii=False) + "\n")
                partial_fh.flush()
                status = "PASS" if rec["ok"] else "FAIL"
                print(f"[{status}] {t['id']} mode={m} rep={rep} "
                      f"first={rec['first_pass_ok']} value={rec['value_ok']} "
                      f"format={rec['format_ok']} wall={rec.get('wall_s')}s "
                      f"tokens={rec.get('token_status')} note={rec.get('note')}", flush=True)
    except KeyboardInterrupt:
        abort_reason = abort_reason or "ABORTED by operator (KeyboardInterrupt)"
        print(abort_reason + "; partial results kept")
    except Exception as exc:  # noqa: BLE001 - finalize partial artifact, never lose rows
        abort_reason = abort_reason or f"HARNESS ERROR: {exc.__class__.__name__}: {exc}"
        print(abort_reason + "; partial results kept")
    finally:
        try:
            partial_fh.close()
        except Exception:  # noqa: BLE001
            pass

    stats_after = stats_snapshot(args.opencode_bin)
    artifact = {
        "benchmark": battery,
        "harness": modes.HARNESS_VERSION,
        "battery_version": f"{args.tasks_file} {bver}",
        "executed_utc": stamp,
        "status": "complete" if not abort_reason else f"partial: {abort_reason}",
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
                                        "ok", "value_ok", "format_ok", "first_pass_ok",
                                        "recovered", "wall_s", "tool_uses", "token_status",
                                        "needed_normalization", "note"])
    w.writeheader()
    for r in rows:
        w.writerow({k: r.get(k) for k in w.fieldnames})
    (RUNS / f"matrix_{stamp}.csv").write_text(buf.getvalue(), encoding="utf-8")
    n_pass = sum(1 for r in rows if r["ok"])
    print(f"matrix done: {n_pass}/{len(rows)} passed -> runs/matrix_{stamp}.json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
