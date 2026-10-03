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
from egress_firewall import EgressPolicy, check_host


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

    def fake_pinned(url, policy, method="GET", data=None, headers=None,
                    timeout_s=30, **kw):
        return {"status": 200, "body": b"{}", "url": url, "redirects": 0}

    # gate layer forced open so the CAPABILITY refusal is what fires;
    # transport pinned-open so nothing real is touched.
    monkeypatch.setattr(
        _ni, "_check_url",
        lambda url, policy: EgressVerdict(True, "ok", ("93.184.216.34",)))
    monkeypatch.setattr(_ni, "_fetch_pinned", fake_pinned)
    n8n = N8NIntegration(
        _cfg(),
        egress_policy=EgressPolicy(allow_public_internet=True,
                                   allowed_ports=(80, 443, 5678)),
        strict=True)
    # transport pinned-open, but no task capability -> loud refusal
    with pytest.raises(RuntimeError, match="capability"):
        n8n._fetch_workflow("abc")
    with pytest.raises(RuntimeError, match="capability"):
        n8n._trigger_via_webhook("path", {})


def test_strict_egress_block_raises_loud(monkeypatch):
    import n8n_integration as _ni

    def fake_pinned(url, policy, method="GET", data=None, headers=None,
                    timeout_s=30, **kw):
        raise AssertionError("pinned transport must not run after refusal")

    monkeypatch.setattr(_ni, "_fetch_pinned", fake_pinned)
    # 127.0.0.1 is loopback: real gate refuses BEFORE any socket opens.
    n8n = N8NIntegration(
        _cfg(), egress_policy=EgressPolicy(allow_public_internet=True),
        strict=True)
    with pytest.raises(RuntimeError, match="Egress blocked"):
        n8n._fetch_workflow("abc")


def test_pinned_json_shapes_preserved(monkeypatch):
    import json as _json
    import n8n_integration as _ni
    from egress_firewall import EgressPolicy as _EP

    calls = {}

    def fake_pinned(url, policy, method="GET", data=None, headers=None,
                    timeout_s=30, **kw):
        calls["method"] = method
        calls["api_key"] = (headers or {}).get("X-N8N-API-KEY")
        calls["ct"] = (headers or {}).get("Content-Type")
        if method == "POST":
            assert _json.loads(data.decode()) == {"a": 1}
            return {"status": 202, "body": b"{}", "url": url, "redirects": 0}
        return {"status": 200,
                "body": _json.dumps({"data": [{"id": "e9"}]}).encode(),
                "url": url, "redirects": 0}

    monkeypatch.setattr(_ni, "_fetch_pinned", fake_pinned)
    n8n = N8NIntegration(
        _cfg(),
        egress_policy=_EP(allow_public_internet=True,
                          allowed_ports=(80, 443, 5678),
                          allowed_domains=("127.0.0.1",)),
        capability_issuer=None, capability_token=None)
    # NOTE: loopback gate refuses under the real firewall; force the gate
    # open here to assert transport SHAPES only (parsing, headers, verbs).
    from egress_firewall import EgressVerdict as _V
    monkeypatch.setattr(
        _ni, "_check_url", lambda url, policy: _V(True, "ok", ("127.0.0.1",)))
    assert n8n._latest_execution_id("wf") == "e9"
    assert n8n._trigger_via_webhook("p", {"a": 1}) is True
    assert calls == {"method": "POST", "api_key": "k",
                     "ct": "application/json"}


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


# ---- HITL telegram uses pinned POST ----

def test_hitl_notify_uses_post_not_get(monkeypatch):
    import hitl_gate
    from hitl_gate import HITLGate
    seen = {}

    def fake_fetch(url, policy, method="GET", data=None, headers=None,
                   timeout_s=10, **kw):
        seen["method"] = method
        seen["url"] = url
        seen["has_body"] = data is not None
        seen["policy"] = policy
        return {"status": 200, "body": b"ok", "url": url, "redirects": 0}

    monkeypatch.setattr(hitl_gate, "_fetch_pinned", fake_fetch)
    gate = HITLGate(security_token="t" * 32)
    handler = gate.notify_telegram("BOTSECRET", "CHAT")
    from hitl_gate import HITLRequest
    handler(HITLRequest(request_id="r1", raw_input="x", risk_score=10,
                        violations=["v"]))
    assert seen["method"] == "POST"
    assert "?" not in seen["url"], "payload must not ride the query string"
    assert seen["has_body"] is True
    assert seen["policy"] is not None, "pinned transport always gated"


def test_hitl_notify_blocked_stays_silent_and_auditable(monkeypatch, capsys):
    import hitl_gate
    from hitl_gate import HITLGate
    from egress_firewall import PinnedFetchBlocked

    def fake_blocked(*a, **k):
        raise PinnedFetchBlocked("boundary check denied: private")

    monkeypatch.setattr(hitl_gate, "_fetch_pinned", fake_blocked)
    gate = HITLGate(security_token="t" * 32)
    handler = gate.notify_telegram("SUPERSECRETBOT", "CHAT")
    from hitl_gate import HITLRequest
    handler(HITLRequest(request_id="r2", raw_input="x", risk_score=10,
                        violations=["v"]))  # must not raise
    err = capsys.readouterr().err
    assert "egress blocked" in err
    assert "SUPERSECRETBOT" not in err, "bot token must never reach logs"


# ---- check_host + named loopback allowance ----

def test_check_host_blocks_private_and_metadata():
    p = EgressPolicy(allow_public_internet=True)
    for bad, port in (("10.0.0.5", 443), ("127.0.0.1", 443),
                      ("169.254.169.254", 80), ("::1", 443),
                      ("192.168.1.1", 443)):
        v = check_host(bad, port, p, resolve=lambda h: [bad])
        assert v.allowed is False, bad


def test_check_host_port_screening():
    p = EgressPolicy(allow_public_internet=True)
    v = check_host("93.184.216.34", 22, p, resolve=lambda h: ["93.184.216.34"])
    assert v.allowed is False and "port" in v.reason


def test_named_loopback_allowance_is_exact_only():
    p = EgressPolicy(allow_public_internet=True,
                     allow_loopback_hosts=("localhost",))
    ok = check_host("localhost", 443, EgressPolicy(
        allow_public_internet=True, allowed_ports=(80, 443, 5678),
        allow_loopback_hosts=("localhost",)),
        resolve=lambda h: ["127.0.0.1"])
    assert ok.allowed is True
    # suffix lookalike: NOT allowed
    evil = check_host("localhost.evil.com", 443, p,
                      resolve=lambda h: ["127.0.0.1"])
    assert evil.allowed is False
    # numeric smuggling of loopback under a named allowance: NOT allowed
    num = check_host("2130706433", 443, p, resolve=lambda h: ["127.0.0.1"])
    assert num.allowed is False
    # unnamed loopback literal: NOT allowed
    lit = check_host("127.0.0.1", 443, p, resolve=lambda h: ["127.0.0.1"])
    assert lit.allowed is False


# ---- VaultBackend pinned transport ----

def test_vault_blocked_addr_returns_none(monkeypatch):
    import egress_firewall as _ef
    from secrets_provider import VaultBackend
    monkeypatch.setattr(_ef, "fetch_pinned", lambda *a, **k: (_ for _ in ()).throw(
        _ef.PinnedFetchBlocked("boundary denied")))
    vb = VaultBackend(addr="http://127.0.0.1:8200", token="t")
    assert vb.get("k") is None  # fail-closed, no exception


def test_vault_sends_token_in_header_not_url(monkeypatch):
    import egress_firewall as _ef
    from secrets_provider import VaultBackend
    seen = {}

    def fake_fetch(url, policy, method="GET", data=None, headers=None,
                   timeout_s=3, **kw):
        seen["url"] = url
        seen["headers"] = headers or {}
        assert method == "GET"
        return {"status": 200,
                "body": b'{"data": {"data": {"K": "v"}}}',
                "url": url, "redirects": 0}

    monkeypatch.setattr(_ef, "fetch_pinned", fake_fetch)
    vb = VaultBackend(addr="https://vault.example", token="SUPERSECRET",
                      egress_policy=EgressPolicy(allow_public_internet=True))
    assert vb.get("K") == "v"
    assert "SUPERSECRET" not in seen["url"]
    assert seen["headers"].get("X-Vault-Token") == "SUPERSECRET"


def test_vault_non200_returns_none(monkeypatch):
    import egress_firewall as _ef
    from secrets_provider import VaultBackend
    monkeypatch.setattr(_ef, "fetch_pinned", lambda *a, **k: {
        "status": 403, "body": b"{}", "url": "", "redirects": 0})
    vb = VaultBackend(addr="https://vault.example", token="t",
                      egress_policy=EgressPolicy(allow_public_internet=True))
    assert vb.get("K") is None


# ---- DependencyHealth egress gate ----

def test_dependency_probe_blocks_private_with_policy():
    from health_probes import DependencyHealth
    d = DependencyHealth(egress_policy=EgressPolicy(allow_public_internet=True))
    d.add("evil", "10.9.9.9", 443)
    res = d.probe("evil")
    assert res["up"] is False and "egress blocked" in res["reason"]


def test_dependency_probe_unchanged_without_policy():
    from health_probes import DependencyHealth
    d = DependencyHealth(timeout_s=0.2)
    d.add("closed", "127.0.0.1", 1)  # nothing listens: refused, not blocked
    res = d.probe("closed")
    assert res["up"] is False and "egress blocked" not in res["reason"]


# ---- research license check pinned ----

def test_verify_license_bad_shapes_no_network(monkeypatch):
    from orchestrator import research as R
    monkeypatch.setattr(R, "fetch_pinned", lambda *a, **k: (_ for _ in ()).throw(
        AssertionError("network must not fire")))
    assert R.verify_license_live("http://evil/x") is None
    assert R.verify_license_live("https://github.com/a/b/c") is None
    assert R.verify_license_live("https://github.com/owner") is None


def test_verify_license_uses_pinned_transport(monkeypatch):
    from orchestrator import research as R
    seen = {}

    def fake_fetch(url, policy, method="GET", data=None, headers=None,
                   timeout_s=20, **kw):
        seen["url"] = url
        seen["policy"] = policy
        assert url == "https://api.github.com/repos/o/r"
        return {"status": 200,
                "body": b'{"license": {"spdx_id": "MIT"}}',
                "url": url, "redirects": 0}

    monkeypatch.setattr(R, "fetch_pinned", fake_fetch)
    assert R.verify_license_live("https://github.com/o/r") == "MIT"
    assert seen["policy"].allowed_domains == ("api.github.com",)


# ---- remote_api target validation ----

def test_remote_mock_target_must_be_loopback_literal():
    from remote_api import MockRouter, RemoteAPIClient
    import urllib.request as _u
    fin = {"body": b"{}", "status": 200, "headers": {}}

    class _Resp:
        def __init__(self, *a, **k): pass
        def __enter__(self): return self
        def __exit__(self, *a): return False
        def read(self): return b"{}"
        status = 200
        headers = {}

    import remote_api as _ra
    orig = _u.urlopen
    _ra.urllib.request.urlopen = lambda *a, **k: _Resp()
    try:
        c = RemoteAPIClient(router=MockRouter(
            {"api.example.com": "http://127.0.0.1:9191"}))
        out = c.request("GET", "https://api.example.com/v1")
        assert out["mock"] is True
        evil = RemoteAPIClient(router=MockRouter(
            {"api.example.com": "http://10.9.9.9:9191"}))
        try:
            evil.request("GET", "https://api.example.com/v1")
            raised = False
        except Exception:
            raised = True
        assert raised, "non-loopback mock target must be refused"
        dns = RemoteAPIClient(router=MockRouter(
            {"api.example.com": "http://mock.internal:9191"}))
        try:
            dns.request("GET", "https://api.example.com/v1")
            raised2 = False
        except Exception:
            raised2 = True
        assert raised2, "DNS-name mock target must be refused"
    finally:
        _ra.urllib.request.urlopen = orig


# ---- trigger_and_verify failure shapes (mutation anchor) ----

def test_trigger_no_key_is_error_not_ok(monkeypatch):
    import n8n_integration as _ni
    monkeypatch.delenv("N8N_API_KEY", raising=False)
    n8n = N8NIntegration(N8NConfig(base_url="http://127.0.0.1:5678",
                                  api_key=""))
    res = n8n.trigger_and_verify("wf", "p", {}, {"a": 1})
    assert res["ok"] is False and res["status"] == "error"


def test_trigger_flat_failure_shape(monkeypatch):
    import n8n_integration as _ni
    n8n = N8NIntegration(N8NConfig(base_url="http://127.0.0.1:5678",
                                  api_key="k"))
    # past the existence check, trigger ok, but no execution appears
    monkeypatch.setattr(n8n, "_fetch_workflow", lambda wf: {"id": wf})
    monkeypatch.setattr(n8n, "_trigger_via_webhook", lambda p, b: True)
    monkeypatch.setattr(n8n, "_latest_execution_id", lambda wf: None)
    # legacy non-strict, transport fails everywhere -> flat, never ok
    res = n8n.trigger_and_verify("wf", "p", {}, {"a": 1},
                                 required_passes=1, max_attempts=2)
    assert res["ok"] is False and res["status"] == "flat"
    assert res["consecutive"] == 0
