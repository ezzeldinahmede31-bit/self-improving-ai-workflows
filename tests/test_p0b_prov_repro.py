"""Tests for provenance.py and reproducibility.py."""

import pytest

from provenance import ProvenanceLog, STAGES
from reproducibility import canonical, check_rebuild, digest, strip_volatile


def test_provenance_trace_order_and_gaps(tmp_path):
    log = ProvenanceLog(str(tmp_path / "prov.jsonl"))
    log.link("wf-1", "deployment", "n8n:prod")
    log.link("wf-1", "requirement", "REQ-7")
    trace = log.trace("wf-1")
    assert [t["stage"] for t in trace] == ["requirement", "deployment"]
    gaps = log.gaps("wf-1")
    assert "requirement" not in gaps and "test" in gaps
    assert log.gaps("wf-1", required=("requirement",)) == []


def test_provenance_rejects_bad_stage(tmp_path):
    log = ProvenanceLog(str(tmp_path / "prov.jsonl"))
    with pytest.raises(ValueError):
        log.link("wf-1", "teleport", "x")


def test_provenance_persists(tmp_path):
    p = tmp_path / "prov.jsonl"
    ProvenanceLog(str(p)).link("a", "test", "pytest: 12 passed")
    log2 = ProvenanceLog(str(p))
    assert log2.trace("a")[0]["ref"] == "pytest: 12 passed"
    assert log2.artifacts() == ["a"]
    assert len(STAGES) == 11


def test_canonical_determinism():
    a = {"z": 1, "a": [3, 2]}
    b = {"a": [3, 2], "z": 1}
    assert canonical(a) == canonical(b)
    assert digest(a) == digest(b)


def test_check_rebuild_detects_nondeterminism():
    import itertools
    seq = itertools.count()
    good = check_rebuild(lambda: {"nodes": [1, 2]})
    assert good["reproducible"] is True
    bad = check_rebuild(lambda: {"n": next(seq)})
    assert bad["reproducible"] is False


def test_strip_volatile_keys():
    obj = {"run_id": "abc", "nodes": [{"id": 1}], "ts": 123.0}
    clean = strip_volatile(obj)
    assert clean == {"nodes": [{"id": 1}]}
