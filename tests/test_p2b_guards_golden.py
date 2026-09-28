"""Tests for scheduler_guards.py and golden_corpus.py."""


def test_cycle_detection():
    from scheduler_guards import find_cycle
    assert find_cycle({"a": ["b"], "b": ["c"], "c": []}) is None
    cyc = find_cycle({"a": ["b"], "b": ["c"], "c": ["a"]})
    assert cyc is not None and set(cyc) == {"a", "b", "c"}
    self_loop = find_cycle({"a": ["a"]})
    assert self_loop == ["a", "a"]


def test_starvation_aging():
    from scheduler_guards import StarvationWatch
    w = StarvationWatch(boost_after_s=100.0)
    w.waiting("t1", now=0.0)
    w.waiting("t2", now=50.0)
    late = w.starved(now=200.0)
    assert [r["task"] for r in late] == ["t1", "t2"]
    w.served("t1")
    assert [r["task"] for r in w.starved(now=200.0)] == ["t2"]


def test_perf_memory_ranking():
    from scheduler_guards import PerfMemory
    p = PerfMemory(window=10)
    for _ in range(5):
        p.record("fast", ok=True, latency_s=0.1, cost=0.01)
    for _ in range(5):
        p.record("slow", ok=True, latency_s=2.0, cost=0.5)
    assert p.best_for(["slow", "fast"]) == "fast"
    assert p.best_for(["slow"], max_cost=0.01) is None
    assert p.best_for(["ghost"]) is None
    s = p.summary("fast")
    assert s["success"] == 1.0 and s["samples"] == 5


def test_golden_gate_blocks_regression(tmp_path):
    from golden_corpus import GoldenCorpus
    g = GoldenCorpus(str(tmp_path / "g.json"))
    g.add_case("c1", reproducer="x", expect="y", incident="i1")
    out = g.gate_update({"c1": lambda: (True, "")})
    assert out["blocked"] is False and out["passed"] == ["c1"]
    out = g.gate_update({"c1": lambda: (False, "broke again")})
    assert out["blocked"] is True
    out = g.gate_update({})
    assert out["blocked"] is True and out["uncovered"] == ["c1"]
    g.save()
    g2 = GoldenCorpus(str(tmp_path / "g.json"))
    assert g2.gate_update({"c1": lambda: (True, "")})["total"] == 1
    import pytest
    with pytest.raises(ValueError):
        g.add_case("c2", reproducer="", expect="y")
