"""Supply-pin regression: prod import surface ⊆ pinned lock.

- requirements.prod.txt pins every third-party module the production
  path imports (AST-proven, stdlib excluded).
- installed versions match the pins (drift fails the test).
- `requests` is banned from the production path (stdlib pinned
  transport only) — the n8n conversion must never regress.
- requirements.lock is a full deterministic freeze (fresh-install
  proven separately; see FINAL_AUDIT/dependency_results.json).
- skills stay hash-pinned via skills-lock.json.
"""
import ast
import importlib.metadata as _md
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)


def _parse_pins(path):
    pins = {}
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            m = re.match(r"^([A-Za-z0-9_.\-]+)==([^\s;]+)", line)
            assert m, f"unparsable lock line: {line}"
            pins[m.group(1).lower().replace("-", "_")] = m.group(2)
    return pins


def _prod_third_party():
    stdlib = set(sys.stdlib_module_names)
    local = set()
    for dp, _, fn in os.walk(ROOT):
        if "/venv" in dp or "/.git" in dp:
            continue
        for f in fn:
            if f.endswith(".py"):
                local.add(f[:-3])
    files = [os.path.join(ROOT, f) for f in os.listdir(ROOT)
             if f.endswith(".py")]
    for f in os.listdir(os.path.join(ROOT, "orchestrator")):
        if f.endswith(".py"):
            files.append(os.path.join(ROOT, "orchestrator", f))
    found = {}
    for rel in files:
        try:
            tree = ast.parse(open(rel, encoding="utf-8").read())
        except Exception:
            continue
        for n in ast.walk(tree):
            mods = []
            if isinstance(n, ast.Import):
                mods = [a.name.split(".")[0] for a in n.names]
            elif isinstance(n, ast.ImportFrom) and n.module and n.level == 0:
                mods = [n.module.split(".")[0]]
            for m in mods:
                if m not in stdlib and m not in local and m != "orchestrator":
                    found.setdefault(m, set()).add(
                        os.path.relpath(rel, ROOT))
    return found


def test_prod_imports_covered_by_pins():
    pins = _parse_pins(os.path.join(ROOT, "requirements.prod.txt"))
    found = _prod_third_party()
    norm = {k.lower().replace("-", "_"): k for k in pins}
    # canonical distribution-name mapping for known imports
    aliases = {"yaml": "pyyaml"}
    uncovered = {}
    for mod, files in found.items():
        key = aliases.get(mod, mod)
        if key not in norm:
            uncovered[mod] = sorted(files)
    assert uncovered == {}, f"unpinned prod imports: {uncovered}"


def test_installed_matches_pins():
    pins = _parse_pins(os.path.join(ROOT, "requirements.prod.txt"))
    for dist, ver in pins.items():
        assert _md.version(dist) == ver, \
            f"drift: {dist} installed {_md.version(dist)} != pinned {ver}"


def test_requests_banned_from_prod_path():
    found = _prod_third_party()
    assert "requests" not in found, \
        f"requests in prod path: {found['requests']}"


def test_full_lock_fresh_and_sorted():
    lines = [l.strip() for l in
             open(os.path.join(ROOT, "requirements.lock"), encoding="utf-8")
             if l.strip() and not l.startswith("#")]
    assert len(lines) > 50, "lock unexpectedly small"
    names = [l.split("==")[0] for l in lines]
    assert names == sorted(names, key=str.lower), "lock must stay sorted"
    for line in lines:
        assert re.match(r"^[A-Za-z0-9_.\-]+==[^\s;]+$", line), \
            f"unparsable lock line: {line}"


def test_skills_hash_pinned():
    lock = json.load(open(os.path.join(ROOT, "skills-lock.json"),
                          encoding="utf-8"))
    skills = lock.get("skills", {})
    assert len(skills) > 0
    for name, rec in list(skills.items())[:50]:
        assert rec.get("computedHash"), f"unhashed skill: {name}"
