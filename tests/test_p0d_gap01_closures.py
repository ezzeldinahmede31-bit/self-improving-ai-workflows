"""GAP-01 closures: every production-reachable DIRECT path is now
pinned, gated, or proven non-production.

- ToolGateway / LiteLLMFailover: loopback-only by default (fail-closed).
- PythonExecutor.execute: fail-closed by default; helpers are direct code
  (no f-string codegen -> no filepath/pattern injection into exec).
- N8NIntegration strict mode: mandatory egress at construction, mandatory
  per-task capability per call; orchestrator wires strict in production.
- HITL telegram: POST body (no GET query-string secret exposure).
"""
import sys
import os
import tempfile

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tool_gateway import ToolGateway, LiteLLMFailover
from tiered_pipeline import PythonExecutor, TieredPipeline
from n8n_integration import N8NIntegration, N8NConfig
from egress_firewall import EgressPolicy


# ---- ToolGateway loopback pin ----

def test_gateway_rejects_non_loopback_host():
    with pytest.raises(ValueError):
        ToolGateway(host="169.254.169.254")
    with pytest.raises(ValueError):
        ToolGateway(host="api.telegram.org")
    with pytest.raises(ValueError):
        ToolGateway(host="10.0.0.1")
    # Smuggling shapes: suffix/prefix tricks are NOT loopback.
    for tricky in ("127.0.0.1.evil.com", "evil-127.0.0.1.com", "localhost.",
                   "LOCALHOST.evil.com", "[::1]"):
        with pytest.raises(ValueError):
            ToolGateway(host=tricky)


def test_gateway_accepts_loopback_and_opt_in():
    assert ToolGateway(host="127.0.0.1").host == "127.0.0.1"
    assert ToolGateway(host="::1").host == "::1"
    gw = ToolGateway(host="10.0.0.1", allow_non_loopback=True)
    assert gw.host == "10.0.0.1"


def test_gateway_rejects_bad_ports():
    with pytest.raises(ValueError):
        ToolGateway(ports={"litellm": 99999})
    with pytest.raises(ValueError):
        ToolGateway(ports={"litellm": "4000"})


def test_litellm_failover_rejects_non_loopback():
    with pytest.raises(ValueError):
        LiteLLMFailover(base_url="https://integrate.api.nvidia.com/v1")
    ok = LiteLLMFailover(base_url="http://127.0.0.1:4000")
    assert ok.base_url == "http://127.0.0.1:4000"


# ---- PythonExecutor fail-closed ----

def test_executor_execute_disabled_by_default():
    with pytest.raises(RuntimeError):
        PythonExecutor().execute("x = 1")


def test_executor_opt_in_still_executes():
    res = PythonExecutor(allow_arbitrary_exec=True).execute("y = 41 + 1")
    assert res["success"] and res["locals"]["y"] == 42


def test_pipeline_custom_code_refused_by_default():
    pipe = TieredPipeline()
    out = pipe.process("compute something", {"code": "__import__('os').system('id')"})
    assert "error" in out.output and "disabled" in out.output["error"]


def test_filepath_injection_cannot_reach_exec(tmp_path):
    """A hostile filepath must be treated as a literal path, never code."""
    evil = str(tmp_path / "x'); import os; os.system('id'); print('")
    pipe = TieredPipeline()
    res = pipe.executor.analyze_logs(evil, "ERROR'); print('pwn")
    assert "error" in res  # literal open() fails -> error dict, no exec
    assert res["error"] != ""


def test_helpers_still_compute_directly(tmp_path):
    log = tmp_path / "app.log"
    log.write_text("INFO ok\nERROR boom\nWARN slow\n")
    pipe = TieredPipeline()
    res = pipe.executor.analyze_logs(str(log), "ERROR")
    assert res["total_lines"] == 3 and res["matches"] == 1
    res2 = pipe.executor.compute_resources(
        [{"base_ram_mb": 512, "base_cpu_percent": 20}], 1.5)
    assert res2["estimated_peak_ram_mb"] == 768.0
    # Malformed shapes fail as data errors, never exceptions, never exec.
    assert "error" in pipe.executor.compute_resources(["nope"], 1.0)
    assert "error" in pipe.executor.compute_resources(
        [{"base_ram_mb": object()}], 1.0)
    assert "error" in pipe.executor.analyze_logs(str(log), "x" * 201)
    assert "error" in pipe.executor.analyze_logs("y" * 1025, None)


# ---- Capability max-TTL cap (generator GAP-02) ----

def test_capability_ttl_capped_fail_closed():
    from capability import CapabilityIssuer, MAX_TTL_S
    iss = CapabilityIssuer(b"y" * 32)
    with pytest.raises(ValueError):
        iss.issue(actions=["net.fetch"], ttl_s=MAX_TTL_S + 1)
    with pytest.raises(ValueError):
        iss.issue(actions=["net.fetch"], ttl_s=10 ** 9)
    tok = iss.issue(actions=["net.fetch"], ttl_s=MAX_TTL_S)
    ok, _ = iss.verify(tok, action="net.fetch", resource="x")
    assert ok is True


# ---- N8N strict mode ----

def _cfg():
    return N8NConfig(base_url="http://127.0.0.1:5678", api_key="k",
                     webhook_base="http://127.0.0.1:5678")


def test_strict_requires_egress_at_construction():
    with pytest.raises(RuntimeError):
        N8NIntegration(_cfg(), strict=True)


def test_strict_requires_capability_per_call(monkeypatch):
    import n8n_integration as _ni
    from egress_firewall import EgressVerdict
    monkeypatch.setattr(
        _ni, "_check_url",
        lambda url, policy: EgressVerdict(True, "ok", ("93.184.216.34",)))
    n8n = N8NIntegration(
        _cfg(),
        egress_policy=EgressPolicy(allow_public_internet=True,
                                   allowed_ports=(80, 443, 5678)),
        strict=True)
    with pytest.raises(RuntimeError, match="capability"):
        n8n._fetch_workflow("abc")
    with pytest.raises(RuntimeError, match="capability"):
        n8n._trigger_via_webhook("path", {})


def test_non_strict_legacy_shape_unchanged():
    n8n = N8NIntegration(_cfg())  # no gates, no strict: no raise on gate
    assert n8n.strict is False
    # calls fail only on network (returns None/False), never on gates
    assert n8n._fetch_workflow("nope") is None


def test_orchestrator_wires_strict_in_production():
    import platform_wiring
    from master_system_orchestrator import SystemOrchestrator
    with tempfile.TemporaryDirectory() as tmp:
        orch = SystemOrchestrator(
            budget_usd=5.0,
            enforcement=platform_wiring.EnforcementProfile(
                egress=platform_wiring.EgressPolicy(
                    allow_public_internet=True),
            ),
            evidence_dir=tmp,
            elide_output=True,
        )
        assert orch.n8n.strict is True
        assert orch.n8n.egress_policy is not None


def test_orchestrator_legacy_stays_non_strict():
    from master_system_orchestrator import SystemOrchestrator
    with tempfile.TemporaryDirectory() as tmp:
        orch = SystemOrchestrator(budget_usd=5.0, enforcement=None,
                                  evidence_dir=tmp, elide_output=True)
        assert orch.n8n.strict is False


# ---- HITL telegram uses POST ----

def test_hitl_notify_uses_post_not_get(monkeypatch):
    import hitl_gate
    from hitl_gate import HITLGate
    seen = {}

    class _Resp:
        def __enter__(self): return self
        def __exit__(self, *a): return False
        def read(self): return b"ok"

    def fake_urlopen(req, timeout=10):
        seen["method"] = req.get_method()
        seen["url"] = req.full_url
        seen["has_body"] = req.data is not None
        return _Resp()

    monkeypatch.setattr(hitl_gate.urllib.request, "urlopen", fake_urlopen)
    gate = HITLGate(security_token="t" * 32)
    handler = gate.notify_telegram("BOT", "CHAT")
    from hitl_gate import HITLRequest
    handler(HITLRequest(request_id="r1", raw_input="x", risk_score=10,
                        violations=["v"]))
    assert seen["method"] == "POST"
    assert "?" not in seen["url"], "payload must not ride the query string"
    assert seen["has_body"] is True
