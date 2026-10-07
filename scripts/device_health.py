#!/usr/bin/env python3
"""device_health.py — READY / DEGRADED / NOT_READY with reasons.

Checks: permissions, sandbox, browser profile, GUI, monitor, cron, MCP config,
storage/state, audit chain, dependencies. Any check may be skipped via --only.
Usage: device_health.py [--json] | selftest
"""
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
PROJ = HERE.parent
sys.path.insert(0, str(HERE))
checks = {}


def check(name, fn):
    try:
        ok, detail = fn()
    except Exception as e:
        ok, detail = False, f"{type(e).__name__}: {e}"
    checks[name] = {"ok": bool(ok), "detail": detail}


def has(cmd):
    return shutil.which(cmd) is not None


def c_permissions():
    from device_permissions import load_policy
    pol, err = load_policy()
    return (pol is not None, err or f"{len(pol['rules'])} rules")


def c_sandbox():
    if not has("bwrap"):
        return False, "bwrap missing"
    r = subprocess.run(["bwrap", "--ro-bind", "/usr", "/usr",
                        "--ro-bind", "/lib", "/lib", "--ro-bind", "/lib64", "/lib64",
                        "--ro-bind", "/etc/ld.so.cache", "/etc/ld.so.cache",
                        "--tmpfs", "/tmp", "--proc", "/proc", "--dev", "/dev",
                        "--unshare-net", "--die-with-parent",
                        "--bind", "/tmp", "/tmp", "--chdir", "/tmp", "--",
                        "/usr/bin/echo", "ok"],
                       capture_output=True, text=True, timeout=30)
    return (r.returncode == 0, "ns+netns trial")


def c_browser():
    p = PROJ / "memory/.sessions/playwright_persistent"
    ok = (p / "Default" / "Cookies").exists()
    return ok, "persistent profile+cookies" if ok else "no persistent profile"


def c_gui():
    if not has("wmctrl") or not has("gnome-screenshot"):
        return False, "wmctrl/screenshot missing"
    env = dict(os.environ, DISPLAY=os.environ.get("DISPLAY", ":0"))
    r = subprocess.run(["wmctrl", "-l"], capture_output=True, text=True,
                       timeout=10, env=env)
    wins = [l for l in r.stdout.splitlines() if l.strip()]
    if r.returncode != 0 or not wins:
        return False, "no X11 windows"
    return True, f"{len(wins)} windows on DISPLAY"


def c_monitor():
    from device_monitor import _live
    _live()
    return True, "module+state ok"


def c_cron():
    from device_cron import load
    load()
    return True, "state ok"


def c_mcp():
    try:
        cfg = json.loads((PROJ / "opencode.jsonc").read_text())
        en = [k for k, v in cfg.get("mcp", {}).items() if v.get("enabled")]
        return (len(en) > 0, f"enabled: {','.join(en)}")
    except Exception as e:
        return False, str(e)[:100]


def c_storage():
    t = Path("/tmp/opencode-device/health.probe")
    t.parent.mkdir(parents=True, exist_ok=True)
    t.write_text("ok")
    ok = t.read_text() == "ok"
    t.unlink()
    return ok, "/tmp/opencode-device writable"


def c_audit():
    r = subprocess.run([sys.executable, str(HERE / "device_audit.py"), "verify"],
                       capture_output=True, text=True, timeout=30)
    return r.returncode == 0, r.stdout.strip()[:80]


def c_deps():
    missing = [c for c in ["bwrap", "wmctrl", "xdotool", "gnome-screenshot", "git"]
               if not has(c)]
    return (not missing, "all present" if not missing else f"missing: {missing}")


def main(argv):
    check("permissions", c_permissions)
    check("sandbox", c_sandbox)
    check("browser", c_browser)
    check("gui", c_gui)
    check("monitor", c_monitor)
    check("cron", c_cron)
    check("mcp", c_mcp)
    check("storage", c_storage)
    check("audit", c_audit)
    check("deps", c_deps)
    bad = [k for k, v in checks.items() if not v["ok"]]
    critical = {"permissions", "sandbox", "storage", "audit"}
    if not bad:
        status = "READY"
    elif bad and not (set(bad) & critical):
        status = "DEGRADED"
    else:
        status = "NOT_READY"
    out = {"status": status, "checks": checks}
    if "--json" in argv or (len(argv) == 2 and argv[1] == "selftest"):
        print(json.dumps(out, indent=1))
    else:
        print(f"STATUS: {status}")
        for k, v in checks.items():
            print(f"  {'ok ' if v['ok'] else 'FAIL'} {k}: {v['detail']}")
    if len(argv) == 2 and argv[1] == "selftest":
        ok = status in ("READY", "DEGRADED")
        print("SELFTEST " + ("OK" if ok else "FAILED"))
        return 0 if ok else 1
    return 0 if status == "READY" else (1 if status == "NOT_READY" else 2)


if __name__ == "__main__":
    sys.exit(main(sys.argv))
