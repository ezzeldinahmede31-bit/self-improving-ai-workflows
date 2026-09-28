"""Tests for policy_engine.py (deterministic Policy-as-Code)."""

import pytest

from policy_engine import PolicyEngine


def _policy(**over):
    base = {
        "default": "deny",
        "rules": [
            {"id": "cal-read", "effect": "allow", "agent": "*",
             "action": "calendar.read", "resource": "*"},
            {"id": "mail-send", "effect": "approve", "agent": "worker",
             "action": "mail.send", "resource": "*"},
            {"id": "no-delete", "effect": "deny", "agent": "*",
             "action": "*.delete*", "resource": "*"},
        ],
        "budget": {"max_tokens": 100, "max_cost": 1.0,
                   "max_runtime_s": 3600},
    }
    base.update(over)
    return base


def test_allow_rule_matches():
    eng = PolicyEngine(_policy())
    d = eng.evaluate(agent="worker", action="calendar.read")
    assert d.allowed and not d.needs_approval and d.rule_id == "cal-read"


def test_deny_wins_over_allow():
    eng = PolicyEngine(_policy())
    d = eng.evaluate(agent="worker", action="calendar.delete")
    assert not d.allowed and d.rule_id == "no-delete"


def test_approve_routes_to_human():
    eng = PolicyEngine(_policy())
    d = eng.evaluate(agent="worker", action="mail.send")
    assert not d.allowed and d.needs_approval and d.rule_id == "mail-send"


def test_default_deny_when_no_rule_matches():
    eng = PolicyEngine(_policy())
    d = eng.evaluate(agent="stranger", action="mail.send")
    assert not d.allowed and d.rule_id == "default"


def test_prompt_cannot_override_deny():
    eng = PolicyEngine(_policy())
    # Even an "approved by prompt" claim changes nothing: verdict is pure
    # function of policy + request.
    d = eng.evaluate(agent="worker", action="db.delete",
                     resource="prod")
    assert not d.allowed and not d.needs_approval


def test_budget_exhaustion_denies_everything():
    eng = PolicyEngine(_policy())
    eng.record_use(tokens=500)
    d = eng.evaluate(agent="worker", action="calendar.read")
    assert not d.allowed and "budget" in d.reason
    assert eng.remaining()["tokens"] < 0


def test_record_use_rejects_negative():
    eng = PolicyEngine(_policy())
    with pytest.raises(ValueError):
        eng.record_use(tokens=-1)


def test_bad_policy_rejected():
    with pytest.raises(ValueError):
        PolicyEngine({"default": "sometimes"})
    with pytest.raises(ValueError):
        PolicyEngine({"rules": [{"id": "x"}]})
    with pytest.raises(TypeError):
        PolicyEngine("not-a-dict")
