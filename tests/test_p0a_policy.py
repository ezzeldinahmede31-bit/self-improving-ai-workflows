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


# ---- policy_gate wrapper + orchestrator step-0d (deny-branch anchors) ----
# These exist because a mutant forcing the WRAPPER to allow-all must fail.

def test_gate_wrapper_propagates_deny():
    import platform_wiring
    prof = platform_wiring.EnforcementProfile(
        policy={"default": "deny", "rules": []})
    v = platform_wiring.policy_gate(prof, agent="orchestrator",
                                    action="workflow.execute")
    assert v["enforced"] is True
    assert v["allowed"] is False


def test_gate_wrapper_propagates_allow():
    import platform_wiring
    prof = platform_wiring.EnforcementProfile(
        policy={"default": "allow", "rules": []})
    v = platform_wiring.policy_gate(prof, agent="orchestrator",
                                    action="workflow.execute")
    assert v["enforced"] is True
    assert v["allowed"] is True


def test_gate_unconfigured_passes_through_unenforced():
    import platform_wiring
    v = platform_wiring.policy_gate(None, agent="x", action="y")
    assert v == {"enforced": False, "allowed": True,
                 "needs_approval": False, "rule": "",
                 "reason": "no policy configured"}


def test_orchestrator_step0d_deny_routes_to_hitl(tmp_path):
    import platform_wiring
    from master_system_orchestrator import SystemOrchestrator
    orch = SystemOrchestrator(
        budget_usd=5.0,
        enforcement=platform_wiring.EnforcementProfile(
            policy={"default": "deny", "rules": []},
            egress=platform_wiring.EgressPolicy(allow_public_internet=True),
        ),
        evidence_dir=str(tmp_path),
        elide_output=True,
    )
    res = orch.execute_workflow_task(
        "denied by policy", {"nodes": [], "connections": {}}, daily_reqs=1)
    assert res["status"] == "PENDING_HUMAN_REVIEW"
    assert "policy denial" in res["reason"]
    assert "hitl_request_id" in res


def test_orchestrator_step0d_allow_passes_gate(tmp_path):
    import platform_wiring
    from master_system_orchestrator import SystemOrchestrator
    orch = SystemOrchestrator(
        budget_usd=5.0,
        enforcement=platform_wiring.EnforcementProfile(
            policy={"default": "allow", "rules": []},
            egress=platform_wiring.EgressPolicy(allow_public_internet=True),
        ),
        evidence_dir=str(tmp_path),
        elide_output=True,
    )
    res = orch.execute_workflow_task(
        "allowed by policy", {"nodes": [], "connections": {}}, daily_reqs=1)
    # allow must NOT route to a policy-denial HITL
    assert "policy denial" not in res.get("reason", "")
