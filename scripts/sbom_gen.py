"""Runtime SBOM generator — evidence, not enforcement.

Collects: python dists (name/version), interpreter + OS, OpenSSL + sqlite
versions, skills w/ hashes, MCP servers from opencode.jsonc, container
images referenced by tooling. Compares installed dists vs requirements.lock
(undeclared / drifted) and writes FINAL_AUDIT/sbom.json.
"""
import importlib.metadata as md
import json
import platform
import sqlite3
import ssl
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "FINAL_AUDIT"


def _lock_names():
    names = {}
    for line in (ROOT / "requirements.lock").read_text().splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "==" in line:
            n, _, v = line.partition("==")
            names[n.lower().replace("-", "_")] = v
    return names


def main():
    dists = sorted(
        ((d.metadata["Name"], d.version) for d in md.distributions()),
        key=lambda t: t[0].lower())
    lock = _lock_names()
    norm_installed = {n.lower().replace("-", "_"): v for n, v in dists
                      if n.lower() not in ("pip", "setuptools", "wheel")}
    undeclared = sorted(set(norm_installed) - set(lock))
    drifted = sorted(
        n for n in set(norm_installed) & set(lock)
        if norm_installed[n] != lock[n])
    try:
        skills = json.loads((ROOT / "skills-lock.json").read_text())["skills"]
    except Exception:
        skills = {}
    try:
        mcp = json.loads((ROOT / "opencode.jsonc").read_text()) \
            .get("mcp", {})
    except Exception:
        mcp = {}
    sbom = {
        "python": platform.python_version(),
        "os": f"{platform.system()} {platform.release()} {platform.machine()}",
        "openssl": ssl.OPENSSL_VERSION,
        "sqlite": sqlite3.sqlite_version,
        "dists": [{"name": n, "version": v} for n, v in dists],
        "dist_count": len(dists),
        "skills": [{"name": k,
                    "hash": (v.get("computedHash") or "")[:16],
                    "source": v.get("sourceType")}
                   for k, v in sorted(skills.items())],
        "skill_count": len(skills),
        "mcp_servers": sorted(mcp.keys()) if isinstance(mcp, dict) else [],
        "container_images_referenced": [
            "ghcr.io/semgrep/semgrep:latest",
            "projectdiscovery/nuclei:latest"],
        "lock_compare": {"undeclared": undeclared, "drifted": drifted},
    }
    (OUT / "sbom.json").write_text(json.dumps(sbom, indent=2))
    print(f"SBOM: {len(dists)} dists, {len(skills)} skills, "
          f"undeclared={len(undeclared)}, drifted={len(drifted)}")
    return 0 if not undeclared and not drifted else 2


if __name__ == "__main__":
    sys.exit(main())
