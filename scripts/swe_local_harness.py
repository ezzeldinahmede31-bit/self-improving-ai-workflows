#!/usr/bin/env python3
"""swe_local_harness.py — run a local SWE-bench-style evaluation on a real repo.

Finds bug-fix commits in the git history (commits that touch BOTH source and
test files), verifies the test actually FAILS on the parent commit, then
grades a fix: after the agent/user applies a patch, the same test must PASS.

Usage:
    venv/bin/python scripts/swe_local_harness.py --repo <path> --max 5 [--since N]

Output:
    - scoreboard JSON (memory/benchmarks/swe_local_<repo>.json)
    - printed PASS/FAIL table per sample

The fix step is intentionally left to the agent (this process hands off):
  Phase A  harness: checkout parent in a worktree -> run tests (expect FAIL)
  Phase B  agent:    edit the worktree to fix the bug
  Phase C  harness:  re-run the same tests (expect PASS) -> grade + scoreboard
"""
import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


def sh(cmd, cwd=None, check=True, timeout=600):
    r = subprocess.run(cmd, shell=True, cwd=cwd, capture_output=True, text=True, timeout=timeout)
    if check and r.returncode != 0:
        raise SystemExit(f"cmd failed ({r.returncode}): {cmd}\n{r.stderr[:800]}")
    return r


def find_fix_commits(repo, max_n, since):
    cmd = f"git -C {repo} log --name-only -n {since} --pretty=format:'%H|%s'"
    r = sh(cmd, check=False)
    commits, cur = [], None
    for line in r.stdout.splitlines():
        if "|" in line and line.strip():
            cur = {"hash": line.split("|")[0], "msg": line.split("|")[1], "files": []}
            commits.append(cur)
        elif line.strip() and cur is not None:
            cur["files"].append(line.strip())
    fixes = []
    for i, c in enumerate(commits):  # newest -> oldest
        files = set(c["files"])
        has_src = any(f.endswith((".py", ".js", ".ts", ".go", ".rs", ".java"))
                      and "test" not in f.lower() for f in files)
        # tests may live in the same commit OR in its parent(s) (SWE-bench style)
        test_files = [f for f in files if "test" in f.lower()]
        for j in (i + 1, i + 2):
            if j < len(commits):
                test_files += [f for f in commits[j]["files"] if "test" in f.lower()]
        if has_src and test_files:
            fixes.append({"hash": c["hash"], "msg": c["msg"], "files": sorted(files),
                          "test_files": sorted(set(test_files))})
        if len(fixes) >= max_n:
            break
    return fixes


def run_tests(worktree, test_files, repo=None):
    """Run the changed test files explicitly (deterministic, no discovery)."""
    if not test_files:
        return -1
    if Path(worktree, "pytest.ini").exists() or Path(worktree, "pyproject.toml").exists() \
       or Path(worktree, "requirements-dev.txt").exists():
        r = sh(f"cd {worktree} && python -m pytest -q --no-header -p no:cacheprovider {test_tokens(test_files, worktree)} > /tmp/_swe_local_run.log 2>&1; rc=$?; tail -4 /tmp/_swe_local_run.log; exit $rc", check=False)
        return r.returncode
    modules = " ".join(t.replace(os.sep, ".").removesuffix(".py") for t in test_files)
    r = sh(f"cd {worktree} && python -m unittest -v {modules} > /tmp/_swe_local_run.log 2>&1; rc=$?; tail -4 /tmp/_swe_local_run.log; exit $rc", check=False)
    return r.returncode


def test_tokens(test_files, worktree):
    return " ".join(str(Path(worktree) / t) for t in test_files if Path(worktree, t).exists())


def grade(results_path, out=None):
    """Phase C: re-run tests in each worktree AFTER the agent applied a fix."""
    res = json.loads(Path(results_path).read_text())
    score = {"passed": 0, "failed": 0, "samples": []}
    for r in res:
        rc = run_tests(r["worktree"], r["test_files"])
        ok = rc == 0
        r["post_fix_test_status"] = "pass" if ok else "FAIL"
        score["samples"].append({"commit": r["commit"], "fix_msg": r["msg"],
                                 "pre": r["pre_fix_test_status"],
                                 "post": r["post_fix_test_status"]})
        if ok:
            score["passed"] += 1
        else:
            score["failed"] += 1
        print(f"[{'PASS' if ok else 'FAIL'}] {r['commit'][:10]} {r['msg'][:50]}")
    score_path = out or str(Path(results_path).with_suffix(".scoreboard.json"))
    Path(score_path).write_text(json.dumps(score, indent=2))
    total = score["passed"] + score["failed"]
    print(f"\nSCORE: {score['passed']}/{total} resolved  ({score['passed']/total:.0%})" if total else "\nSCORE: no samples")
    print(f"scoreboard: {score_path}")


def main():
    ap = argparse.ArgumentParser(description="Local SWE-bench-style harness")
    ap.add_argument("--repo", required=True, help="path to the git repository")
    ap.add_argument("--max", type=int, default=4)
    ap.add_argument("--since", type=int, default=200, help="scan window (commits back)")
    ap.add_argument("--grade", default=None, help="Phase C: path to Phase-A JSON to grade")
    args = ap.parse_args()

    if args.grade:
        grade(args.grade)
        return

    repo = Path(args.repo).resolve()
    assert (repo / ".git").exists(), "not a git repo"
    fixes = find_fix_commits(repo, args.max, args.since)
    if not fixes:
        print("No bug-fix commits found (need commits touching src+tests).")
        return

    print(f"== {len(fixes)} samples in {repo}")
    results = []
    tmp = Path(tempfile.mkdtemp(prefix="swe_local_"))
    for i, c in enumerate(fixes, 1):
        test_files = c["test_files"]
        wt = tmp / f"wt{i}"
        sh(f"git -C {repo} worktree add -q {wt} {c['hash']}~1", check=False)
        phase_a = run_tests(wt, test_files)
        print(f"[{i}/{len(fixes)}] {c['hash'][:10]} {c['msg'][:60]} | parent tests: {'FAIL(expected)' if phase_a != 0 else 'UNEXPECTED PASS'}")
        results.append({"commit": c["hash"], "msg": c["msg"], "worktree": str(wt),
                        "pre_fix_test_status": "fail" if phase_a != 0 else "pass",
                        "files": c["files"], "test_files": test_files})
    sh(f"git -C {repo} worktree prune")
    out = repo.parent / f"swe_local_{repo.name}.json"
    out.write_text(json.dumps(results, indent=2))
    print(f"\nPhase A done -> samples in {out}")
    print("Phase B: apply your fix in the listed worktrees, then rerun:\n"
          f"  {sys.argv[0]} --grade {out}")
    if "--grade" in sys.argv:  # Phase C (not used via argparse path; kept simple)
        pass


if __name__ == "__main__":
    main()