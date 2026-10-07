"""Device platform regression gate: every device module's selftest +
redteam + health must exit 0. Full T1-T25 E2E runs separately
(scripts/device_e2e.py) and is linked from docs/COWORK_PARITY.md.
"""
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
PY = ROOT / "venv" / "bin" / "python"

MODULES = [
    "device_permissions", "device_sandbox", "device_monitor", "device_cron",
    "device_loop", "device_audit", "device_state", "device_symbols",
    "device_health",
]


def run(mod, *args):
    return subprocess.run(
        [str(PY), str(ROOT / "scripts" / f"{mod}.py"), *args],
        capture_output=True, text=True, timeout=300, cwd=str(ROOT))


def test_module_selftests():
    for mod in MODULES:
        r = run(mod, "selftest")
        assert r.returncode == 0, f"{mod} selftest failed:\n{r.stdout[-1500:]}\n{r.stderr[-500:]}"


def test_redteam():
    r = run("device_redteam")
    assert r.returncode == 0, f"redteam failed:\n{r.stdout[-2000:]}"
    assert "REDTEAM: PASS (10/10)" in r.stdout


def test_e2e_report_green():
    import json
    rep = json.loads(Path("/tmp/opencode-device/e2e_report.json").read_text())
    assert rep["verdict"] == "COWORK_GRADE", rep
    assert rep["failed"] == 0, rep
