"""Tests for business_invariants.py."""

from business_invariants import InvariantEngine, dotted


def _clinic_engine():
    eng = InvariantEngine()
    eng.register("clinic", "doctor-match",
                 InvariantEngine.equals("appointment.doctor", "Dr. Samy"),
                 "requested doctor only")
    eng.register("clinic", "price-list",
                 lambda p: (p.get("price") in (800, 1000), "stale price"),
                 "current list prices")
    eng.register("clinic", "tz", InvariantEngine.one_of(
        "appointment.timezone", ["Africa/Cairo"]), "ops zone")
    return eng


def test_all_pass():
    eng = _clinic_engine()
    out = eng.evaluate("clinic", {"appointment": {"doctor": "Dr. Samy",
                                                 "timezone": "Africa/Cairo"},
                                  "price": 800})
    assert out == {"domain": "clinic", "passed": ["doctor-match",
                                                 "price-list", "tz"],
                   "failed": [], "ok": True}


def test_wrong_doctor_blocks():
    eng = _clinic_engine()
    out = eng.evaluate("clinic", {"appointment": {"doctor": "Dr. Other",
                                                 "timezone": "Africa/Cairo"},
                                  "price": 800})
    assert out["ok"] is False
    assert out["failed"][0]["name"] == "doctor-match"


def test_crashing_predicate_fails_closed():
    eng = InvariantEngine()

    def boom(payload):
        raise RuntimeError("bad predicate")

    eng.register("d", "x", boom)
    out = eng.evaluate("d", {})
    assert out["ok"] is False and "crashed" in out["failed"][0]["reason"]


def test_unknown_domain_passes_empty():
    eng = InvariantEngine()
    assert eng.evaluate("nope", {})["ok"] is True
    assert eng.domains() == []


def test_dotted_helper():
    assert dotted({"a": {"b": 1}}, "a.b") == 1
    assert dotted({"a": {}}, "a.b.c", default="d") == "d"
