#!/usr/bin/env python3
"""device_latency.py — real per-operation latency benchmark (no single timing).

Measures, over many samples: permission-check, state persistence (write+read),
audit log+verify, sandbox startup, and one browser open+fill+screenshot against
the isolated tbw fixture app. Writes /tmp/opencode-device/latency_report.json.
Thresholds are DERIVED from the observed baseline (printed as guidance), never
chosen to force PASS.
"""
import json
import os
import statistics
import sys
import tempfile
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(HERE / "scripts"))
sys.path.insert(0, str(HERE / "benchmarks"))
sys.path.insert(0, str(HERE / "tests" / "e2e"))
from bench_common import summarize  # noqa: E402

OUT = Path("/tmp/opencode-device/latency_report.json")
N = 50


def main():
    tmp = Path(tempfile.mkdtemp(prefix="bench-lat-"))
    os.environ["DEVICE_STATE_ROOT"] = str(tmp / "state")
    import device_state as ds
    from device_permissions import evaluate
    from device_audit import cmd_log, cmd_verify
    from device_sandbox import run as sbrun

    rep = {"time": time.strftime("%Y-%m-%dT%H:%M:%S"), "samples_per_op": N,
           "ops": {}}

    t = []
    for _ in range(N):
        s = time.perf_counter()
        evaluate("Bash", "git status")
        t.append((time.perf_counter() - s) * 1000)
    rep["ops"]["permission_check_ms"] = summarize(t)

    t = []
    for i in range(N):
        obj = {"i": i, "pad": "x" * 500}
        s = time.perf_counter()
        ds.write("lat.json", obj)
        t.append((time.perf_counter() - s) * 1000)
    rep["ops"]["state_persist_write_ms"] = summarize(t)

    t = []
    for _ in range(N):
        s = time.perf_counter()
        ds.read("lat.json")
        t.append((time.perf_counter() - s) * 1000)
    rep["ops"]["state_persist_read_ms"] = summarize(t)

    t = []
    for i in range(N):
        s = time.perf_counter()
        cmd_log("bench", "loop", "exec", "Bash", "ALLOW", f"git status {i}")
        t.append((time.perf_counter() - s) * 1000)
    rep["ops"]["audit_log_ms"] = summarize(t)

    s = time.perf_counter()
    rc = cmd_verify()
    verify_ms = (time.perf_counter() - s) * 1000
    rep["ops"]["audit_verify_ms"] = {"single_run_ms": round(verify_ms, 2),
                                     "rc": rc}

    t = []
    work = tmp / "work"
    work.mkdir()
    for _ in range(max(5, N // 10)):
        s = time.perf_counter()
        rc = sbrun(["/usr/bin/echo", "hi"], workdir=str(work), timeout=30)
        assert rc == 0
        t.append((time.perf_counter() - s) * 1000)
    rep["ops"]["sandbox_startup_ms"] = summarize(t)

    # browser op + screenshot against the isolated fixture app
    try:
        from playwright.sync_api import sync_playwright
        from tbw_app import start_server
        srv, base = start_server()
        try:
            with sync_playwright() as pw:
                ctx = pw.chromium.launch_persistent_context(
                    str(tmp / "prof"), headless=True,
                    args=["--no-sandbox", "--disable-dev-shm-usage"])
                pg = ctx.new_page()
                s = time.perf_counter()
                pg.goto(base + "/")
                pg.fill("#u", "test")
                pg.fill("#p", "test")
                pg.click("#go")
                pg.wait_for_load_state("domcontentloaded")
                goto_ms = (time.perf_counter() - s) * 1000
                s = time.perf_counter()
                pg.goto(base + "/")
                pg.fill("#name", "bench")
                fill_ms = (time.perf_counter() - s) * 1000
                s = time.perf_counter()
                shot = tmp / "shot.png"
                pg.screenshot(path=str(shot))
                shot_ms = (time.perf_counter() - s) * 1000
                rep["ops"]["browser_goto_login_ms"] = {"single_run_ms":
                                                       round(goto_ms, 1)}
                rep["ops"]["browser_fill_ms"] = {"single_run_ms":
                                                 round(fill_ms, 1)}
                rep["ops"]["gui_screenshot_ms"] = {"single_run_ms":
                                                   round(shot_ms, 1),
                                                   "bytes": shot.stat().st_size}
                ctx.close()
        finally:
            srv.shutdown()
    except Exception as e:
        rep["ops"]["browser_error"] = str(e)[:200]

    # derived guidance (observed, not enforced)
    p95perm = rep["ops"]["permission_check_ms"]["p95"]
    p95w = rep["ops"]["state_persist_write_ms"]["p95"]
    rep["observed_baseline_guidance"] = {
        "permission_p95_ms": p95perm,
        "state_write_p95_ms": p95w,
        "suggested_thresholds": {
            "permission_p95_ms": round(p95perm * 5, 1),
            "state_write_p95_ms": round(p95w * 5, 1),
        },
        "note": "thresholds = 5x observed p95 on this box; "
                "informational, not gates",
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(rep, indent=1))
    print(f"wrote {OUT}")
    for k, v in rep["ops"].items():
        if isinstance(v, dict) and "p50" in v:
            print(f"{k}: p50={v['p50']} p95={v['p95']} p99={v['p99']} "
                  f"min={v['min']} max={v['max']}")
        else:
            print(f"{k}: {v}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
