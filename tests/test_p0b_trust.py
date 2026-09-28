"""Tests for skill_trust.py."""

import pytest

from skill_trust import TrustRegistry


def _reg(tmp_path):
    return TrustRegistry(str(tmp_path / "trust.json"), b"2" * 32)


def test_register_check_load_roundtrip(tmp_path):
    r = _reg(tmp_path)
    skill = tmp_path / "SKILL.md"
    skill.write_text("# demo skill")
    r.register(skill_id="demo", version="1.0", author="me",
               source="local", skill_md_path=str(skill),
               permissions=["calendar.read"], risk="low")
    r.save()
    r2 = TrustRegistry(str(tmp_path / "trust.json"), b"2" * 32)
    assert r2.sealed_ok is True
    verdict, _ = r2.check_load("demo", str(skill))
    assert verdict == "ok"


def test_tamper_detected(tmp_path):
    r = _reg(tmp_path)
    skill = tmp_path / "SKILL.md"
    skill.write_text("# v1")
    r.register(skill_id="demo", version="1.0", author="me",
               source="local", skill_md_path=str(skill),
               permissions=[], risk="low")
    r.save()
    skill.write_text("# v1 + injected line")
    r2 = TrustRegistry(str(tmp_path / "trust.json"), b"2" * 32)
    verdict, _ = r2.check_load("demo", str(skill))
    assert verdict == "tamper"


def test_broken_seal_fails_closed(tmp_path):
    r = _reg(tmp_path)
    skill = tmp_path / "SKILL.md"
    skill.write_text("# v1")
    r.register(skill_id="demo", version="1.0", author="me",
               source="local", skill_md_path=str(skill),
               permissions=[], risk="low")
    r.save()
    with open(tmp_path / "trust.json", "ab") as fh:
        fh.write(b" ")
    r2 = TrustRegistry(str(tmp_path / "trust.json"), b"2" * 32)
    assert r2.sealed_ok is False
    verdict, _ = r2.check_load("demo", str(skill))
    assert verdict == "unknown"


def test_high_risk_needs_review(tmp_path):
    r = _reg(tmp_path)
    skill = tmp_path / "SKILL.md"
    skill.write_text("# risky")
    r.register(skill_id="r", version="1", author="me", source="local",
               skill_md_path=str(skill), permissions=["*"], risk="high")
    verdict, _ = r.check_load("r", str(skill))
    assert verdict == "review"


def test_unknown_skill_and_bad_risk(tmp_path):
    r = _reg(tmp_path)
    verdict, _ = r.check_load("ghost", str(tmp_path / "nope.md"))
    assert verdict == "unknown"
    skill = tmp_path / "SKILL.md"
    skill.write_text("# x")
    with pytest.raises(ValueError):
        r.register(skill_id="x", version="1", author="a", source="s",
                   skill_md_path=str(skill), permissions=[], risk="wild")
