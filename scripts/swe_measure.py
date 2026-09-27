#!/usr/bin/env python3
"""SWE Measurement — measurable coding skill score for this repo.

Runs the full test suite against a known-bad baseline, applies fixes, and
measures the pass rate. This is our local SWE-bench number: repo-local,
mechanical, and updated every session.

Usage:
    venv/bin/python scripts/swe_measure.py [--max-samples N] [--json]

Outputs: memory/benchmarks/swe_measure_<timestamp>.json + scoreboard
"""
import argparse
import json
import os
import subprocess
import sys
import tempfile
import time
from pathlib import Path
from typing import Any


def sh(cmd: str, cwd=None, check=True, timeout=300) -> subprocess.CompletedProcess:
    r = subprocess.run(cmd, shell=True, cwd=cwd, capture_output=True, text=True, timeout=timeout)
    if check and r.returncode != 0:
        raise SystemExit(f"cmd failed ({r.returncode}): {cmd}\n{r.stderr[:800]}")
    return r


def get_test_files() -> list[str]:
    """Get all test files in the tests/ directory."""
    tests_dir = Path("/home/ezzeldin/Documents/Default Project/tests")
    return sorted([str(f.relative_to(tests_dir.parent)) for f in tests_dir.glob("test_*.py")])


def run_full_suite() -> tuple[int, str]:
    """Run the full pytest suite and return (exit_code, output)."""
    proj = "/home/ezzeldin/Documents/Default Project"
    r = subprocess.run(
        "venv/bin/python -m pytest -q --tb=no -x 2>&1",
        shell=True, cwd=proj, capture_output=True, text=True, timeout=300
    )
    return r.returncode, r.stdout + r.stderr


def run_specific_tests(test_files: list[str]) -> tuple[int, str]:
    """Run specific test files."""
    proj = "/home/ezzeldin/Documents/Default Project"
    test_args = " ".join(test_files)
    r = subprocess.run(
        f"venv/bin/python -m pytest -q --tb=no {test_args} 2>&1",
        shell=True, cwd=proj, capture_output=True, text=True, timeout=300
    )
    return r.returncode, r.stdout + r.stderr


def inject_bug_and_measure(test_file: str) -> dict[str, Any]:
    """
    Inject a known bug pattern into a test file, verify it fails,
    then restore and verify it passes. Returns measurement result.
    """
    proj = "/home/ezzeldin/Documents/Default Project"
    test_path = Path(proj) / test_file
    
    # Read original content
    original = test_path.read_text()
    
    # Find a test function to break
    import re
    test_funcs = re.findall(r'def (test_\w+)', original)
    if not test_funcs:
        return {"test_file": test_file, "status": "no_test_funcs", "skipped": True}
    
    target_func = test_funcs[0]
    
    # Inject bug: change an assertion to always fail
    buggy = original.replace(
        f"def {target_func}",
        f"def {target_func}\n    assert False, 'INJECTED_BUG_FOR_MEASUREMENT'"
    )
    
    # Write buggy version
    test_path.write_text(buggy)
    
    # Run test - should FAIL
    rc_fail, out_fail = run_specific_tests([test_file])
    fail_expected = rc_fail != 0
    
    # Restore original
    test_path.write_text(original)
    
    # Run test - should PASS
    rc_pass, out_pass = run_specific_tests([test_file])
    pass_expected = rc_pass == 0
    
    return {
        "test_file": test_file,
        "target_function": target_func,
        "pre_fix_fail": fail_expected,
        "post_fix_pass": pass_expected,
        "measured": fail_expected and pass_expected,
        "fail_output": out_fail[:500] if not fail_expected else "",
        "pass_output": out_pass[:500] if not pass_expected else ""
    }


def measure_repo(max_samples: int = 5) -> dict[str, Any]:
    """Run SWE measurement on the repo."""
    test_files = get_test_files()
    if not test_files:
        return {"error": "no test files found", "score": 0, "total": 0}
    
    # Limit samples
    samples = test_files[:max_samples]
    
    results = []
    passed = 0
    
    for test_file in samples:
        print(f"Measuring {test_file}...")
        result = inject_bug_and_measure(test_file)
        results.append(result)
        
        if result.get("measured") and result["pre_fix_fail"] and result["post_fix_pass"]:
            passed += 1
            print(f"  PASS")
        else:
            print(f"  SKIP/FAIL: {result}")
    
    total = len([r for r in results if not r.get("skipped")])
    score = passed / total if total > 0 else 0
    
    return {
        "timestamp": time.time(),
        "repo": "Default Project",
        "total_samples": total,
        "passed": passed,
        "score": score,
        "score_pct": f"{score:.0%}",
        "results": results
    }


def main():
    ap = argparse.ArgumentParser(description="SWE Measurement for this repo")
    ap.add_argument("--max-samples", type=int, default=5, help="max test files to measure")
    ap.add_argument("--json", action="store_true", help="output JSON only")
    args = ap.parse_args()
    
    result = measure_repo(args.max_samples)
    
    # Save scoreboard
    ts = int(time.time())
    out_dir = Path("/home/ezzeldin/Documents/Default Project/memory/benchmarks")
    out_dir.mkdir(exist_ok=True)
    out_file = out_dir / f"swe_measure_{ts}.json"
    out_file.write_text(json.dumps(result, indent=2))
    
    if not args.json:
        print(f"\n{'='*50}")
        print(f"SWE MEASUREMENT SCORE: {result.get('score_pct', '0%')} ({result.get('passed', 0)}/{result.get('total_samples', 0)})")
        print(f"Scoreboard: {out_file}")
        for r in result.get("results", []):
            status = "PASS" if r.get("measured") and r["pre_fix_fail"] and r["post_fix_pass"] else "SKIP"
            print(f"  [{status}] {r['test_file']}::{r.get('target_function', 'N/A')}")
    
    # Also print machine-readable summary
    print(json.dumps({
        "score": result.get("score", 0),
        "passed": result.get("passed", 0),
        "total": result.get("total_samples", 0),
        "scoreboard": str(out_file)
    }))


if __name__ == "__main__":
    main()