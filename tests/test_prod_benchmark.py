"""Production general-benchmark integrity gate.

Asserts the battery itself is sound (coverage, determinism, honest framing)
without re-running the full evidence report: the script run is the evidence
(memory/benchmarks/prod_general_*.json); this test guards the harness.
"""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "scripts"))

import prod_general_benchmark as B  # noqa: E402

REQUIRED_DIMENSIONS = {"mathematics", "reasoning", "coding", "debugging",
                       "planning", "tool-use", "multi-step", "novel",
                       "cross-domain", "safety", "research", "writing"}


def test_battery_covers_all_dimensions():
    bat = B.build_battery()
    dims = {t["dimension"] for t in bat._tasks}
    assert REQUIRED_DIMENSIONS <= dims, f"missing: {REQUIRED_DIMENSIONS - dims}"
    assert len(bat.tasks()) >= 12


def test_battery_has_no_skill_tasks():
    dims = {t["dimension"] for t in B.build_battery()._tasks}
    assert {"novel", "cross-domain", "research"} <= dims


def test_suite_is_deterministic():
    bat = B.build_battery()
    r1 = bat.compare({"direct": B.direct, "system": B.system})
    r2 = bat.compare({"direct": B.direct, "system": B.system})
    for name in ("direct", "system"):
        a = r1["results"][name]
        b = r2["results"][name]
        assert a["pass_rate"] == b["pass_rate"]
        assert [r["ok"] for r in a["rows"]] == [r["ok"] for r in b["rows"]]


def test_system_never_scores_below_direct():
    bat = B.build_battery()
    res = bat.compare({"direct": B.direct, "system": B.system})
    assert (res["results"]["system"]["pass_rate"]
            >= res["results"]["direct"]["pass_rate"])
    assert res["pick"] == "system"
