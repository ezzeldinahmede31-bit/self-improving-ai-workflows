"""Tests for the open-source tool gateway (tool_gateway.py) + its wiring into
the orchestrator. All external tools are mocked — these tests never require
Docker images, running containers, or network access."""

import json

import pytest

from tool_gateway import (ToolGateway, ToolStatus, LiteLLMFailover, PrismMock,
                          SemgrepSAST, NucleiScan, GarakLLMScan)
from master_system_orchestrator import SystemOrchestrator


class _FakeCtx:
    """Explodes if `.status()` actually touches docker/socket on the real host."""
    def __init__(self, overrides=None):
        self.overrides = overrides or {}

    def status(self, refresh=False):
        s = ToolStatus()
        for k in s.__dataclass_fields__:
            setattr(s, k, self.overrides.get(k, False))
        return s

    def enabled(self, tool):
        return self.overrides.get(tool, False)


class TestCapabilityProbe:
    def test_status_shows_all_down_in_clean_env(self, monkeypatch):
        gw = ToolGateway()

        def fake_tcp(*a, **k):
            return False

        monkeypatch.setattr("tool_gateway._tcp_open", fake_tcp)
        monkeypatch.setattr("tool_gateway._http_get", lambda *a, **k: None)
        monkeypatch.setattr(ToolGateway, "_image_present", staticmethod(lambda i: False))
        monkeypatch.setattr(ToolGateway, "_python_module", staticmethod(lambda m: False))

        st = gw.status(refresh=True)
        for k in st.__dataclass_fields__:
            assert getattr(st, k) is False

    def test_probe_reflected_from_overrides(self):
        gw = ToolGateway()
        gw._cache = _FakeCtx({"litellm": True, "prism": True}).status()
        assert gw.enabled("litellm") is True
        assert gw.enabled("qdrant") is False


class TestLiteLLMFailover:
    def test_rejects_budget_ceiling_429(self, monkeypatch):
        import urllib.error

        def fake_urlopen(*a, **k):
            raise urllib.error.HTTPError(
                url="http://127.0.0.1:4000/chat/completions",
                code=429, msg="rate limited", hdrs={}, fp=None)

        monkeypatch.setattr("tool_gateway.urllib.request.urlopen", fake_urlopen)
        lf = LiteLLMFailover(base_url="http://127.0.0.1:4000", budget_usd=3.0)
        res = lf.complete([{"role": "user", "content": "hi"}])
        assert res.ok is False
        assert res.reason == "budget_ceiling"

    def test_serves_success_model(self, monkeypatch):
        class FakeResp:
            status = 200

            def __enter__(self):
                return self

            def __exit__(self, *a):
                return False

            def read(self):
                return b'{"model": "deepseek-chat", "choices": []}'

        def fake_urlopen(req, timeout=5):
            return FakeResp()

        monkeypatch.setattr("tool_gateway.urllib.request.urlopen", fake_urlopen)
        lf = LiteLLMFailover(base_url="http://127.0.0.1:4000")
        res = lf.complete([{"role": "user", "content": "hi"}])
        assert res.ok is True
        assert res.model_used == "deepseek-chat"

    def test_unreachable_when_proxy_down(self, monkeypatch):
        def fake_open(*a, **k):
            raise OSError("conn refused")

        monkeypatch.setattr("tool_gateway.urllib.request.urlopen", fake_open)
        lf = LiteLLMFailover()
        res = lf.complete([{"role": "user", "content": "x"}])
        assert res.ok is False
        assert res.reason.startswith("unreachable")


class TestPrismMock:
    def test_resolve_external_url_to_mock(self):
        pm = PrismMock(base_url="http://127.0.0.1:4010")
        u = pm.resolve("https://api.example.com/v2/users?q=1")
        assert u == "http://127.0.0.1:4010/v2/users?q=1"

    def test_healthy_requires_probe(self):
        pm = PrismMock()
        assert pm.healthy(_FakeCtx()) is False
        assert pm.healthy(_FakeCtx({"prism": True})) is True


class TestScannersWithoutImages:
    def test_semgrep_skips_when_image_absent(self):
        s = SemgrepSAST()
        res = s.run("/tmp/nonesuch", gw=_FakeCtx())
        assert res["ran"] is False
        assert "not present" in res["reason"]

    def test_nuclei_skips_when_image_absent(self):
        n = NucleiScan()
        res = n.run("https://127.0.0.1:9191", gw=_FakeCtx())
        assert res["ran"] is False
        assert "not present" in res["reason"]

    def test_garak_skips_when_module_missing(self):
        g = GarakLLMScan()
        res = g.run(gw=_FakeCtx())
        assert res["ran"] is False

    def test_semgrep_parses_findings_when_present(self, monkeypatch):
        class FakeProc:
            returncode = 0
            stdout = json.dumps({"results": [{"path": "/src/n.py",
                                              "rule_id": "bandit.B104"}]})
            stderr = ""

        monkeypatch.setattr("subprocess.run", lambda *a, **k: FakeProc())
        s = SemgrepSAST()
        res = s.run("/src", gw=_FakeCtx({"semgrep": True}))
        assert res["ran"] is True
        assert len(res["findings"]) == 1
        assert res["findings"][0]["rule_id"] == "bandit.B104"

    def test_nuclei_parses_jsonl_hits(self, monkeypatch):
        class FakeProc:
            returncode = 0
            stdout = '{"info":{"name":"xss"},"matched-at":"/a"}\n'
            stderr = ""

        monkeypatch.setattr("subprocess.run", lambda *a, **k: FakeProc())
        n = NucleiScan()
        res = n.run("http://127.0.0.1:9191/a", gw=_FakeCtx({"nuclei": True}))
        assert res["ran"] is True
        assert res["hits"][0]["info"]["name"] == "xss"


# ---------------------------------------------------------------------------
# Orchestrator integration: tool report surfaces on deploy-ready, pipeline
# stays deterministic when every tool is down.
# ---------------------------------------------------------------------------

class TestOrchestratorTools:
    def setup_method(self):
        self.orch = SystemOrchestrator(
            budget_usd=20.0, elide_output=True, tools_host="127.0.0.1")

    @staticmethod
    def _valid_flow():
        return {"nodes": [
            {"name": "Receive Webhook", "type": "n8n-nodes-base.webhook",
             "parameters": {"path": "v1-orders", "httpMethod": "POST",
                            "authentication": "headerAuth",
                            "pinnedData": {"1": {"json": {"order": {"id": 1}}}}},
             "continueOnFail": True},
            {"name": "Send Supabase", "type": "n8n-nodes-base.httpRequest",
             "parameters": {"url": "https://api.example.com/v1/orders"},
             "continueOnFail": True},
        ], "connections": {"Receive Webhook": {"main": [{"node": "Send Supabase"}]}}}

    def test_deploy_ready_includes_tools_report(self, monkeypatch):
        self.orch.tools.status = lambda refresh=False: _FakeCtx(
            {"litellm": True, "prism": True}).status()
        res = self.orch.execute_workflow_task(
            "orders ingest", self._valid_flow(),
            daily_reqs=500, tech_stack=["supabase", "deepseek"])
        assert res["status"] == "READY_FOR_DEPLOYMENT"
        assert "tools" in res
        assert "litellm" in res["tools"]["active_tools"]

    def test_all_tools_down_still_deploys(self, monkeypatch):
        self.orch.tools.status = lambda refresh=False: _FakeCtx().status()
        res = self.orch.execute_workflow_task(
            "orders ingest", self._valid_flow(),
            daily_reqs=500, tech_stack=["supabase", "deepseek"])
        assert res["status"] == "READY_FOR_DEPLOYMENT"
        assert res["tools"]["active_tools"] == []