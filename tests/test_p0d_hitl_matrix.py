"""HITL decision matrix: replay / forged / expired / tenant / actor /
duplicate / cross-request isolation.

Shared-secret semantics are by design (operator secret = fully trusted
human); everything else is fail-closed and tested.
"""
import os
import sys
import tempfile
from datetime import datetime, timedelta, timezone

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from hitl_gate import HITLGate, HITLState

TOKEN = "operator-secret-token"


def _gate(tmp_path):
    return HITLGate(db_path=str(tmp_path / "h.db"), security_token=TOKEN,
                    timeout_minutes=15)


def test_forged_token_rejected(tmp_path):
    g = _gate(tmp_path)
    req = g.create_pending("op", 60, ["v"])
    assert g.approve(req.request_id, "forged")["status"] == "INVALID_TOKEN"
    assert g.get(req.request_id).state == HITLState.PENDING


def test_replay_duplicate_approval_inert(tmp_path):
    g = _gate(tmp_path)
    req = g.create_pending("op", 60, ["v"])
    first = g.approve(req.request_id, TOKEN)
    assert first["status"] == HITLState.APPROVED
    again = g.approve(req.request_id, TOKEN)
    assert again["status"] == HITLState.APPROVED  # no flip, no error
    assert g.get(req.request_id).state == HITLState.APPROVED


def test_reject_after_approve_inert(tmp_path):
    g = _gate(tmp_path)
    req = g.create_pending("op", 60, ["v"])
    g.approve(req.request_id, TOKEN)
    res = g.reject(req.request_id, "too late")
    assert res["status"] == HITLState.APPROVED
    assert g.get(req.request_id).state == HITLState.APPROVED


def test_approval_after_expiry_denied_without_sweeper(tmp_path):
    g = _gate(tmp_path)
    req = g.create_pending("op", 60, ["v"])
    # age the request past expiry directly in the store (no sweeper run)
    past = (datetime.now(timezone.utc) - timedelta(minutes=1)).isoformat()
    with g._connect() as conn:
        conn.execute("UPDATE pending_approvals SET expires_at = ? "
                     "WHERE request_id = ?", (past, req.request_id))
        conn.commit()
    res = g.approve(req.request_id, TOKEN)
    assert res["status"] == HITLState.EXPIRED
    assert g.get(req.request_id).state == HITLState.EXPIRED


def test_malformed_expiry_fail_closed(tmp_path):
    g = _gate(tmp_path)
    req = g.create_pending("op", 60, ["v"])
    with g._connect() as conn:
        conn.execute("UPDATE pending_approvals SET expires_at = ? "
                     "WHERE request_id = ?", ("not-a-timestamp",
                                              req.request_id))
        conn.commit()
    res = g.approve(req.request_id, TOKEN)
    assert res["status"] == HITLState.EXPIRED


def test_wrong_tenant_refused_when_declared(tmp_path):
    g = _gate(tmp_path)
    req = g.create_pending("op", 60, ["v"], payload={"tenant": "A"})
    res = g.approve(req.request_id, TOKEN, tenant="B")
    assert res["status"] == "WRONG_TENANT"
    assert g.get(req.request_id).state == HITLState.PENDING
    ok = g.approve(req.request_id, TOKEN, tenant="A")
    assert ok["status"] == HITLState.APPROVED


def test_undeclared_tenant_allows_approval(tmp_path):
    g = _gate(tmp_path)
    req = g.create_pending("op", 60, ["v"], payload={"n": 1})
    assert g.approve(req.request_id, TOKEN)["status"] == HITLState.APPROVED


def test_actor_recorded_not_token(tmp_path):
    g = _gate(tmp_path)
    req = g.create_pending("op", 60, ["v"])
    g.approve(req.request_id, TOKEN, actor="ezz")
    got = g.get(req.request_id)
    assert "ezz" in (got.decision_reason or "")
    assert TOKEN not in (got.decision_reason or "")
    assert got.token_hash is not None and TOKEN not in got.token_hash


def test_cross_request_isolation(tmp_path):
    g = _gate(tmp_path)
    a = g.create_pending("op-a", 60, ["v"])
    b = g.create_pending("op-b", 60, ["v"])
    g.approve(a.request_id, TOKEN)
    assert g.get(b.request_id).state == HITLState.PENDING
    g.reject(b.request_id, "no")
    assert g.get(a.request_id).state == HITLState.APPROVED


def test_unknown_request_not_found(tmp_path):
    g = _gate(tmp_path)
    assert g.approve("nope", TOKEN)["status"] == "NOT_FOUND"
    assert g.reject("nope")["status"] == "NOT_FOUND"
