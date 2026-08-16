import pytest
import json
import os
import sys
import tempfile
from datetime import datetime, timedelta, timezone
import sqlite3

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from hitl_gate import (
    HITLGate,
    HITLState,
    HITLRequest,
    ApprovalWithheldError,
    _hash_token,
)
from verifier_engine import VerifierEngine


@pytest.fixture
def db_path():
    f = tempfile.NamedTemporaryFile(suffix='.db', delete=False)
    path = f.name
    f.close()
    yield path
    if os.path.exists(path):
        os.unlink(path)


@pytest.fixture
def gate(db_path):
    return HITLGate(db_path=db_path, timeout_minutes=15, security_token='test-token-123')


class TestHITLStateMachine:
    def test_create_pending(self, gate):
        req = gate.create_pending('risky docker op', 65, ['privileged container'], {'id': 1})
        assert req.state == HITLState.PENDING
        assert req.risk_score == 65
        assert req.request_id is not None
        assert len(req.request_id) == 16

    def test_pending_persisted_in_db(self, gate):
        req = gate.create_pending('op', 50, ['x'])
        loaded = gate.get(req.request_id)
        assert loaded is not None
        assert loaded.state == HITLState.PENDING
        assert loaded.violations == ['x']

    def test_approve_with_correct_token(self, gate):
        req = gate.create_pending('op', 60, ['y'])
        result = gate.approve(req.request_id, 'test-token-123')
        assert result['status'] == HITLState.APPROVED
        loaded = gate.get(req.request_id)
        assert loaded.state == HITLState.APPROVED
        assert loaded.token_hash == _hash_token('test-token-123')

    def test_approve_with_wrong_token_denied(self, gate):
        req = gate.create_pending('op', 60, ['y'])
        result = gate.approve(req.request_id, 'wrong-token')
        assert result['status'] == 'INVALID_TOKEN'
        loaded = gate.get(req.request_id)
        assert loaded.state == HITLState.PENDING  # still pending

    def test_approve_without_configured_token_fails(self, db_path):
        gate = HITLGate(db_path=db_path, timeout_minutes=15, security_token=None)
        req = gate.create_pending('op', 60, [])
        result = gate.approve(req.request_id, 'anything')
        assert result['status'] == 'INVALID_TOKEN'

    def test_reject(self, gate):
        req = gate.create_pending('op', 70, [])
        result = gate.reject(req.request_id, 'looks bad')
        assert result['status'] == HITLState.REJECTED
        loaded = gate.get(req.request_id)
        assert loaded.state == HITLState.REJECTED
        assert loaded.decision_reason == 'looks bad'

    def test_cannot_approve_twice(self, gate):
        req = gate.create_pending('op', 65, [])
        gate.approve(req.request_id, 'test-token-123')
        result = gate.approve(req.request_id, 'test-token-123')
        assert result['status'] == HITLState.APPROVED  # already approved, idempotent read

    def test_reject_nonexistent(self, gate):
        result = gate.reject('nope')
        assert result['status'] == 'NOT_FOUND'

    def test_approve_nonexistent(self, gate):
        result = gate.approve('nope', 'test-token-123')
        assert result['status'] == 'NOT_FOUND'


class TestHITLTimeout:
    def test_default_deny_on_expiry(self, gate, db_path):
        # Manually plant an already-expired pending row
        conn = sqlite3.connect(db_path)
        conn.execute(
            "INSERT INTO pending_approvals (request_id, raw_input, risk_score, "
            "violations, payload, state, created_at, expires_at, decided_at, "
            "decision_reason, token_hash) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            ('expired', 'op', 99, '[]', None, HITLState.PENDING,
             (datetime.now(timezone.utc) - timedelta(minutes=30)).isoformat(),
             (datetime.now(timezone.utc) - timedelta(minutes=5)).isoformat(),
             None, '', None),
        )
        conn.commit()
        conn.close()

        expired = gate.sweep_expired()
        assert 'expired' in expired
        loaded = gate.get('expired')
        assert loaded.state == HITLState.EXPIRED
        assert loaded.decision_reason == 'timeout_default_deny'

    def test_no_expiry_within_timeout(self, gate, db_path):
        req = gate.create_pending('op', 50, [])
        expired = gate.sweep_expired()
        assert req.request_id not in expired
        assert gate.get(req.request_id).state == HITLState.PENDING

    def test_short_timeout_expires(self, db_path):
        gate = HITLGate(db_path=db_path, timeout_minutes=0, security_token='t')
        req = gate.create_pending('op', 55, [])
        expired = gate.sweep_expired()
        assert req.request_id in expired


class TestHITLNotification:
    def test_cli_notify_called(self, gate, capsys):
        req = gate.create_pending('roman op', 80, ['banned pattern'])
        out = capsys.readouterr().out
        assert req.request_id in out
        assert '80' in out
        assert 'banned pattern' in out

    def test_custom_handler_receives_request(self, db_path):
        received = []

        def handler(req):
            received.append(req)

        gate = HITLGate(db_path=db_path, security_token='t', notify_handler=handler)
        req = gate.create_pending('op', 44, [])
        assert received and received[0].request_id == req.request_id

    def test_token_from_env(self, db_path, monkeypatch):
        monkeypatch.setenv('HITL_SECURITY_TOKEN', 'env-token')
        gate = HITLGate(db_path=db_path, security_token=None, env_token=None)
        assert gate.security_token == 'env-token'


class TestHITLVerifierIntegration:
    def test_security_risk_routes_to_pending(self, db_path):
        gate = HITLGate(db_path=db_path, security_token='tok')
        engine = VerifierEngine(hitl_gate=gate)
        flow = {
            "nodes": [{"type": "n8n-nodes-base.code",
                       "parameters": {"jsCode": "require('child_process').exec('id')"}}],
        }
        result = engine.verify_and_route(flow)
        assert result['status'] == 'PENDING_HUMAN_REVIEW'
        assert result['can_retry'] is False
        assert 'hitl_request_id' in result
        assert gate.get(result['hitl_request_id']).state == HITLState.PENDING

    def test_clean_flow_does_not_route_to_hitl(self, db_path):
        gate = HITLGate(db_path=db_path, security_token='tok')
        engine = VerifierEngine(hitl_gate=gate)
        flow = {
            "nodes": [
                {"name": "Receive Webhook", "type": "n8n-nodes-base.webhook",
                 "parameters": {"path": "x", "pinnedData": {}, "authentication": "headerAuth"}},
                {"name": "Send Response", "type": "n8n-nodes-base.httpRequest",
                 "parameters": {"url": "https://api.example.com"}},
            ],
            "connections": {"Receive Webhook": {"main": [{"node": "Send Response"}]}},
        }
        result = engine.verify_and_route(flow)
        assert result['status'] == 'READY_FOR_DEPLOYMENT'

    def test_reject_and_expired_abort(self, db_path):
        gate = HITLGate(db_path=db_path, security_token='tok')
        engine = VerifierEngine(hitl_gate=gate)
        flow = {
            "nodes": [{"type": "n8n-nodes-base.code",
                       "parameters": {"jsCode": "eval(payload)"}}],
        }
        result = engine.verify_and_route(flow)
        rid = result['hitl_request_id']
        gate.reject(rid, 'no way')
        assert gate.get(rid).state == HITLState.REJECTED

    def test_full_hitl_lifecycle(self, db_path):
        gate = HITLGate(db_path=db_path, security_token='tok')
        engine = VerifierEngine(hitl_gate=gate)
        flow = {
            "nodes": [{"type": "n8n-nodes-base.code",
                       "parameters": {"jsCode": "eval('2+2')"}}],
        }
        result = engine.verify_and_route(flow)
        assert result['status'] == 'PENDING_HUMAN_REVIEW'
        rid = result['hitl_request_id']
        # approve with correct token
        res = gate.approve(rid, 'tok')
        assert res['status'] == HITLState.APPROVED
        # reject flow after approval should be blocked (already decided)
        res2 = gate.reject(rid, 'too late')
        assert res2['status'] == HITLState.APPROVED  # cannot change after approval


if __name__ == "__main__":
    pytest.main([__file__, "-v"])