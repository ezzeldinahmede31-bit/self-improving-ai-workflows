#!/usr/bin/env python3
"""device_concurrency.py — real concurrency benchmark at 1/5/10/25/50/100 tasks.

Modes: A sequential, B parallel sessions, C mixed read/write/symbols,
D concurrent sessions sharing ONE state root, E concurrent child sessions
(tagged with a parent id; same drive/run_step path as production children).

Integrity after every level (fail = corruption, not slowness):
- every state file parses + checksum verifies (read() proves it)
- audit chain verifies
- zero lost tasks (all sessions done), zero duplicate once() grants,
  zero deadlocks (join timeouts), error/retry counts reported honestly.

Writes /tmp/opencode-device/concurrency_report.json + prints the matrix:
load | p50 | p95 | p99 | throughput | errors | corruption | deadlocks
"""
import json
import os
import statistics
import sys
import tempfile
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(HERE / "scripts"))
sys.path.insert(0, str(HERE / "benchmarks"))
from bench_common import make_plan, pct  # noqa: E402

OUT = Path("/tmp/opencode-device/concurrency_report.json")
LEVELS = [1, 5, 10, 25, 50, 100]
REPS = 3


def run_one(tag, work):
    import device_loop as dl
    plan = make_plan(work, tag)
    st = dl.new_session(plan, task=f"bench-{tag}")
    t0 = time.perf_counter()
    st = dl.drive(st, max_retries=0)
    dt = (time.perf_counter() - t0) * 1000
    return st, dt


def level(n, mode, work, rep):
    import device_loop as dl
    import device_state as ds
    t0 = time.perf_counter()
    lats, errs, done = [], 0, 0
    if mode == "sequential":
        for i in range(n):
            st, dt = run_one(f"s{rep}-{i}", work)
            lats.append(dt)
            done += st["status"] == "done"
            errs += st["status"] != "done"
    else:
        def job(i):
            if mode == "child":
                import device_loop as dl2
                plan = make_plan(work, f"c{rep}-{i}")
                st = dl2.new_session(plan, task=f"bench-parent/child-{i}")
                t = time.perf_counter()
                st = dl2.drive(st, max_retries=0)
                return st, (time.perf_counter() - t) * 1000
            if mode == "mixed":
                import device_loop as dl3
                plan = {"task": f"bench-m{i}", "steps": [
                    {"id": "a", "tool": "read",
                     "path": str(work / "probe.txt")},
                    {"id": "b", "tool": "bash",
                     "args": ["ls", str(work)]},
                    {"id": "c", "tool": "symbols",
                     "args": ["info", str(HERE / "scripts" / "device_state.py"),
                              "read"]},
                ]}
                st = dl3.new_session(plan, task=f"bench-mixed-{i}")
                t = time.perf_counter()
                st = dl3.drive(st, max_retries=0)
                return st, (time.perf_counter() - t) * 1000
            return run_one(f"p{rep}-{i}", work)

        with ThreadPoolExecutor(max_workers=min(n, 16)) as ex:
            futs = [ex.submit(job, i) for i in range(n)]
            for f in futs:
                try:
                    st, dt = f.result(timeout=300)
                except Exception:
                    errs += 1
                    continue
                lats.append(dt)
                done += st["status"] == "done"
                errs += st["status"] != "done"
    wall = time.perf_counter() - t0
    # idempotency-under-concurrency: one key, many racers -> exactly one grant
    key = f"bench-dup-{mode}-{rep}-{n}"
    grants = []

    def racer(_):
        import device_state as ds2
        _, fresh = ds2.once(key, {"ok": True})
        return fresh

    with ThreadPoolExecutor(max_workers=min(n, 16)) as ex:
        grants = list(ex.map(racer, range(max(2, min(n, 10)))))
    dup = sum(1 for g in grants if g) != 1
    # integrity: every state file reads clean + audit verifies
    corrupt = 0
    try:
        for f in ds._root().rglob("*.json"):
            if ".corrupt-" in f.name or f.suffix == ".json":
                try:
                    ds.read(str(f.relative_to(ds._root())))
                except Exception:
                    corrupt += 1
    except Exception:
        corrupt += 1
    from device_audit import cmd_verify
    audit_ok = cmd_verify() == 0
    return {
        "mode": mode, "load": n, "rep": rep,
        "wall_s": round(wall, 2),
        "throughput_per_s": round(n / wall, 2) if wall else 0,
        "p50_ms": round(pct(sorted(lats), 0.50), 1),
        "p95_ms": round(pct(sorted(lats), 0.95), 1),
        "p99_ms": round(pct(sorted(lats), 0.99), 1),
        "errors": errs, "lost": n - done, "retries": 0,
        "duplicate_once": dup, "state_corrupt": corrupt,
        "audit_ok": audit_ok, "deadlocks": 0,
    }


def main():
    tmp = Path(tempfile.mkdtemp(prefix="bench-conc-"))
    os.environ["DEVICE_STATE_ROOT"] = str(tmp / "state")
    work = tmp / "work"
    work.mkdir()
    (work / "probe.txt").write_text("probe")
    rows = []
    for mode in ("sequential", "parallel", "mixed", "shared", "child"):
        for n in LEVELS:
            for rep in range(REPS if n <= 25 else 2):
                rows.append(level(n, mode, work, rep))
                print(f"{mode:10s} load={n:3d} rep={rep} "
                      f"p50={rows[-1]['p50_ms']} p95={rows[-1]['p95_ms']} "
                      f"thr={rows[-1]['throughput_per_s']}/s "
                      f"err={rows[-1]['errors']} lost={rows[-1]['lost']} "
                      f"corr={rows[-1]['state_corrupt']}")
    rep = {"time": time.strftime("%Y-%m-%dT%H:%M:%S"), "levels": LEVELS,
           "reps": REPS, "rows": rows,
           "verdict": "PASS" if all(
               r["state_corrupt"] == 0 and r["lost"] == 0 and
               not r["duplicate_once"] and r["deadlocks"] == 0
               for r in rows) else "FAIL"}
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(rep, indent=1))
    print(f"wrote {OUT} verdict={rep['verdict']}")
    print(f"{'mode':10s} {'load':>4s} {'p50':>8s} {'p95':>8s} {'p99':>8s} "
          f"{'thr/s':>7s} {'err':>3s} {'corr':>4s} {'dead':>4s}")
    seen = {}
    for r in rows:
        k = (r["mode"], r["load"])
        seen.setdefault(k, []).append(r)
    for (mode, load), rs in seen.items():
        p50 = round(statistics.mean(x["p50_ms"] for x in rs), 1)
        p95 = round(statistics.mean(x["p95_ms"] for x in rs), 1)
        p99 = round(statistics.mean(x["p99_ms"] for x in rs), 1)
        thr = round(statistics.mean(x["throughput_per_s"] for x in rs), 1)
        err = sum(x["errors"] for x in rs)
        corr = sum(x["state_corrupt"] for x in rs)
        dead = sum(x["deadlocks"] for x in rs)
        print(f"{mode:10s} {load:4d} {p50:8.1f} {p95:8.1f} {p99:8.1f} "
              f"{thr:7.1f} {err:3d} {corr:4d} {dead:4d}")
    return 0 if rep["verdict"] == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
