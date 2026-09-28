"""Tests for tool_result_verifier.py."""

from tool_result_verifier import ResultVerifier, has_keys, matches


def test_verified_commit(tmp_path):
    v = ResultVerifier(str(tmp_path / "j.jsonl"))
    seen = []
    out = v.commit_if_verified(
        tool="calendar", claimed={"booked": True, "id": "e1"},
        checker=matches("id", "e1"), evidence="re-read",
        commit_fn=seen.append)
    assert out["verified"] and out["committed"] and seen == [
        {"booked": True, "id": "e1"}]


def test_failed_check_blocks_commit(tmp_path):
    v = ResultVerifier(str(tmp_path / "j.jsonl"))
    seen = []
    out = v.commit_if_verified(
        tool="calendar", claimed={"booked": True, "id": "e1"},
        checker=matches("id", "e2"), commit_fn=seen.append)
    assert not out["verified"] and not out["committed"] and seen == []


def test_has_keys_checker():
    ok, _ = has_keys("booked", "id")({"booked": True, "id": "x"})
    assert ok
    ok, note = has_keys("booked", "id")({"booked": True})
    assert not ok and "id" in note
    ok, _ = has_keys("a")("not-a-dict")
    assert not ok


def test_crashing_checker_fails_closed(tmp_path):
    v = ResultVerifier(str(tmp_path / "j.jsonl"))

    def boom(claimed):
        raise RuntimeError("checker bug")

    out = v.verify(tool="t", claimed={}, checker=boom)
    assert out["verified"] is False and "crashed" in out["note"]


def test_dry_run_without_commit_fn(tmp_path):
    v = ResultVerifier(str(tmp_path / "j.jsonl"))
    out = v.commit_if_verified(tool="t", claimed={"a": 1},
                               checker=has_keys("a"))
    assert out["verified"] and out["committed"] is False


def test_journal_appends(tmp_path):
    p = tmp_path / "j.jsonl"
    v = ResultVerifier(str(p))
    v.verify(tool="t", claimed={"a": 1}, checker=has_keys("a"))
    assert len(p.read_text().strip().splitlines()) == 1
