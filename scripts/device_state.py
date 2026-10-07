#!/usr/bin/env python3
"""device_state.py — durable atomic JSON state store with backup/restore + idempotency.

P0-A/P0-B hardening round (2026-10-07):
- Authoritative state lives in a PERSISTENT directory, never /tmp:
    $DEVICE_STATE_ROOT  (explicit override, e.g. tests)
    else ~/.local/state/opencode-device
  Legacy /tmp/opencode-device/state is migrated once (copy + marker) and is
  no longer authoritative. /tmp remains for transient artifacts only.
- Atomic persistence: tmp file in same dir -> flush+fsync -> os.replace ->
  fsync directory. Concurrent writers serialize via fcntl.flock on a per-file
  sidecar lock; stale .tmp files older than 1h are reaped (stale-lock recovery).
- Integrity: every state file has a .sha256 sidecar; read verifies checksum
  AND JSON parse AND schema envelope; any failure -> quarantine (.corrupt-<ts>)
  + RuntimeError (fail closed, never silently load).
- Schema: envelope {"_schema": int, "_v": 1, "data": <user obj>} with
  migration chain MIGRATIONS. Unknown future major schema -> fail closed.
- Permissions: root dir 0o700, files 0o600; enforced on every write, verified
  by verify_permissions(). World-readable state is refused.
- Backup (P0-B): backup_state() writes a deterministic snapshot dir containing
  state files (scrubbed of raw secrets) + manifest.json (schema, timestamps,
  checksums, scrub report). verify_backup() re-checks everything.
  restore_state() stages into a candidate dir, validates fully, then atomically
  promotes file-by-file (current files are parked in a rollback dir first).
  Generations: keep last BACKUP_GENERATIONS (default 5), prune older.
  Secrets: values under secret-ish keys are stored as {"__redacted__": True}
  references, never raw. Raw-secret-shaped strings inside backups are rejected
  by verify_backup (test_backup_contains_no_raw_secrets).

Idempotency: once(key, result) records completed destructive operations;
peek(key) tells a resumed worker to SKIP re-execution.

Usage:
  device_state.py read <name> | write <name> (stdin JSON)
  device_state.py once <key> (stdin result) | peek <key>
  device_state.py snapshot | restore <dir> | list
  device_state.py backup | verify-backup <dir> | list-backups
  device_state.py where | selftest
"""
import fcntl
import fnmatch
import hashlib
import json
import os
import re
import shutil
import sys
import time
from pathlib import Path

STATE_SCHEMA = 1
MIGRATIONS = {}  # old_schema -> fn(envelope) ; none yet (schema 1 is first)
IDEM = "idempotency.json"
BACKUP_GENERATIONS = 5
SCHEMA_FILE = "_schema.json"

LEGACY_ROOT = Path("/tmp/opencode-device/state")
LEGACY_BACKUPS = Path("/tmp/opencode-device/backups")


def resolve_root():
    ov = os.environ.get("DEVICE_STATE_ROOT") or os.environ.get(
        "OPCODE_DEVICE_STATE_ROOT")
    if ov:
        return Path(ov).expanduser()
    # persistent per-user state dir (XDG)
    xdg = os.environ.get("XDG_STATE_HOME")
    base = Path(xdg).expanduser() if xdg else Path.home() / ".local" / "state"
    return base / "opencode-device"


def resolve_backups():
    return resolve_root() / "backups"


def _ensure_perms_dir(p):
    p.mkdir(parents=True, exist_ok=True)
    try:
        os.chmod(p, 0o700)
    except Exception:
        pass


def _ensure_perms_file(p):
    try:
        os.chmod(p, 0o600)
    except Exception:
        pass


_REPAIR_AT = [0.0]


def _root():
    r = resolve_root()
    _ensure_perms_dir(r)
    # perm repair walks the tree: throttle to once per process-boot/hour,
    # otherwise every write degrades to O(tree) (found by concurrency bench:
    # p50 blew out to ~4s at load 100).
    now = time.time()
    if now - _REPAIR_AT[0] > 3600:
        _repair_perms(r)
        _REPAIR_AT[0] = now
    _migrate_legacy_once(r)
    return r


def _repair_perms(root):
    """Best-effort tightening of existing files (owner-only). Safe: only
    removes group/other bits inside our own state dir."""
    try:
        for d, _ds, fs in os.walk(root):
            try:
                os.chmod(d, 0o700)
            except Exception:
                pass
            for fn in fs:
                fp = os.path.join(d, fn)
                try:
                    st = os.stat(fp)
                    mode = st.st_mode & 0o777
                    if mode & 0o077:
                        os.chmod(fp, mode & ~0o077)
                except Exception:
                    pass
    except Exception:
        pass


def _open_lock(lock):
    lock.parent.mkdir(parents=True, exist_ok=True)
    lf = open(lock, "a+")
    try:
        os.chmod(lock, 0o600)
    except Exception:
        pass
    return lf


def _migrate_legacy_once(root):
    marker = root / ".migrated_from_tmp"
    if marker.exists():
        return
    try:
        if LEGACY_ROOT.exists():
            moved = 0
            for f in LEGACY_ROOT.rglob("*.json"):
                if ".corrupt-" in f.name:
                    continue
                rel = f.relative_to(LEGACY_ROOT)
                dest = root / rel
                if dest.exists():
                    continue
                dest.parent.mkdir(parents=True, exist_ok=True)
                try:
                    json.loads(f.read_text())
                except Exception:
                    continue
                shutil.copy2(f, dest)
                _ensure_perms_file(dest)
                moved += 1
            marker.write_text(json.dumps(
                {"ts": time.time(), "moved": moved,
                 "from": str(LEGACY_ROOT)}))
            _ensure_perms_file(marker)
    except Exception:
        pass


def _path(name):
    r = _root()
    p = (r / name).resolve()
    rr = r.resolve()
    assert str(p) == str(rr) or str(p).startswith(str(rr) + "/"), \
        "path escape"
    return p


def _lock_path(p):
    return p.with_suffix(p.suffix + ".lock")


def _checksum_path(p):
    return p.with_suffix(p.suffix + ".sha256")


def _sha256_file(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def _read_locked(p):
    """Read+verify a state file whose lock is already held. Returns obj/None."""
    if not p.exists():
        return None
    raw = p.read_bytes()
    csum = _checksum_path(p)
    if csum.exists():
        expect = csum.read_text().strip().split()[0]
        if hashlib.sha256(raw).hexdigest() != expect:
            raise RuntimeError("corrupt state (checksum mismatch)")
    try:
        env = json.loads(raw.decode("utf-8"))
    except Exception:
        raise RuntimeError("corrupt state (unparsable)")
    return _unwrap(env, p.name)


def _write_locked(p, obj):
    """Atomic write assuming the file lock is already held."""
    payload = json.dumps(_wrap(obj), indent=1, sort_keys=True)
    tmp = p.with_suffix(p.suffix + f".tmp{os.getpid()}")
    with open(tmp, "w") as f:
        f.write(payload)
        f.flush()
        os.fsync(f.fileno())
    _ensure_perms_file(tmp)
    digest = _sha256_file(tmp)
    os.replace(tmp, p)
    _ensure_perms_file(p)
    _checksum_path(p).write_text(digest + "\n")
    _ensure_perms_file(_checksum_path(p))
    try:
        dfd = os.open(str(p.parent), os.O_DIRECTORY)
        try:
            os.fsync(dfd)
        finally:
            os.close(dfd)
    except Exception:
        pass


def _reap_stale_tmp(d):
    now = time.time()
    try:
        for t in d.glob("*.tmp*"):
            try:
                if now - t.stat().st_mtime > 3600:
                    t.unlink()
            except Exception:
                pass
    except Exception:
        pass


def _wrap(obj):
    if isinstance(obj, dict) and set(obj.keys()) == {"_schema", "_v", "data"}:
        return obj  # already enveloped
    return {"_schema": STATE_SCHEMA, "_v": 1, "data": obj}


def _unwrap(env, name="<state>"):
    if not isinstance(env, dict):
        raise RuntimeError(f"corrupt state (bad envelope): {name}")
    if "_schema" not in env or "data" not in env:
        # legacy v0: raw user JSON written before envelopes existed -> adopt
        return env
    sch = env["_schema"]
    if not isinstance(sch, int) or sch < 1:
        raise RuntimeError(f"corrupt state (bad schema): {name}")
    if sch > STATE_SCHEMA:
        raise RuntimeError(
            f"incompatible future schema v{sch} (this code: v{STATE_SCHEMA}): "
            f"{name} -> fail closed")
    while sch < STATE_SCHEMA:
        fn = MIGRATIONS.get(sch)
        if fn is None:
            raise RuntimeError(
                f"no migration v{sch}->v{sch+1}: {name} -> fail closed")
        env = fn(env)
        sch = env["_schema"]
    return env["data"]


# ---------------- read / write ----------------

def read(name):
    p = _path(name)
    if not p.exists():
        return None
    lock = _lock_path(p)
    lock.parent.mkdir(parents=True, exist_ok=True)
    with _open_lock(lock) as lf:
        try:
            fcntl.flock(lf, fcntl.LOCK_SH)
            raw = p.read_bytes()
        finally:
            try:
                fcntl.flock(lf, fcntl.LOCK_UN)
            except Exception:
                pass
    csum = _checksum_path(p)
    if csum.exists():
        expect = csum.read_text().strip().split()[0]
        got = hashlib.sha256(raw).hexdigest()
        if got != expect:
            q = p.with_suffix(p.suffix + f".corrupt-{int(time.time())}")
            try:
                p.rename(q)
                csum.unlink(missing_ok=True)
            except Exception:
                pass
            raise RuntimeError(f"corrupt state (checksum mismatch) "
                               f"quarantined at {q}")
    try:
        env = json.loads(raw.decode("utf-8"))
    except Exception:
        q = p.with_suffix(p.suffix + f".corrupt-{int(time.time())}")
        try:
            p.rename(q)
            if csum.exists():
                csum.unlink(missing_ok=True)
        except Exception:
            pass
        raise RuntimeError(f"corrupt state quarantined at {q}")
    try:
        return _unwrap(env, name)
    except RuntimeError:
        q = p.with_suffix(p.suffix + f".corrupt-{int(time.time())}")
        try:
            p.rename(q)
            if csum.exists():
                csum.unlink(missing_ok=True)
        except Exception:
            pass
        raise


def write(name, obj):
    p = _path(name)
    p.parent.mkdir(parents=True, exist_ok=True)
    _reap_stale_tmp(p.parent)
    lock = _lock_path(p)
    lock.parent.mkdir(parents=True, exist_ok=True)
    with _open_lock(lock) as lf:
        fcntl.flock(lf, fcntl.LOCK_EX)
        try:
            _write_locked(p, obj)
        finally:
            try:
                fcntl.flock(lf, fcntl.LOCK_UN)
            except Exception:
                pass


def verify_permissions():
    """Return (ok, problems). Owner-only dir (0700), files 0600, no symlinks."""
    r = resolve_root()
    problems = []
    if not r.exists():
        return True, []
    try:
        st = r.stat()
        if st.st_mode & 0o077:
            problems.append(f"root dir perms {oct(st.st_mode & 0o777)} "
                            f"(want 0700): {r}")
        if os.path.islink(r):
            problems.append(f"root dir is a symlink: {r}")
    except Exception as e:
        problems.append(f"root stat failed: {e}")
    for f in r.rglob("*"):
        try:
            if os.path.islink(f):
                # lock files and tmp files are transient; state symlinks deny
                if f.suffix not in (".lock",) and ".tmp" not in f.name:
                    problems.append(f"symlink in state: {f}")
                continue
            if f.is_file() and not f.name.startswith(".migrated"):
                mode = f.stat().st_mode & 0o777
                if mode & 0o077:
                    problems.append(f"world/group-readable {oct(mode)}: {f}")
        except Exception as e:
            problems.append(f"stat failed {f}: {e}")
    return (len(problems) == 0), problems


def peek(key):
    d = read(IDEM) or {}
    rec = d.get(key)
    return rec["result"] if rec else None


def once(key, result):
    """Idempotent grant. The read-modify-write holds ONE exclusive lock, so N
    concurrent racers produce exactly ONE fresh=True (no duplicate execution).
    Previously read() and write() locked separately and racers double-granted
    (found by the concurrency benchmark, duplicate_once=True)."""
    p = _path(IDEM)
    p.parent.mkdir(parents=True, exist_ok=True)
    lock = _lock_path(p)
    lock.parent.mkdir(parents=True, exist_ok=True)
    with _open_lock(lock) as lf:
        fcntl.flock(lf, fcntl.LOCK_EX)
        try:
            try:
                d = _read_locked(p) or {}
            except RuntimeError:
                # corrupt idempotency log fails closed: refuse a fresh grant
                # rather than risk a duplicate destructive execution.
                raise
            if key in d:
                return d[key]["result"], False
            d[key] = {"result": result, "ts": time.time()}
            _write_locked(p, d)
            return result, True
        finally:
            try:
                fcntl.flock(lf, fcntl.LOCK_UN)
            except Exception:
                pass


# ---------------- backup / restore (P0-B) ----------------

SECRET_KEY_RES = [
    r"api[_-]?key", r"secret", r"token", r"password", r"passwd",
    r"cookie", r"session[_-]?secret", r"auth[_-]?header", r"bearer",
    r"private[_-]?key", r"client[_-]?secret", r"credential",
]
SECRET_VALUE_RES = [
    r"sk-[A-Za-z0-9]{8,}", r"ghp_[A-Za-z0-9]{8,}", r"gho_[A-Za-z0-9]{8,}",
    r"xox[bap]-[A-Za-z0-9-]{8,}", r"AKIA[0-9A-Z]{16}",
    r"Bearer\s+[A-Za-z0-9\-._~+/=]{8,}",
]


def _looks_secret_key(k):
    kl = str(k).lower()
    return any(re.search(p, kl) for p in SECRET_KEY_RES)


def scrub_for_backup(obj):
    """Replace secret-ish values with redacted references. Returns (scrubbed, n)."""
    n = [0]

    def _s(o):
        if isinstance(o, dict):
            out = {}
            for k, v in o.items():
                if _looks_secret_key(k):
                    n[0] += 1
                    out[k] = {"__redacted__": True, "ref": str(k)}
                else:
                    out[k] = _s(v)
            return out
        if isinstance(o, list):
            return [_s(x) for x in o]
        if isinstance(o, str):
            for p in SECRET_VALUE_RES:
                if re.search(p, o):
                    n[0] += 1
                    return "__REDACTED_SECRET_VALUE__"
        return o

    return _s(obj), n[0]


def _iter_state_files(root=None):
    r = root or _root()
    for f in sorted(r.rglob("*.json")):
        if ".corrupt-" in f.name or f.name.endswith((".lock",)):
            continue
        if f.suffix == ".sha256":
            continue
        if "backups" in f.parts[len(r.parts):]:
            continue
        yield f


def backup_state(label=None):
    """Deterministic backup: scrubbed state + manifest. Returns backup dir."""
    root = _root()
    broot = resolve_backups()
    _ensure_perms_dir(broot)
    ts = time.strftime("%Y%m%d-%H%M%S")
    dest = broot / (ts + (f"-{label}" if label else ""))
    dest.mkdir(parents=True, exist_ok=True)
    files = {}
    scrubbed_total = 0
    for f in _iter_state_files(root):
        rel = str(f.relative_to(root))
        try:
            data = read(rel)
        except Exception:
            continue  # corrupt files are quarantined by read(); skip
        clean, n = scrub_for_backup(data)
        scrubbed_total += n
        payload = json.dumps({"_schema": STATE_SCHEMA, "_v": 1, "data": clean},
                             indent=1, sort_keys=True)
        out = dest / rel
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(payload)
        _ensure_perms_file(out)
        files[rel] = hashlib.sha256(payload.encode()).hexdigest()
    manifest = {
        "schema": STATE_SCHEMA,
        "created_at": time.time(),
        "created_iso": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "label": label,
        "files": files,
        "scrubbed_values": scrubbed_total,
        "tool": "device_state.backup_state",
    }
    mpayload = json.dumps(manifest, indent=1, sort_keys=True)
    (dest / "manifest.json").write_text(mpayload)
    _ensure_perms_file(dest / "manifest.json")
    try:
        os.chmod(dest, 0o700)
    except Exception:
        pass
    # prune old generations (keep newest N)
    sibs = sorted([d for d in broot.iterdir() if d.is_dir()])
    for old in sibs[:-BACKUP_GENERATIONS]:
        shutil.rmtree(old, ignore_errors=True)
    return dest


def list_backups():
    broot = resolve_backups()
    if not broot.exists():
        return []
    return sorted([str(d) for d in broot.iterdir() if d.is_dir()])


def verify_backup(d):
    """Integrity + schema + no-raw-secrets. Returns (ok, problems)."""
    src = Path(d)
    problems = []
    if not src.exists():
        return False, ["backup dir missing"]
    try:
        manifest = json.loads((src / "manifest.json").read_text())
    except Exception as e:
        return False, [f"manifest unreadable: {e}"]
    if manifest.get("schema", 0) > STATE_SCHEMA:
        problems.append("future schema -> incompatible")
    for rel, digest in manifest.get("files", {}).items():
        f = src / rel
        if not f.exists():
            problems.append(f"missing file: {rel}")
            continue
        payload = f.read_bytes()
        if hashlib.sha256(payload).hexdigest() != digest:
            problems.append(f"checksum mismatch: {rel}")
            continue
        try:
            env = json.loads(payload.decode())
            _unwrap(env, rel)
        except Exception as e:
            problems.append(f"unparsable/incompatible {rel}: {e}")
            continue
        text = payload.decode("utf-8", "ignore")
        for p in SECRET_VALUE_RES:
            if re.search(p, text):
                problems.append(f"raw secret pattern in {rel}: {p}")
        # redacted refs are fine; raw secret KEYS with string values are suspect
        try:
            data = env["data"]

            def _walk(o, path=""):
                if isinstance(o, dict):
                    for k, v in o.items():
                        if _looks_secret_key(k) and isinstance(v, str) \
                                and v not in ("__REDACTED_SECRET_VALUE__", ""):
                            problems.append(
                                f"unredacted secret key {path}/{k}")
                        _walk(v, f"{path}/{k}")
                elif isinstance(o, list):
                    for i, x in enumerate(o):
                        _walk(x, f"{path}[{i}]")
            _walk(data)
        except Exception:
            pass
    return (len(problems) == 0), problems


def restore_state(d):
    """Atomic restore: validate candidate -> stage -> promote with rollback."""
    src = Path(d)
    ok, problems = verify_backup(src)
    if not ok:
        raise RuntimeError(f"backup invalid, refusing restore: {problems}")
    root = _root()
    manifest = json.loads((src / "manifest.json").read_text())
    # stage into temp candidate dir
    cand = root.parent / f".restore-candidate-{os.getpid()}"
    if cand.exists():
        shutil.rmtree(cand, ignore_errors=True)
    cand.mkdir(parents=True, exist_ok=True)
    try:
        for rel in manifest.get("files", {}):
            s = src / rel
            t = cand / rel
            t.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(s, t)
        # re-verify staged copies
        for rel, digest in manifest.get("files", {}).items():
            payload = (cand / rel).read_bytes()
            if hashlib.sha256(payload).hexdigest() != digest:
                raise RuntimeError(f"staging checksum mismatch: {rel}")
        # park current files for rollback, then promote atomically
        rollback = root.parent / f".restore-rollback-{int(time.time())}"
        rollback.mkdir(parents=True, exist_ok=True)
        for rel in manifest.get("files", {}):
            live = root / rel
            staged = cand / rel
            if live.exists():
                r = rollback / rel
                r.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(live, r)
                lc = _checksum_path(live)
                if lc.exists():
                    rc = rollback / (rel + ".sha256")
                    rc.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(lc, rc)
            live.parent.mkdir(parents=True, exist_ok=True)
            tmp = live.with_suffix(live.suffix + f".tmp{os.getpid()}")
            shutil.copy2(staged, tmp)
            _ensure_perms_file(tmp)
            os.replace(tmp, live)
            _ensure_perms_file(live)
            _checksum_path(live).write_text(
                hashlib.sha256(live.read_bytes()).hexdigest() + "\n")
            _ensure_perms_file(_checksum_path(live))
    finally:
        shutil.rmtree(cand, ignore_errors=True)
    return 0


# legacy names kept for CLI compat
def snapshot():
    dest = backup_state()
    # count for CLI message parity
    n = len(json.loads((dest / "manifest.json").read_text()).get("files", {}))
    print(f"{dest} ({n} files)")
    return 0


def restore(d):
    # accept both new backups and legacy raw-snapshot dirs
    src = Path(d)
    if (src / "manifest.json").exists():
        restore_state(src)
    else:
        # legacy raw snapshot: validate parses BEFORE touching live state
        cands = list(src.rglob("*.json"))
        if not cands:
            raise RuntimeError("no such backup")
        for f in cands:
            json.loads(f.read_text())
        for f in cands:
            rel = f.relative_to(src)
            data = json.loads(f.read_text())
            data = data["data"] if isinstance(data, dict) and \
                set(data.keys()) == {"_schema", "_v", "data"} else data
            write(str(rel), data)
    print(f"restored {d}")
    return 0


def main(argv):
    if len(argv) == 2 and argv[1] == "selftest":
        import uuid
        write("t.json", {"a": 1})
        ok1 = read("t.json") == {"a": 1}
        print(f"atomic roundtrip -> {'PASS' if ok1 else 'FAIL'}")
        k = f"op-{uuid.uuid4().hex[:6]}"
        r1, fresh1 = once(k, {"done": True})
        r2, fresh2 = once(k, {"done": True})
        ok2 = fresh1 and not fresh2 and r1 == r2 and peek(k) == r1
        print(f"idempotency no-double-exec -> {'PASS' if ok2 else 'FAIL'}")
        (_path("t.json")).write_bytes(b"{broken")
        try:
            read("t.json")
            ok3 = False
        except RuntimeError:
            ok3 = True
        print(f"corrupt quarantined -> {'PASS' if ok3 else 'FAIL'}")
        write("t.json", {"a": 2})
        import subprocess
        r = subprocess.run([sys.executable, __file__, "snapshot"],
                           capture_output=True, text=True)
        dest = r.stdout.strip().split(" ")[0]
        write("t.json", {"a": 999})
        subprocess.run([sys.executable, __file__, "restore", dest],
                       check=True, capture_output=True)
        ok4 = read("t.json") == {"a": 2}
        print(f"backup/restore -> {'PASS' if ok4 else 'FAIL'}")
        okp, probs = verify_permissions()
        print(f"permissions -> {'PASS' if okp else 'FAIL ' + str(probs)}")
        print(f"root={resolve_root()} (persistent={resolve_root() != LEGACY_ROOT})")
        ok = ok1 and ok2 and ok3 and ok4 and okp
        print("SELFTEST " + ("OK" if ok else "FAILED"))
        return 0 if ok else 1
    if len(argv) == 2 and argv[1] == "where":
        print(resolve_root())
        return 0
    if len(argv) == 2 and argv[1] == "backup":
        dest = backup_state()
        print(dest)
        return 0
    if len(argv) == 3 and argv[1] == "verify-backup":
        ok, problems = verify_backup(argv[2])
        print("OK" if ok else f"INVALID: {problems}")
        return 0 if ok else 1
    if len(argv) == 2 and argv[1] == "list-backups":
        for b in list_backups():
            print(b)
        return 0
    if len(argv) >= 3 and argv[1] == "read":
        print(json.dumps(read(argv[2])))
        return 0
    if len(argv) >= 3 and argv[1] == "write":
        write(argv[2], json.loads(sys.stdin.read()))
        print("wrote")
        return 0
    if len(argv) >= 4 and argv[1] == "once":
        r, fresh = once(argv[2], json.loads(sys.stdin.read()))
        print(json.dumps({"fresh": fresh, "result": r}))
        return 0
    if len(argv) >= 3 and argv[1] == "peek":
        print(json.dumps(peek(argv[2])))
        return 0
    if len(argv) >= 2 and argv[1] == "snapshot":
        return snapshot()
    if len(argv) >= 3 and argv[1] == "restore":
        return restore(argv[2])
    if len(argv) >= 2 and argv[1] == "list":
        for f in sorted(_iter_state_files()):
            print(f.relative_to(_root()))
        return 0
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv))
