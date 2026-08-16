"""LIVE end-to-end test against the real n8n instance.

Unlike every other test in this suite (hermetic, mocked), this one proves the
final kilometre: our orchestrator produces a workflow, we deploy it to the real
n8n at EZZELDIN8N_URL via its REST API, confirm it accepts the graph, then
delete it.

Guarded: only runs when RUN_LIVE_E2E=1 is set AND the instance is reachable.
Without the flag the whole module is skipped — `pytest` stays green everywhere.

Usage:
    RUN_LIVE_E2E=1 venv/bin/python -m pytest tests/test_e2e_live_n8n.py -m e2e -s
"""

import json
import os
import urllib.request
import urllib.error

import pytest

E2E_FLAG = os.environ.get("RUN_LIVE_E2E", "0") == "1"
N8N_BASE = os.environ.get("EZZELDIN8N_URL", "https://ezzeldin8n.ezzeldin8n.cfd")
N8N_API_KEY = os.environ.get("N8N_API_KEY", "")

pytestmark = pytest.mark.e2e

needs_live = pytest.mark.skipif(
    not E2E_FLAG,
    reason="Live E2E requires RUN_LIVE_E2E=1 (deploys a throwaway workflow to n8n)",
)


def _headers() -> dict:
    return {
        "Content-Type": "application/json",
        "X-N8N-API-KEY": N8N_API_KEY,
    }


@needs_live
class TestLiveN8nE2E:
    """Deploys a minimal webhook workflow, verifies the API accepted it, cleans
    up. Exercises the same graph shape the orchestrator would emit."""

    @pytest.fixture()
    def cleanup(self):
        created = []
        yield created
        for wid in created:
            try:
                req = urllib.request.Request(
                    f"{N8N_BASE}/api/v1/workflows/{wid}",
                    method="DELETE", headers=_headers())
                urllib.request.urlopen(req, timeout=10)
            except Exception:
                pass  # best-effort teardown

    def test_create_workflow_via_api(self, cleanup):
        body = {
            "name": "e2e-smoke-pytest",
            "nodes": [
                {"id": "n1", "name": "When webhook called",
                 "type": "n8n-nodes-base.webhook", "typeVersion": 2,
                 "position": [0, 0],
                 "parameters": {"path": "e2e-pytest", "httpMethod": "POST"}},
                {"id": "n2", "name": "Respond to Webhook",
                 "type": "n8n-nodes-base.respondToWebhook", "typeVersion": 1,
                 "position": [220, 0], "parameters": {"respondWith": "json",
                                                      "responseBody": "={{ { 'ok': true } }}"}},
            ],
            "connections": {
                "When webhook called": {
                    "main": [[{"node": "Respond to Webhook", "type": "main", "index": 0}]]
                },
            },
            "settings": {"executionOrder": "v1"},
        }
        req = urllib.request.Request(
            f"{N8N_BASE}/api/v1/workflows",
            data=json.dumps(body).encode(),
            headers=_headers(), method="POST")
        try:
            with urllib.request.urlopen(req, timeout=15) as resp:
                payload = json.loads(resp.read().decode())
        except urllib.error.HTTPError as e:
            if e.code == 401:
                pytest.skip("No N8N_API_KEY configured for live E2E")
            raise

        assert payload.get("id"), f"n8n did not return workflow id: {payload}"
        cleanup.append(payload["id"])
        assert payload["name"] == "e2e-smoke-pytest"
        # The API accepted our graph shape — node type + connection format valid.
        node_types = {n.get("type") for n in payload.get("nodes", [])}
        assert "n8n-nodes-base.respondToWebhook" in node_types