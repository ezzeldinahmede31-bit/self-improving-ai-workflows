"""test_device_state_durable.py — P0-A/P0-B proof: durable state + backup/restore.

All tests run against an ISOLATED DEVICE_STATE_ROOT under tmp_path (never the
real persistent dir, never /tmp/opencode-device, never production creds).
"""
import hashlib
import json
import os
import stat
import subprocess
import sys
import time
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent.parent
SCRIPTS = HERE / "scripts"
sys.path.insert(0, str(SCRIPTS))

PY = sys.executable


@pytest.fixture()
def sroot(tmp_path, monkeypatch):
    root = tmp_path / "dstate"
    monkeypatch.setenv("DEVICE_STATE_ROOT", str(root))
    # force reimport so resolve_root() picks up the env
    for mod in [m for m in list(sys.modules) if m == "device_state"]:
        del sys.modules[mod]
    import device_state as ds
    return root, ds


def _perms(p):
    return stat.S_IMODE(p.stat().st_mode)


def test_state_survives_process_restart(sroot):
    root, ds = sroot
    # process A: write then die
    r = subprocess.run(
        [PY, "-c",
         "import sys; sys.path.insert(0, 'scripts');"
         "from device_state import write; write('sess.json', {'step': 7})"],
        capture_output=True, text=True, cwd=str(HERE),
        env={**os.environ})
    assert r.returncode == 0, r.stderr
    # process B: fresh interpreter loads and continues
    r2 = subprocess.run(
        [PY, "-c",
         "import sys; sys.path.insert(0, 'scripts');"
         "from device_state import read, write;"
         "d = read('sess.json'); assert d == {'step': 7}, d;"
         "write('sess.json', {'step': 8})"],
        capture_output=True, text=True, cwd=str(HERE),
        env={**os.environ})
    assert r2.returncode == 0, r2.stderr
    assert ds.read("sess.json") == {"step": 8}


def test_state_survives_simulated_reboot(sroot):
    root, ds = sroot
    ds.write("cron/tasks.json", {"jobs": ["a", "b"]})
    ds.once("op-1", {"done": True})
    # simulated reboot: drop the module (in-memory caches), keep only disk
    for mod in [m for m in list(sys.modules) if m == "device_state"]:
        del sys.modules[mod]
    env = {k: v for k, v in os.environ.items()
           if k not in ("PYTHONINSPECT",)}
    r = subprocess.run(
        [PY, "-c",
         "import sys; sys.path.insert(0, 'scripts');"
         "from device_state import read, peek;"
         "assert read('cron/tasks.json') == {'jobs': ['a', 'b']};"
         "assert peek('op-1') == {'done': True};"
         "print('RESUMED')"],
        capture_output=True, text=True, cwd=str(HERE), env=env)
    assert r.returncode == 0, r.stderr
    assert "RESUMED" in r.stdout


def test_atomic_state_write_under_concurrency(sroot):
    root, ds = sroot
    n = 8
    procs = [
        subprocess.Popen(
            [PY, "-c",
             "import sys; sys.path.insert(0, 'scripts');"
             f"from device_state import write; write('c{i}.json', "
             f"{{'i': {i}, 'pad': 'x' * 2000}} )"],
            cwd=str(HERE), env={**os.environ})
        for i in range(n)
    ]
    for p in procs:
        assert p.wait(timeout=120) == 0
    # every file parses, checksum sidecars verify on read
    for i in range(n):
        assert ds.read(f"c{i}.json")["i"] == i
    # hammer the SAME file from many processes: last-writer-wins, never torn
    procs = [
        subprocess.Popen(
            [PY, "-c",
             "import sys; sys.path.insert(0, 'scripts');"
             f"from device_state import write; write('shared.json', "
             f"{{'w': {i}}})"],
            cwd=str(HERE), env={**os.environ})
        for i in range(n)
    ]
    for p in procs:
        assert p.wait(timeout=120) == 0
    v = ds.read("shared.json")
    assert isinstance(v["w"], int) and 0 <= v["w"] < n
    raw = (root / "shared.json").read_bytes()
    json.loads(raw.decode())  # parses -> not torn


def test_corrupted_state_fails_closed(sroot):
    root, ds = sroot
    ds.write("sess.json", {"step": 1})
    p = root / "sess.json"
    # flip bytes on disk (keep checksum stale -> mismatch path)
    raw = bytearray(p.read_bytes())
    raw[10] ^= 0xFF
    p.write_bytes(bytes(raw))
    with pytest.raises(RuntimeError):
        ds.read("sess.json")
    # quarantined, never silently loaded
    assert not p.exists()
    assert len(list(root.glob("sess.json.corrupt-*"))) == 1
    # byte-valid JSON but schema-violating envelope also fails closed
    ds.write("sess2.json", {"a": 1})
    p2 = root / "sess2.json"
    env = json.loads(p2.read_text())
    env["_schema"] = 9999  # future major
    p2.write_text(json.dumps(env))
    (root / "sess2.json.sha256").write_text(
        hashlib.sha256(p2.read_bytes()).hexdigest() + "\n")
    with pytest.raises(RuntimeError):
        ds.read("sess2.json")


def test_state_permissions(sroot):
    root, ds = sroot
    ds.write("a/b.json", {"x": 1})
    assert _perms(root) == 0o700
    assert _perms(root / "a" / "b.json") == 0o600
    assert _perms(root / "a" / "b.json.sha256") == 0o600
    ok, problems = ds.verify_permissions()
    assert ok, problems
    # default production root (no override) must not be under /tmp
    import os as _os
    saved = _os.environ.pop("DEVICE_STATE_ROOT", None)
    try:
        for mod in [m for m in list(sys.modules) if m == "device_state"]:
            del sys.modules[mod]
        import device_state as _ds2
        assert str(_ds2.resolve_root()) != "/tmp/opencode-device/state"
        assert not str(_ds2.resolve_root()).startswith("/tmp/")
    finally:
        if saved is not None:
            _os.environ["DEVICE_STATE_ROOT"] = saved


def test_backup_restore_roundtrip(sroot):
    root, ds = sroot
    ds.write("sess.json", {"step": 3})
    ds.once("op-9", {"done": True})
    dest = ds.backup_state(label="t")
    assert (dest / "manifest.json").exists()
    ok, problems = ds.verify_backup(dest)
    assert ok, problems
    # destroy test state
    (root / "sess.json").unlink()
    (root / "idempotency.json").unlink(missing_ok=True)
    assert ds.read("sess.json") is None
    # restore + verify + resume
    ds.restore_state(dest)
    assert ds.read("sess.json") == {"step": 3}
    assert ds.peek("op-9") == {"done": True}
    ok2, _ = ds.verify_permissions()
    assert ok2


def test_backup_corruption_detection(sroot):
    root, ds = sroot
    ds.write("sess.json", {"step": 1})
    dest = ds.backup_state()
    # tamper with a backup payload byte
    bf = dest / "sess.json"
    raw = bytearray(bf.read_bytes())
    raw[12] ^= 0xFF
    bf.write_bytes(bytes(raw))
    ok, problems = ds.verify_backup(dest)
    assert not ok and problems
    with pytest.raises(RuntimeError):
        ds.restore_state(dest)
    # live state untouched by refused restore
    assert ds.read("sess.json") == {"step": 1}


def test_restore_is_atomic(sroot):
    root, ds = sroot
    ds.write("keep.json", {"v": "original"})
    ds.write("sess.json", {"step": 1})
    good = ds.backup_state(label="good")
    # craft a candidate backup dir with one invalid member but valid manifest sig:
    # simplest honest path: corrupt the copy, verify must fail, restore refused
    import shutil
    cand = Path(str(good) + "-evilcopy")
    shutil.copytree(good, cand)
    (cand / "sess.json").write_bytes(b"{not json")
    ok, _ = ds.verify_backup(cand)
    assert not ok
    with pytest.raises(RuntimeError):
        ds.restore_state(cand)
    assert ds.read("keep.json") == {"v": "original"}
    assert ds.read("sess.json") == {"step": 1}


def test_backup_contains_no_raw_secrets(sroot):
    root, ds = sroot
    ds.write("sess.json", {
        "api_key": "sk-abcdefgh12345678",
        "nested": {"password": "hunter2-secret"},
        "note": "plain text",
    })
    dest = ds.backup_state()
    blob = "\n".join(
        f.read_text() for f in dest.rglob("*.json"))
    assert "sk-abcdefgh12345678" not in blob
    assert "hunter2-secret" not in blob
    assert "plain text" in blob  # non-secrets survive
    ok, problems = ds.verify_backup(dest)
    assert ok, problems


def test_concurrent_once_grants_exactly_once(sroot):
    """N racers, one key: exactly one fresh=True (no duplicate execution)."""
    import threading
    root, ds = sroot
    results = []
    barrier = threading.Barrier(10)

    def racer(i):
        barrier.wait(timeout=30)
        _, fresh = ds.once("race-key", {"by": i})
        results.append(fresh)

    ts = [threading.Thread(target=racer, args=(i,)) for i in range(10)]
    for t in ts:
        t.start()
    for t in ts:
        t.join(timeout=60)
    assert len(results) == 10
    assert sum(1 for f in results if f) == 1
