import pytest
import json
import os
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from remote_api import (
    MockRouter,
    RemoteAPIClient,
    EgressBlockedError,
    health_summary,
    TELEMETRY_DB_PATH,
)
from mock_server import MockAPIServer
from remote_api_adapter import RemoteAPIAdapter, RemoteNodeSpec
from quirks_memory import remember_quirk, query_quirks, render_as_prompt, QUIRKS_DB_PATH
from local_routing import HybridRouter, ExecLocale


@pytest.fixture
def mock_server():
    server = MockAPIServer(port=9191, scenarios={
        "/v1/users": {"status": 200, "body": {"users": [{"id": 1, "name": "Mock"}]}},
        "/v1/limited": {"status": 429, "headers": {"Retry-After": "0"}},
        "/v1/unauthorized": {"status": 401, "body": {"error": "invalid_token"}},
        "/v1/error": {"status": 503, "body": {"error": "unavailable"}},
    })
    server.start()
    yield server
    server.stop()


@pytest.fixture
def telemetry_db(monkeypatch, tmp_path):
    monkeypatch.setattr("remote_api.TELEMETRY_DB_PATH", tmp_path / "telemetry.db")
    from remote_api import init_telemetry_db
    init_telemetry_db()


class TestMockRouter:
    def test_route_to_mock(self):
        router = MockRouter({"api.example.com": "http://127.0.0.1:9191"})
        url = router.resolve("https://api.example.com/v1/users?x=1")
        assert url == "http://127.0.0.1:9191/v1/users?x=1"

    def test_no_mapping_keeps_url(self):
        router = MockRouter({})
        url = "https://example.org/x"
        assert router.resolve(url) == url

    def test_subdomain_matches_mock(self):
        router = MockRouter({"example.com": "http://127.0.0.1:9191"})
        assert router.resolve("https://api.example.com/x").startswith("http://127.0.0.1:9191")

    def test_block_sensitive_without_mock(self):
        router = MockRouter({})
        with pytest.raises(EgressBlockedError):
            router.assert_safe("https://api.stripe.com/v1/charges")

    def test_block_subdomain_sensitive(self):
        router = MockRouter({})
        with pytest.raises(EgressBlockedError):
            router.assert_safe("https://api.supabase.co/rest/v1")

    def test_mock_unblocks_sensitive(self):
        router = MockRouter({"api.stripe.com": "http://127.0.0.1:9191"})
        router.assert_safe("https://api.stripe.com/v1/charges")  # no raise


class TestRemoteAPIClient:
    def test_mocked_success(self, mock_server, telemetry_db):
        router = MockRouter({"api.example.com": "http://127.0.0.1:9191"})
        client = RemoteAPIClient(router=router, max_retries=2, base_backoff_seconds=0.01)
        result = client.request("GET", "https://api.example.com/v1/users")
        assert result["status"] == 200
        assert result["mock"] is True
        assert result["body"]["users"][0]["name"] == "Mock"

    def test_429_retries_with_backoff(self, mock_server, telemetry_db):
        sleeps = []
        router = MockRouter({"api.example.com": "http://127.0.0.1:9191"})
        client = RemoteAPIClient(router=router, max_retries=3,
                                 base_backoff_seconds=0.001, sleep=sleeps.append)
        result = client.request("GET", "https://api.example.com/v1/limited")
        # 429 with Retry-After 0 → we retry but mock keeps returning 429 until max
        assert result["status"] == 429
        assert len(sleeps) >= 1  # did backoff

    def test_401_not_retried(self, mock_server, telemetry_db):
        router = MockRouter({"api.example.com": "http://127.0.0.1:9191"})
        client = RemoteAPIClient(router=router, max_retries=3,
                                 base_backoff_seconds=0.001, sleep=lambda s: None)
        result = client.request("GET", "https://api.example.com/v1/unauthorized")
        assert result["status"] == 401
        assert result.get("retries", 0) == 0  # 401 is not retryable

    def test_503_retried(self, mock_server, telemetry_db):
        router = MockRouter({"api.example.com": "http://127.0.0.1:9191"})
        client = RemoteAPIClient(router=router, max_retries=3,
                                 base_backoff_seconds=0.001, sleep=lambda s: None)
        result = client.request("GET", "https://api.example.com/v1/error")
        assert result["status"] == 503


class TestTelemetry:
    def test_health_summary_groups_by_service(self, mock_server, telemetry_db):
        router = MockRouter({"api.example.com": "http://127.0.0.1:9191"})
        client = RemoteAPIClient(router=router, max_retries=1, base_backoff_seconds=0.001,
                                 sleep=lambda s: None)
        client.request("GET", "https://api.example.com/v1/users")
        summary = health_summary()
        assert any(s["service"] == "api.example.com" for s in summary)
        service = next(s for s in summary if s["service"] == "api.example.com")
        assert service["calls"] >= 1
        assert service["avg_ms"] >= 0


class TestRemoteAPIAdapter:
    def test_parse_curl_post(self):
        adapter = RemoteAPIAdapter()
        spec = adapter.from_curl(
            "curl -X POST 'https://api.stripe.com/v1/charges' "
            "-H 'Authorization: Bearer sk_test_x' "
            "-H 'Content-Type: application/x-www-form-urlencoded' "
            "-d 'amount=2000&currency=usd'"
        )
        assert spec.method == "POST"
        assert spec.auth_type == "bearer"
        assert spec.url.endswith("/charges")
        assert spec.body == {"amount": "2000", "currency": "usd"}

    def test_parse_curl_get(self):
        adapter = RemoteAPIAdapter()
        spec = adapter.from_curl(
            "curl 'https://api.github.com/repos/n8n-io/n8n' -H 'Accept: application/vnd.github+json'"
        )
        assert spec.method == "GET"
        assert "github" in spec.url

    def test_node_json_has_credentials_placeholder(self):
        adapter = RemoteAPIAdapter()
        spec = adapter.from_curl(
            "curl -X GET 'https://api.x.com/v1' -H 'Authorization: Bearer key'"
        )
        node = spec.to_n8n_node(credential_id="", credential_name="")
        assert node["type"] == "n8n-nodes-base.httpRequest"
        assert "credentials" in node

    def test_openapi_extraction(self):
        adapter = RemoteAPIAdapter()
        doc = {
            "openapi": "3.0.0",
            "info": {"title": "Petstore"},
            "servers": [{"url": "https://petstore.example.com/api"}],
            "paths": {
                "/pets": {
                    "get": {
                        "parameters": [{"name": "X-API-Key", "in": "header"}],
                        "responses": {"200": {}},
                    }
                }
            },
        }
        spec = adapter.from_openapi(doc, "/pets", "get")
        assert spec.method == "GET"
        assert spec.url == "https://petstore.example.com/api/pets"


class TestQuirksMemory:
    def test_remember_and_recall(self, tmp_path, monkeypatch):
        monkeypatch.setattr("quirks_memory.QUIRKS_DB_PATH", tmp_path / "q.db")
        from quirks_memory import init_quirks_db
        init_quirks_db()
        remember_quirk("telegram", "messages longer than 4096 chars rejected",
                       "chunk into <= 4096 parts", ["4096", "telegram"])
        results = query_quirks("telegram", "long message")
        assert results and results[0]["service"] == "telegram"
        assert "chunk" in results[0]["fix"]

    def test_render_prompt_fragment(self, tmp_path, monkeypatch):
        monkeypatch.setattr("quirks_memory.QUIRKS_DB_PATH", tmp_path / "q.db")
        from quirks_memory import init_quirks_db
        init_quirks_db()
        remember_quirk("stripe", "idempotency required", "send Idempotency-Key", ["idempotency"])
        prompt = render_as_prompt("stripe", "retry create charge")
        assert "Known quirks" in prompt
        assert "Idempotency-Key" in prompt

    def test_no_quirk_empty_prompt(self, tmp_path, monkeypatch):
        monkeypatch.setattr("quirks_memory.QUIRKS_DB_PATH", tmp_path / "q.db")
        from quirks_memory import init_quirks_db
        init_quirks_db()
        assert render_as_prompt("never-seen-service") == ""


class TestHybridRouter:
    def test_deterministic_local(self):
        router = HybridRouter()
        d = router.route("run AST security scan on workflow")
        assert d.locale == ExecLocale.LOCAL
        assert d.cloud_allowed is False

    def test_security_always_human_gate(self):
        router = HybridRouter()
        d = router.route("analyze firewall", security_sensitive=True)
        assert d.locale == ExecLocale.LOCAL
        assert d.needs_human is True

    def test_reasoning_to_cloud_when_capable(self):
        router = HybridRouter(local_model_configured=False, cloud_capable=True)
        d = router.route("design a fanout topology for 4 SaaS providers")
        assert d.locale == ExecLocale.CLOUD_REASONING

    def test_reasoning_local_model_preferred(self):
        router = HybridRouter(local_model_configured=True)
        d = router.route("design a fanout topology")
        assert d.locale == ExecLocale.LOCAL_MODEL

    def test_reasoning_fallback_local(self):
        router = HybridRouter(local_model_configured=False, cloud_capable=False)
        d = router.route("why is this architecture failing")
        assert d.locale == ExecLocale.LOCAL


if __name__ == "__main__":
    pytest.main([__file__, "-v"])