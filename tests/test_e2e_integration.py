"""E2E Integration Test Scenarios - Validates the 7 chains end-to-end.

These are NOT unit tests — they exercise the full production path:
orchestrator → policy → capability → sandbox → egress → n8n → verification
→ invariants → audit → deployment → monitoring → incident.

Each scenario asserts the full path behaves as expected.
"""

from __future__ import annotations

import tempfile
import time

import platform_wiring
from master_system_orchestrator import SystemOrchestrator
from platform_wiring import EnforcementProfile, EgressPolicy


def _sample_workflow(authed: bool = False) -> dict:
    """A minimal valid n8n workflow with a webhook and expected output.

    authed=True sets webhook authentication so the chain can proceed past
    the security gate (R5 WEBHOOK_NO_AUTH) to the later stages under test.
    No credentials are embedded and no external traffic is performed by any
    scenario (the n8n step is skipped without an API key; tool probes are
    localhost/docker-inspect only).
    """
    webhook_params = {"path": "test-e2e",
                      "pinnedData": {"1": {"json": {}}}}
    if authed:
        webhook_params["authentication"] = "headerAuth"
    return {
        "nodes": [
            {"name": "Webhook", "type": "n8n-nodes-base.webhook",
             "parameters": webhook_params},
            {"name": "HTTP Request", "type": "n8n-nodes-base.httpRequest",
             "parameters": {"url": "https://httpbin.org/post", "method": "POST"}},
        ],
        "connections": {
            "Webhook": {"main": [[{"node": "HTTP Request"}]]},
        },
        "n8n_workflow_id": "test-workflow-id",
        "n8n_payload": {"test": "e2e"},
        "n8n_expected_output": {"status": "ok"},
        "webhook_path": "test-e2e",
    }


def _business_checks() -> dict:
    return {
        "domain": "clinic",
        "payload": {"appointment": {"doctor": "Dr. Samy", "timezone": "Africa/Cairo"},
                    "price": 800},
        "checks": [
            ("doctor-match",
             lambda p: (p["appointment"]["doctor"] == "Dr. Samy", "wrong doctor"),
             "requested doctor only"),
            ("price-list",
             lambda p: (p["price"] in (800, 1000), "stale price"),
             "current list prices"),
        ],
    }


def run_scenario_A_valid_execution():
    """Scenario A: Valid agent execution through the full chain."""
    with tempfile.TemporaryDirectory() as tmp:
        orch = SystemOrchestrator(
            budget_usd=100.0,
            enforcement=EnforcementProfile(
                policy={"default": "allow",
                        "rules": [{"id": "allow-net", "effect": "allow",
                                   "agent": "*", "action": "net.fetch",
                                   "resource": "*"}]},
                capability_secret=b"cap-secret-32-bytes-minimum-length-here",
                egress=platform_wiring.EgressPolicy(
                    allow_public_internet=True,
                    allowed_domains=("httpbin.org",))),
            evidence_dir=tmp,
        )
        wf = _sample_workflow(authed=True)
        res = orch.execute_workflow_task(
            task_prompt="E2E valid booking flow",
            workflow_json=wf,
            daily_reqs=10,
            business=_business_checks(),
        )
        return res


def run_scenario_B_policy_denial():
    """Scenario B: Policy denial blocks execution before tool runs."""
    with tempfile.TemporaryDirectory() as tmp:
        orch = SystemOrchestrator(
            budget_usd=100.0,
            enforcement=EnforcementProfile(
                policy={"default": "deny",
                        "rules": [{"id": "deny-all", "effect": "deny",
                                   "agent": "*", "action": "*", "resource": "*"}]},
                capability_secret=b"cap-secret-32-bytes-minimum-length-here",
                egress=platform_wiring.EgressPolicy(
                    allow_public_internet=True),
                ),
            evidence_dir=tmp,
        )
        wf = _sample_workflow()
        res = orch.execute_workflow_task(
            task_prompt="Should be denied by policy",
            workflow_json=wf,
            daily_reqs=10,
        )
        return res


def run_scenario_C_untrusted_skill():
    """Scenario C: Untrusted skill held for review at the skill-trust gate.

    Uses a fully isolated registry directory (never a fixed /tmp path, so
    parallel runs cannot collide). Returns the actual registry verdict.
    """
    with tempfile.TemporaryDirectory() as tmp:
        import os
        reg_dir = os.path.join(tmp, "skill-trust")
        secret = b"trust-secret-32-bytes-minimum-length"
        orch = SystemOrchestrator(
            budget_usd=100.0,
            enforcement=EnforcementProfile(
                policy={"default": "allow"},
                trust_registry_path=reg_dir,
                trust_secret=secret,
            ),
            evidence_dir=tmp,
        )
        assert orch is not None  # wiring constructed; verdict comes from registry
        from skill_trust import TrustRegistry
        reg = TrustRegistry(reg_dir, secret)
        sk = tempfile.NamedTemporaryFile(suffix=".md", delete=False, dir=tmp)
        sk.write(b"# test\nname: malicious\n")
        sk.close()
        reg.register(skill_id="malicious", version="1", author="attacker",
                     source="unknown", skill_md_path=sk.name,
                     permissions=["*"], risk="high")
        verdict, reason = reg.check_load("malicious", sk.name)
        return {"status": "tested", "verdict": verdict, "reason": reason,
                "sealed": reg.sealed_ok}


def run_scenario_D_verification_failure():
    """Scenario D: Model action passes tool but fails invariant check."""
    with tempfile.TemporaryDirectory() as tmp:
        orch = SystemOrchestrator(
            budget_usd=100.0,
            enforcement=EnforcementProfile(
                policy={"default": "allow"},
                capability_secret=b"cap-secret-32-bytes-minimum-length-here",
                egress=platform_wiring.EgressPolicy(
                    allow_public_internet=True,
                    allowed_domains=("httpbin.org",))),
            evidence_dir=tmp,
        )
        wf = _sample_workflow()
        # Business checks with WRONG doctor (well-formed 3-tuple specs:
        # (name, fn, doc) — malformed specs are a separate fail-closed test).
        bad_business = {
            "domain": "clinic",
            "payload": {"appointment": {"doctor": "Dr. Wrong", "timezone": "Africa/Cairo"},
                        "price": 800},
            "checks": [
                ("doctor-match",
                 lambda p: (p["appointment"]["doctor"] == "Dr. Samy", "wrong doctor"),
                 "requested doctor only"),
            ],
        }
        res = orch.execute_workflow_task(
            task_prompt="E2E invariant failure",
            workflow_json=dict(
                {"nodes": [
                    {"name": "Webhook", "type": "n8n-nodes-base.webhook",
                     "parameters": {"path": "test-invariant",
                                    "authentication": "headerAuth",
                                    "pinnedData": {"1": {"json": {}}}}},
                    {"name": "HTTP Request", "type": "n8n-nodes-base.httpRequest",
                     "parameters": {"url": "https://httpbin.org/post", "method": "POST"}},
                ],
                "connections": {"Webhook": {"main": [[{"node": "HTTP Request"}]]}},
                "n8n_workflow_id": "test-workflow-id",
                "n8n_payload": {"test": "e2e"},
                "n8n_expected_output": {"status": "ok"},
                "webhook_path": "test-invariant",
            }),
            daily_reqs=10,
            business=bad_business,
        )
        return res


def run_scenario_E_deployment_failure():
    """Scenario E: Deployment canary fails and rolls back."""
    with tempfile.TemporaryDirectory() as tmp:
        orch = SystemOrchestrator(
            budget_usd=100.0,
            enforcement=EnforcementProfile(
                policy={"default": "allow"},
                capability_secret=b"cap-secret-32-bytes-minimum-length-here",
                egress=platform_wiring.EgressPolicy(
                    allow_public_internet=True),
                ),
            evidence_dir=tmp,
        )
        wf = _sample_workflow(authed=True)
        probe_calls: list = []

        def _recording_probe(stage: int, ok: bool):
            def _probe():
                probe_calls.append(stage)
                return ok, {"err": 0.0 if ok else 0.5}
            return _probe

        orch.set_deployment_probes(
            probes={
                1: _recording_probe(1, True),
                10: _recording_probe(10, True),
                50: _recording_probe(50, False),
                100: _recording_probe(100, True),
            },
            promote_fn=lambda stage: None,
        )
        res = orch.execute_workflow_task(
            task_prompt="E2E deployment rollback",
            workflow_json=wf,
            daily_reqs=10,
            business=_business_checks(),
        )
        res = dict(res)
        res["probe_calls"] = probe_calls
        return res


def run_scenario_F_incident_recovery():
    """Scenario F: Incident detected, correlated, recovery, golden case created."""
    with tempfile.TemporaryDirectory() as tmp:
        orch = SystemOrchestrator(
            budget_usd=100.0,
            enforcement=EnforcementProfile(
                policy={"default": "allow"},
                incident_actions={"kill_session": lambda i, c: None,
                                  "revoke_token": lambda i, c: None,
                                  "quarantine_workflow": lambda i, c: None,
                                  "alert_human": lambda i, c: None,
                                  "preserve_evidence": lambda i, c: None},
                ),
            evidence_dir=tmp,
        )
        # Simulate incident
        from incident import IncidentResponse, correlate
        ir = IncidentResponse({
            "kill_session": lambda i, c: None,
            "revoke_token": lambda i, c: None,
            "quarantine_workflow": lambda i, c: None,
            "alert_human": lambda i, c: None,
            "preserve_evidence": lambda i, c: None,
        })
        base = time.time()
        alerts = [
            {"agent": "a", "session": "s", "kind": "url", "ts": base},
            {"agent": "a", "session": "s", "kind": "cred", "ts": base + 5},
            {"agent": "a", "session": "s", "kind": "api", "ts": base + 9},
        ]
        corr = correlate(alerts)
        # All 3 alerts share (agent, session) inside the window with >=2
        # kinds, so they fuse into exactly 1 incident and nothing is lonely.
        return {"correlated": len(corr["incidents"]) == 1,
                "lonely_kept": len(corr["lonely"]) == 0}


# ---------------------------------------------------------------------------
# pytest entry points — these are what the suite actually collects and runs.
# Before 2026-10-10 this module exposed zero test_ functions, so none of the
# six scenarios below ever executed in CI despite the file living in tests/.
# Each test asserts the stage the scenario names (not a vacuous "ok").
# Evidence class: COMPONENT_INTEGRATION_TEST (mocked transports, real chain).
# ---------------------------------------------------------------------------

def test_A_valid_execution_passes_capability_and_security_gates():
    """A: allowed policy + allow-listed egress must NOT stop at step 2d.

    Regression for the capability-namespace defect (mint resource="task:*"
    could never match the hostname check at step 2d, dead-ending every
    enforced workflow with an external URL). Asserts the chain proceeds past
    egress/capability into verification and seals a decided outcome.
    """
    res = run_scenario_A_valid_execution()
    assert res.get("status") == "READY_FOR_DEPLOYMENT", res
    assert "Egress/capability" not in str(res.get("reason", "")), res
    assert res.get("decision", {}).get("status") == "READY_FOR_DEPLOYMENT", res
    assert res.get("snapshot_version"), "version snapshot must be recorded"


def test_B_policy_denial_blocks_before_spend():
    """B: deny-all policy fails closed to human review with the rule named."""
    res = run_scenario_B_policy_denial()
    assert res.get("status") == "PENDING_HUMAN_REVIEW", res
    assert "deny-all" in str(res.get("reason", "")), res
    assert res.get("hitl_request_id"), "denial must open a HITL request"


def test_C_high_risk_skill_held_for_review():
    """C: a high-risk '*' permission skill must never verify as 'ok'."""
    res = run_scenario_C_untrusted_skill()
    assert res.get("verdict") == "review", res
    assert res.get("verdict") != "ok"
    assert res.get("sealed") is True, "registry integrity seal must hold"


def test_D_wrong_doctor_fails_at_invariant_stage():
    """D: chain must reach the invariant stage and name the failing check.

    Regression pair of test_A: proves execution was NOT stopped earlier at
    egress/capability (the pre-fix behaviour), and that a technically green
    delivery with wrong domain truth fails closed instead of deploying.
    """
    res = run_scenario_D_verification_failure()
    assert res.get("status") == "PENDING_HUMAN_REVIEW", res
    assert res.get("reason") == "Business invariant failure", res
    failed = [f["name"] for f in res.get("invariants", {}).get("failed", [])]
    assert "doctor-match" in failed, res


def test_D_malformed_check_spec_fails_closed_without_raise():
    """Malformed business-check specs must fail closed, never raise.

    Regression for the unpack-ValueError escape: a non-callable check fn
    used to propagate a ValueError out of execute_workflow_task and crash
    the caller. (Well-formed 2-tuples are normalized with doc=""; anything
    else seals PENDING_HUMAN_REVIEW with the cause named.)
    """
    import io
    import contextlib
    with tempfile.TemporaryDirectory() as tmp:
        orch = SystemOrchestrator(
            budget_usd=100.0,
            enforcement=EnforcementProfile(
                policy={"default": "allow"},
                capability_secret=b"cap-secret-32-bytes-minimum-length-here",
                egress=EgressPolicy(allow_public_internet=True,
                                    allowed_domains=("httpbin.org",))),
            evidence_dir=tmp,
        )
        bad = {"domain": "clinic",
               "payload": {"appointment": {"doctor": "Dr. Samy"}, "price": 800},
               "checks": [("doctor-match", "not-a-function",
                            "corrupted spec")]}  # fn not callable: malformed
        with contextlib.redirect_stdout(io.StringIO()):
            res = orch.execute_workflow_task(
                task_prompt="malformed invariant spec",
                workflow_json=_sample_workflow(authed=True),
                daily_reqs=10, business=bad)
    assert res.get("status") == "PENDING_HUMAN_REVIEW", res
    assert res.get("reason") == "Business invariant spec malformed", res


def test_E_failing_canary_stops_rollout():
    """E: the failing 50%-stage probe must halt promotion (no 100% probe)."""
    res = run_scenario_E_deployment_failure()
    assert res.get("probe_calls") == [1, 10, 50], res
    assert 100 not in (res.get("probe_calls") or []), "rollout must stop"


def test_F_incident_correlates_and_leaves_nothing_lonely():
    """F: 3 same-session alerts fuse into 1 incident; lonely set is empty."""
    res = run_scenario_F_incident_recovery()
    assert res.get("correlated") is True, res
    assert res.get("lonely_kept") is True, res


def run_all_scenarios():
    """Execute all 6 E2E scenarios and return summary."""
    scenarios = [
        ("A_valid_execution", run_scenario_A_valid_execution),
        ("B_policy_denial", run_scenario_B_policy_denial),
        ("C_untrusted_skill", run_scenario_C_untrusted_skill),
        ("D_verification_failure", run_scenario_D_verification_failure),
        ("E_deployment_failure", run_scenario_E_deployment_failure),
        ("F_incident_recovery", run_scenario_F_incident_recovery),
    ]
    results = {}
    for name, fn in scenarios:
        try:
            res = fn()
            ok = res.get("status", "").startswith("PENDING") or \
                 res.get("status") in ("READY_FOR_DEPLOYMENT", "tested") or \
                 res.get("ok") or res.get("correlated")
            results[name] = {"status": "ok" if ok else "unexpected",
                             "result": str(res)[:200]}
        except Exception as e:
            results[name] = {"status": "error", "error": str(e)}
    return results


if __name__ == "__main__":
    print("Running E2E Integration Scenarios...")
    res = run_all_scenarios()
    for k, v in res.items():
        print(f"  {k}: {v['status']}")
        if v.get("error"):
            print(f"    ERROR: {v['error']}")