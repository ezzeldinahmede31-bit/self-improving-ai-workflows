"""Tests for traceability.py."""

import pytest

from traceability import Traceability


def test_link_and_coverage(tmp_path):
    t = Traceability(str(tmp_path / "t.json"))
    t.add_requirement("REQ-1", "Book with requested doctor",
                      ["doctor matches request"])
    t.add_requirement("REQ-2", "Confirm over channel",
                      ["user gets confirmation"])
    t.link_test("REQ-1", "test_books_doctor", "run-42")
    cov = t.coverage()
    assert cov["linked"] == ["REQ-1"] and cov["unlinked"] == ["REQ-2"]
    assert cov["total"] == 2 and cov["rate"] == 0.5


def test_assert_ready_blocks_gaps(tmp_path):
    t = Traceability(str(tmp_path / "t.json"))
    t.add_requirement("REQ-1", "stmt", ["a"])
    assert t.assert_ready()["ok"] is False
    t.link_test("REQ-1", "test_x", "ev")
    assert t.assert_ready()["ok"] is True
    out = t.assert_ready(["REQ-1", "REQ-9"])
    assert out["ok"] is False and out["unknown"] == ["REQ-9"]


def test_link_unknown_requirement_raises(tmp_path):
    t = Traceability(str(tmp_path / "t.json"))
    with pytest.raises(KeyError):
        t.link_test("REQ-?", "test_x")


def test_persistence_and_read(tmp_path):
    p = tmp_path / "t.json"
    t = Traceability(str(p))
    t.add_requirement("REQ-1", "stmt", ["a"])
    t.link_test("REQ-1", "test_x", "ev-1")
    t.save()
    t2 = Traceability(str(p))
    rec = t2.requirement("REQ-1")
    assert rec["tests"][0]["test"] == "test_x"
    assert t2.requirement("REQ-?") is None
