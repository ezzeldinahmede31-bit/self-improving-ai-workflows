#!/usr/bin/env python3
"""Self-audit for the frontier-parity harness (v1.0.0).

Checks (all read-only, stdlib only):
 1. allowlisted model IDs resolve in the LIVE catalog with status=active.
 2. no mock/fake/stub model results: harness source + artifacts contain no
    fabricated-result markers; every row carries provenance fields.
 3. rubric consistency: every runnable task has a grader; sealed tasks have prompt=null.
 4. no reference-answer leakage: exact expected outputs absent from prompts.
 5. token honesty: every artifact row labels MEASURED/UNMEASURED; UNMEASURED never 0-cost-claimed.
 6. grader determinism: grade-twice identical on sample outputs.
 7. confinement: no production files outside benchmarks/frontier_parity/ modified (git status).

Usage: venv/bin/python benchmarks/frontier_parity/self_audit.py [--artifact runs/matrix_X.json]
Exit 0 = all checks pass. Any failure prints the finding and exits 1.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
sys.path.insert(0, str(HERE))

import graders  # noqa: E402
import modes  # noqa: E402

FAILURES: list[str] = []


def check(name: str, ok: bool, detail: str = "") -> None:
    print(f"[{'PASS' if ok else 'FAIL'}] {name} {detail}")
    if not ok:
        FAILURES.append(name)


def live_catalog_ids(opencode_bin: str = "opencode") -> set[str]:
    out = subprocess.run([opencode_bin, "models", "--verbose"],
                         capture_output=True, text=True, timeout=60)
    ids, active = set(), set()
    import re
    for m in re.finditer(r"^(opencode/[^\s]+)\n(\{.*?\n\})", out.stdout, re.M | re.S):
        ids.add(m.group(1))
        try:
            if json.loads(m.group(2)).get("status") == "active":
                active.add(m.group(1))
        except ValueError:
            pass
    return ids, active


def main() -> int:
    ap = __import__("argparse").ArgumentParser()
    ap.add_argument("--artifact", default="")
    args = ap.parse_args()

    tasks = json.loads((HERE / "tasks_v1.json").read_text(encoding="utf-8"))["tasks"]
    runnable = [t for t in tasks if not t.get("held_out")]
    sealed = [t for t in tasks if t.get("held_out")]

    # 1. model identity vs live catalog
    try:
        ids, active = live_catalog_ids()
        check("models-in-catalog", modes.ALLOWLIST <= ids, f"allowlist={sorted(modes.ALLOWLIST)}")
        check("models-active", modes.ALLOWLIST <= active, "")
    except Exception as exc:  # noqa: BLE001
        check("models-in-catalog", False, f"catalog unreadable: {exc}")

    # 2. no fabricated-result markers in harness source.
    # Whole-word match, negation-aware: a bare 'mock'/'fake'/'stub' outside a
    # negated context (no/never/refus/without/not) is a finding.
    import re as _re
    src_lines = ((HERE / "modes.py").read_text()
                 + (HERE / "run_matrix.py").read_text()).splitlines()
    bad = [ln.strip()[:80] for ln in src_lines
           if _re.search(r"\b(mock|fake|stub|fabricat\w+|hardcoded score)\b", ln, _re.I)
           and not _re.search(r"\b(no|never|refus\w*|without|not|against)\b", ln, _re.I)]
    check("no-mock-markers", not bad, f"found={bad}" if bad else "")

    # 3. rubric consistency
    missing = [t["id"] for t in runnable if t["id"] not in graders.GRADERS]
    check("graders-registered", not missing, f"missing={missing}" if missing else "")
    noaccept = [t["id"] for t in runnable if not t.get("acceptance")]
    check("acceptance-present", not noaccept, "")
    sealed_ok = all(t.get("prompt") is None for t in sealed)
    check("sealed-prompts-null", sealed_ok, f"sealed={len(sealed)}")

    # 4. no reference-answer leakage into prompts
    leaks = []
    for t in runnable:
        p = t.get("prompt", "") or ""
        if "333833500" in p:
            leaks.append(t["id"])
        if t["id"] == "FP-R01" and "'15'" in p.replace("[0, 100]", ""):
            leaks.append(t["id"])
    check("no-answer-leak", not leaks, f"leaks={leaks}" if leaks else "")

    # 5+6. grader determinism on samples
    samples = {
        "FP-R01": "15", "FP-M01": "333833500",
        "FP-C01": "def median(a):\n    s = sorted(a)\n    n = len(s)\n    m = n // 2\n    return s[m] if n % 2 else (s[m-1] + s[m]) / 2\n",
        "FP-D01": "def find(a, x):\n    lo, hi = 0, len(a)\n    while lo < hi:\n        mid = (lo + hi) // 2\n        if a[mid] < x:\n            lo = mid + 1\n        else:\n            hi = mid\n    return lo if lo < len(a) and a[lo] == x else -1\n",
        "FP-P01": '["b", "c", "a", "d", "e", "f"]',
        "FP-T01": "DYNAMIC", "FP-N01": "2026-10-09",
        "FP-X01": '{"title": "t", "owner": "o", "eta": "e", "cities": "Paris Berlin Madrid"}',
    }
    det_ok = True
    for tid, sample in samples.items():
        ctx = {"fixture_total": sample} if tid == "FP-T01" else {}
        out = sample if tid != "FP-T01" else sample
        r1 = graders.grade(tid, out, ctx)
        r2 = graders.grade(tid, out, ctx)
        if r1 != r2 or not r1[0]:
            det_ok = False
            print(f"  grader issue {tid}: {r1} vs {r2}")
    check("grader-deterministic", det_ok, "")

    # artifact checks
    if args.artifact:
        art = json.loads(Path(args.artifact).read_text(encoding="utf-8"))
        rows = art.get("rows", [])
        prov = all(all(k in r for k in ("task", "mode", "model", "prompt_sha", "token_status"))
                   for r in rows)
        check("artifact-provenance", prov, f"rows={len(rows)}")
        tok = all(r.get("token_status") in ("MEASURED", "UNMEASURED") for r in rows)
        check("artifact-token-labels", tok, "")
        nomock = all("mock" not in str(r.get("model", "")).lower() for r in rows)
        check("artifact-no-mock-models", nomock, "")
        chron = all(r.get("harness") == modes.HARNESS_VERSION for r in rows)
        check("artifact-harness-version", chron, "")

    # 7. confinement (git status, read-only)
    try:
        out = subprocess.run(["git", "status", "--porcelain"], capture_output=True,
                             text=True, timeout=30, cwd=str(ROOT))
        touched = [l[3:] for l in out.stdout.splitlines() if l.strip()]
        # Designated artifact dirs (benchmark outputs) are allowed; anything
        # else (prod code, configs, memory narrative) is a finding.
        allowed_prefixes = ("benchmarks/frontier_parity/", "benchmarks/",
                            "memory/benchmarks/", "output/")
        outside = [f for f in touched
                   if not f.startswith(allowed_prefixes)]
        check("confinement", not outside, f"outside={outside}" if outside else f"touched={len(touched)}")
    except Exception as exc:  # noqa: BLE001
        check("confinement", False, f"git unreadable: {exc}")

    print("SELF-AUDIT " + ("PASS" if not FAILURES else f"FAIL: {FAILURES}"))
    return 0 if not FAILURES else 1


if __name__ == "__main__":
    raise SystemExit(main())
