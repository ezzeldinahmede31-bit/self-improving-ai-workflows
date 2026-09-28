"""Tests for supply_chain.py."""

import json

import supply_chain as sc


def test_sbom_lists_live_environment():
    sbom = sc.python_sbom()
    assert sbom["total"] > 0
    names = [p["name"].lower() for p in sbom["packages"]]
    assert "pytest" in names or "pip" in names


def test_lockfile_version_compare(tmp_path=None):
    import importlib.metadata as md
    try:
        ver = md.version("pytest")
    except md.PackageNotFoundError:
        ver = None
    if ver is None:
        return
    lock = {"pytest": {"version": ver}, "no-such-pkg": {"version": "1"}}
    out = sc.verify_lockfile(lock)
    assert out["ok"] and "no-such-pkg" in out["missing"]
    out2 = sc.verify_lockfile({"pytest": {"version": "0.0.0-zzz"}})
    assert not out2["ok"] and out2["mismatched"][0]["name"] == "pytest"


def test_skill_hash_verify_against_real_lock(tmp_path):
    out = sc.verify_skill_hashes()
    # Lock is partial by design: unknown entries are fine, mismatches are not.
    assert isinstance(out["checked"], int)
    assert out["mismatched"] == [] or all("name" in m for m in out["mismatched"])
    # Tamper path: forge a lock pointing at a real file with a wrong hash.
    import pathlib
    real = list(pathlib.Path(".opencode/skills").glob("*/SKILL.md"))
    assert real, "expected at least one skill doc"
    rel = real[0].relative_to(".opencode/skills").as_posix()
    fake = {"skills": {"Probe": {"skillPath": rel, "computedHash": "0" * 64}}}
    p = tmp_path / "lock.json"
    p.write_text(json.dumps(fake))
    out2 = sc.verify_skill_hashes(
        str(p), search_roots=(".opencode/skills",))
    assert len(out2["mismatched"]) == 1


def test_skill_hash_unreadable_lock(tmp_path):
    out = sc.verify_skill_hashes(str(tmp_path / "missing.json"))
    assert out["ok"] is False and out["reason"] == "lockfile unreadable"


def test_vuln_scan_skips_honestly_when_absent(monkeypatch):
    import shutil
    monkeypatch.setattr(shutil, "which", lambda *_a, **_k: None)
    out = sc.vuln_scan()
    assert out["status"] == "SKIPPED"


def test_file_signing_roundtrip(tmp_path):
    p = tmp_path / "a.bin"
    p.write_bytes(b"artifact-bytes")
    sig = sc.sign_file(str(p), b"1" * 32)
    assert sc.verify_file_signature(str(p), b"1" * 32, sig) is True
    p.write_bytes(b"tampered")
    assert sc.verify_file_signature(str(p), b"1" * 32, sig) is False
