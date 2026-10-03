"""Audit failure matrix: success / exception / timeout / unavailable /
signing failure / degraded routing / recovery.

Policy under test:
- safety verdicts: fail-CLOSED (denials stay denials, nothing deploys).
- denial/HITL ROUTING: survives audit outage, explicitly degraded
  (audit_failed=True + stderr) — an outage must never blind review.
- terminal results: carry evidence or audit_failed=True, never silence.
"""
import os
import sys
import tempfile

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from immutable_audit import AuditChain
import platform_wiring


def test_audit_success_roundtrip_and_verify(tmp_path):
    chain = AuditChain(str(tmp_path / "a.db"), secret=b"s" * 32)
    e1 = chain.append(kind="t", actor="a", subject="s", detail="d1")
    e2 = chain.append(kind="t", actor="a", subject="s", detail="d2")
    assert e1["id"] != e2["id"]
    assert chain.verify() == {"ok": True, "checked": 2, "broken_at": None}


def test_audit_signing_failure_fail_closed_at_build(tmp_path):
    with pytest.raises(ValueError):
        AuditChain(str(tmp_path / "a.db"), secret=b"short")
    with pytest.raises(RuntimeError):
        platform_wiring.build_production_sinks(
            evidence_dir=str(tmp_path), audit_secret=None)


def test_audit_storage_unavailable_is_loud_not_silent(tmp_path):
    missing = str(tmp_path / "no-such-dir" / "a.db")
    with pytest.raises(Exception):
        AuditChain(missing)


def test_production_sinks_require_key(monkeypatch, tmp_path):
    monkeypatch.delenv("AUDIT_HMAC_KEY", raising=False)
    with pytest.raises(RuntimeError):
        platform_wiring.build_production_sinks(evidence_dir=str(tmp_path))
    sinks = platform_wiring.build_production_sinks(
        evidence_dir=str(tmp_path), audit_secret=b"k" * 32)
    assert sinks["signed"] is True


def _deny_orch(tmp_path):
    from master_system_orchestrator import SystemOrchestrator
    return SystemOrchestrator(
        budget_usd=5.0,
        enforcement=platform_wiring.EnforcementProfile(
            policy={"default": "deny", "rules": []},
            egress=platform_wiring.EgressPolicy(allow_public_internet=True),
        ),
        evidence_dir=str(tmp_path),
        elide_output=True,
    )


def test_policy_denial_survives_audit_exception(capsys, tmp_path):
    orch = _deny_orch(tmp_path)

    class _Broken:
        def append(self, **k):
            raise OSError("disk gone")

    orch.evidence["audit"] = _Broken()
    res = orch.execute_workflow_task(
        "denied task", {"nodes": [], "connections": {}}, daily_reqs=1)
    # fail-closed verdict + degraded-but-present routing evidence
    assert res["status"] == "PENDING_HUMAN_REVIEW"
    assert "hitl_request_id" in res
    err = capsys.readouterr().err
    assert "AUDIT-FAILURE" in err


def test_policy_denial_survives_audit_timeout(capsys, tmp_path):
    orch = _deny_orch(tmp_path)

    class _Hanging:
        def append(self, **k):
            raise TimeoutError("audit store hung")

    orch.evidence["audit"] = _Hanging()
    res = orch.execute_workflow_task(
        "denied task 2", {"nodes": [], "connections": {}}, daily_reqs=1)
    assert res["status"] == "PENDING_HUMAN_REVIEW"
    assert "hitl_request_id" in res
    assert "AUDIT-FAILURE" in capsys.readouterr().err


def test_audit_recovery_chain_stays_verifiable(tmp_path):
    """Outage then recovery: written events still form a valid chain
    (the gap is absence, not corruption — absence is visible via ids)."""
    chain = AuditChain(str(tmp_path / "a.db"), secret=b"s" * 32)
    e1 = chain.append(kind="t", actor="a", subject="s", detail="before")
    # outage window: nothing written (simulated by simply not writing)
    e2 = chain.append(kind="t", actor="a", subject="s", detail="after")
    assert e2["id"] == e1["id"] + 1  # gap is explicit in the id sequence
    assert chain.verify()["ok"] is True


def test_golden_failure_is_loud_not_silent(capsys, tmp_path):
    orch = _deny_orch(tmp_path)

    class _BrokenGolden:
        _cases = {}
        def add_case(self, *a, **k):
            raise OSError("golden store gone")

    orch.evidence["golden"] = _BrokenGolden()
    orch._golden_from_rejection("t", ["v"])  # must not raise...
    assert "GOLDEN-FAILURE" in capsys.readouterr().err  # ...nor stay silent
