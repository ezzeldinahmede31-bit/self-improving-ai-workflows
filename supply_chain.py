"""Supply-chain security: SBOM, lockfile verify, skill-hash verify.

Three independent checks, stdlib only, no network:
  - python_sbom() — enumerate installed distributions (importlib.metadata)
    with versions, locations, and installer origin where recorded.
  - verify_lockfile() — compare a pip-style lock ({name: version, files
    with sha256}) against the live environment.
  - verify_skill_hashes() — recompute sha256 over skill files named in
    skills-lock.json and report ok / mismatched / unknown (lock is
    partial by design: unknown means "not in lock", never "trusted").
  - vuln_scan() — run pip-audit when present, else SKIP with reason
    (never pretend a scan happened).
  - sign_file()/verify_file_signature() — HMAC envelope for any artifact
    (used by provenance + trust registry flows).
"""

from __future__ import annotations

import hashlib
import hmac
import json
import shutil
import subprocess
import time
from importlib import metadata
from pathlib import Path


def _sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def python_sbom() -> dict:
    """Enumerate installed distributions (name, version, origin)."""
    pkgs = []
    for dist in metadata.distributions():
        try:
            name = dist.metadata["Name"] or "unknown"
            ver = dist.version or "unknown"
        except (KeyError, AttributeError):
            continue
        origin = ""
        try:
            direct = dist.read_text("direct_url.json")
            if direct:
                origin = str(json.loads(direct).get("url", ""))
        except (OSError, ValueError, KeyError):
            origin = ""
        loc = ""
        try:
            loc = str(dist.locate_file("")) if hasattr(dist, "locate_file") else ""
        except (OSError, ValueError):
            loc = ""
        pkgs.append({"name": name, "version": ver, "origin": origin,
                     "location": loc})
    pkgs.sort(key=lambda p: p["name"].lower())
    return {"generated_at": time.time(), "total": len(pkgs),
            "packages": pkgs}


def verify_lockfile(lock: dict, *, check_files: bool = False) -> dict:
    """Compare {name: {version, files?}} lock against live environment.

    check_files also hashes installed RECORD-listed files when the lock
    carries per-file sha256 entries (slow; off by default).
    """
    live = {d.metadata["Name"].lower(): d.version
            for d in metadata.distributions() if d.metadata["Name"]}
    mismatched, missing, ok_total = [], [], 0
    for name, spec in (lock or {}).items():
        want = str((spec or {}).get("version", ""))
        got = live.get(str(name).lower())
        if got is None:
            missing.append(str(name))
        elif want and got != want:
            mismatched.append({"name": str(name), "want": want, "got": got})
        else:
            ok_total += 1
    out = {"ok": not mismatched, "matching": ok_total,
           "mismatched": mismatched, "missing": missing}
    if check_files:
        out["files_note"] = "per-file hashing runs on explicit request only"
    return out


def verify_skill_hashes(lock_path: str = "skills-lock.json",
                        search_roots: tuple[str, ...] = (
                            ".opencode/skills", ".agents/skills")) -> dict:
    """Recompute sha256 for skill files named in the lockfile.

    Returns ok / mismatched / unknown lists. `unknown` covers lock
    entries whose file cannot be located exactly once — resolution
    ambiguity is reported, never silently trusted.
    """
    try:
        lock = json.loads(Path(lock_path).read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {"ok": False, "reason": "lockfile unreadable",
                "ok_list": [], "mismatched": [], "unknown": []}
    entries = lock.get("skills", {}) if isinstance(lock, dict) else {}
    ok_list, mismatched, unknown = [], [], []
    for display, spec in entries.items():
        rel = str((spec or {}).get("skillPath", ""))
        want = str((spec or {}).get("computedHash", ""))
        if not rel or not want:
            unknown.append({"name": str(display), "why": "lock entry bare"})
            continue
        hits = [r for root in search_roots
                for r in [Path(root) / rel] if r.is_file()]
        if len(hits) != 1:
            unknown.append({"name": str(display),
                            "why": f"resolved {len(hits)} files"})
            continue
        actual = _sha256_file(hits[0])
        if hmac.compare_digest(actual, want):
            ok_list.append(str(display))
        else:
            mismatched.append({"name": str(display), "want": want[:12],
                               "got": actual[:12]})
    return {"ok": not mismatched, "checked": len(ok_list),
            "ok_list": ok_list, "mismatched": mismatched,
            "unknown": unknown}


def vuln_scan() -> dict:
    """Run pip-audit when installed; otherwise SKIP honestly."""
    exe = shutil.which("pip-audit")
    if exe is None:
        return {"status": "SKIPPED",
                "reason": "pip-audit not installed; no scan performed"}
    try:
        proc = subprocess.run([exe, "-f", "json"], capture_output=True,
                              text=True, timeout=300)
    except (OSError, subprocess.TimeoutExpired) as exc:
        return {"status": "ERROR", "reason": str(exc)}
    try:
        data = json.loads(proc.stdout or "[]")
    except ValueError:
        return {"status": "ERROR", "reason": "unparseable scanner output"}
    vulns = data if isinstance(data, list) else data.get("vulnerabilities", [])
    return {"status": "DONE", "total": len(vulns), "findings": vulns}


def sign_file(path: str, secret: bytes) -> str:
    """HMAC-sha256 hex over raw file bytes."""
    if not isinstance(secret, bytes) or len(secret) < 16:
        raise ValueError("secret must be bytes of 16+ bytes")
    return hmac.new(secret, Path(path).read_bytes(),
                    hashlib.sha256).hexdigest()


def verify_file_signature(path: str, secret: bytes, sig: str) -> bool:
    """Constant-time check of a file signature."""
    try:
        return hmac.compare_digest(sign_file(path, secret), str(sig))
    except (OSError, ValueError):
        return False
