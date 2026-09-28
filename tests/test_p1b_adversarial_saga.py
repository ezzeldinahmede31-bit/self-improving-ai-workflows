"""Tests for adversarial_suite.py and saga.py."""


def test_corpus_shape_and_families():
    from adversarial_suite import cases, families
    all_cases = cases()
    assert len(all_cases) >= 10
    assert "prompt-injection" in families()
    for c in all_cases:
        assert {"id", "family", "payload", "expect"} <= set(c)
    assert len(cases("prompt-injection")) >= 2


def test_detector_grading():
    from adversarial_suite import run_suite

    def strict(case):
        return {"inj-direct": "block", "priv-esc": "block"}.get(
            case["id"], "allow")

    out = run_suite(strict)
    assert out["total"] == out["hits"] + sum(
        1 for r in out["rows"] if not r["ok"])
    assert 0.0 < out["rate"] < 1.0


def test_crashing_detector_fails_case():
    from adversarial_suite import run_suite

    def boom(case):
        raise RuntimeError("detector down")

    out = run_suite(boom)
    assert out["hits"] == 0 and out["rate"] == 0.0


def test_saga_happy_path(tmp_path):
    from saga import Saga
    s = Saga(str(tmp_path / "s.jsonl"))
    log = []
    s.add_step("book", lambda: log.append("book") or "b1",
               lambda: log.append("unbook"))
    s.add_step("pay", lambda: log.append("pay") or "p1",
               lambda: log.append("refund"))
    out = s.run("s1")
    assert out["committed"] and out["compensated"] == [] and \
        out["failed_at"] is None


def test_saga_compensates_reverse(tmp_path):
    from saga import Saga
    s = Saga(str(tmp_path / "s.jsonl"))
    order = []

    def fail():
        raise RuntimeError("payment declined")

    s.add_step("book", lambda: order.append("book"),
               lambda: order.append("unbook"))
    s.add_step("pay", fail, lambda: order.append("refund"))
    out = s.run("s2")
    assert not out["committed"] and out["failed_at"] == "pay"
    assert out["compensated"] == ["book"] and order[-1] == "unbook"


def test_saga_missing_compensation_reported(tmp_path):
    from saga import Saga
    s = Saga(str(tmp_path / "s.jsonl"))
    s.add_step("a", lambda: True)  # no undo defined

    def fail():
        raise RuntimeError("x")

    s.add_step("b", fail)
    out = s.run("s3")
    assert out["compensation_errors"] and \
        "no compensation" in out["compensation_errors"][0]["error"]
