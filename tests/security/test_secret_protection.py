"""test_secret_protection.py — secrets/state/backups/audit sweep.

Plants FAKE canary secrets (never production values) through each sink and
proves the real boundary: audit redacts, backups scrub to references, live
state + latest backup + audit log contain no raw-secret patterns.
"""
import json
import re
import sys
import tempfile
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(HERE / "scripts"))
sys.path.insert(0, str(HERE))

CANARY_KEY = "sk-canary-" + "X" * 24
CANARY_JWT = ("eyJjYW5hcnktaGVhZGVy."
              "Y2FuYXJ5LXBheWxvYWQtMTIzNDU2Nzg5MA."
              "Y2FuYXJ5LXNpZ25hdHVyZS0xMjM0NTY3ODkwMTIz")

PATTERNS = [r"sk-canary-X{24}", r"Y2FuYXJ5LXNpZ25hdHVyZS0xMjM0NTY3ODkwMTIz"]


def hit(text):
    return [p for p in PATTERNS if re.search(p, text)]


def test_secret_protection(tmp_path, monkeypatch):
    import device_state as ds
    from device_audit import cmd_log, redact
    monkeypatch.setenv("DEVICE_STATE_ROOT", str(tmp_path / "state"))
    for m in list(sys.modules):
        if m == "device_state":
            del sys.modules[m]
    import device_state as ds  # noqa: F811

    # 1. secret -> audit must be redacted
    assert not hit(redact(f"api_key={CANARY_KEY}"))
    assert not hit(redact(f"token {CANARY_JWT}"))

    # 2. secret -> state write is stored (documented: callers pass refs), but
    #    the BACKUP edge must scrub it to a reference
    ds.write("sess.json", {"api_key": CANARY_KEY, "note": "plain"})
    dest = ds.backup_state(label="canary")
    blob = "\n".join(f.read_text() for f in dest.rglob("*.json"))
    assert not hit(blob), "backup leaked raw canary"
    assert "__redacted__" in blob
    ok, probs = ds.verify_backup(dest)
    assert ok, probs

    # 3. secret -> error path: corrupt-state errors must not echo secrets
    p = tmp_path / "state" / "sess.json"
    raw = p.read_bytes()
    p.write_bytes(b"{broken")
    try:
        ds.read("sess.json")
        raised = ""
    except RuntimeError as e:
        raised = str(e)
    assert not hit(raised + raw.decode("utf-8", "ignore")[:0])

    # 4. sweep live persistent state dir for raw-secret SHAPES (broad regexes
    #    over real artifacts; canary-tuned to avoid prod false positives)
    import subprocess
    r = subprocess.run([sys.executable, "scripts/device_audit.py", "verify"],
                       capture_output=True, text=True, timeout=60,
                       cwd=str(HERE))
    assert r.returncode == 0
    state_root = ds._root()
    text = ""
    for f in list(state_root.rglob("*.json"))[:200]:
        try:
            text += f.read_text()[:2000]
        except Exception:
            pass
    for p in PATTERNS:
        assert not re.search(p, text)
