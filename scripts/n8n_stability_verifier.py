#!/usr/bin/env python3
"""Stability verifier — runs a deployed n8n workflow on the LIVE instance and
demands REQUIRED_CONSECUTIVE_PASSES back-to-back executions whose output
exactly matches the expected output defined at design time.

Called from build_gates_pipeline.py AFTER QUALITY + INTEGRITY pass and BEFORE
HITL. Any single mismatch resets the consecutive counter (strict rule); after
MAX_TOTAL_ATTEMPTS the workflow is rejected. The result distinguishes a
FLAT_FAILURE (failed from the very first attempt — deterministic bug) from a
FLAKY failure (reached N consecutive successes then regressed — intermittent
bug), so the final report separates the two classes.

Config comes from the environment (N8N_BASE_URL, N8N_API_KEY) — never
hardcoded. Read via os.environ with a .env fallback next to this module.

Usage (standalone):
    venv/bin/python -c "from scripts.n8n_stability_verifier import verify_stability; ..."
"""

from __future__ import annotations

import hashlib
import json
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlsplit

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from egress_firewall import (EgressPolicy, fetch_pinned, PinnedFetchBlocked)

REQUIRED_CONSECUTIVE_PASSES = 5
MAX_TOTAL_ATTEMPTS = 15
TIMEOUT_PER_EXECUTION = 30
ROOT = Path(__file__).resolve().parent.parent
ERROR_LOG_PATH = ROOT / "memory" / "n8n_error_patterns.md"


class _HttpTimeout(Exception):
    """Pinned transport timed out (maps to the old requests Timeout path)."""


class _HttpConnectionError(Exception):
    """Pinned transport unreachable/refused (maps to the old requests
    ConnectionError path, including firewall refusals)."""


class _PinnedResp:
    """Minimal response shape (status_code / json() / text) over bytes."""

    def __init__(self, status: int, body: bytes):
        self.status_code = int(status)
        self._body = body or b""

    def json(self):
        return json.loads(self._body.decode("utf-8"))

    @property
    def text(self) -> str:
        return self._body.decode("utf-8", "replace")


def _gate_policy_for(base_url: str) -> EgressPolicy:
    """Pin gate traffic to the OPERATOR-configured n8n host:port.

    The base URL comes from N8N_BASE_URL env (operator config, never
    workflow input). The policy allow-lists exactly that host — including
    an explicit loopback allowance when the operator points at their own
    local instance — plus its port. Anything else (redirects included) is
    re-validated per hop by fetch_pinned.
    """
    parts = urlsplit(base_url or "")
    host = (parts.hostname or "localhost").lower().rstrip(".")
    try:
        port = parts.port
    except ValueError:
        port = None
    ports = {80, 443, 5678}
    if port:
        ports.add(port)
    import ipaddress as _ip
    loop: tuple[str, ...] = ()
    try:
        if _ip.ip_address(host).is_loopback:
            loop = (host,)
    except ValueError:
        if host == "localhost":
            loop = ("localhost",)
    return EgressPolicy(allow_public_internet=True,
                        allowed_domains=(host,),
                        allowed_ports=tuple(sorted(ports)),
                        allow_loopback_hosts=loop)


def _http_get(url: str, headers: dict | None = None,
              timeout: int = TIMEOUT_PER_EXECUTION) -> _PinnedResp:
    """Pinned GET against the configured n8n host. Raises _HttpTimeout /
    _HttpConnectionError (never returns a forgery)."""
    policy = _gate_policy_for(N8N_BASE_URL)
    try:
        out = fetch_pinned(url, policy, method="GET",
                           headers=headers or {}, timeout_s=timeout)
    except PinnedFetchBlocked as e:
        raise _HttpConnectionError(f"egress refused: {e}")
    except TimeoutError as e:
        raise _HttpTimeout(str(e))
    except OSError as e:
        raise _HttpConnectionError(str(e))
    return _PinnedResp(out.get("status", 0), out.get("body", b""))


def _http_post(url: str, headers: dict | None = None,
               payload: dict | None = None,
               timeout: int = TIMEOUT_PER_EXECUTION) -> _PinnedResp:
    """Pinned POST against the configured n8n host. Same error contract."""
    policy = _gate_policy_for(N8N_BASE_URL)
    try:
        out = fetch_pinned(url, policy, method="POST",
                           data=json.dumps(payload or {}).encode(),
                           headers={"Content-Type": "application/json",
                                    **(headers or {})},
                           timeout_s=timeout)
    except PinnedFetchBlocked as e:
        raise _HttpConnectionError(f"egress refused: {e}")
    except TimeoutError as e:
        raise _HttpTimeout(str(e))
    except OSError as e:
        raise _HttpConnectionError(str(e))
    return _PinnedResp(out.get("status", 0), out.get("body", b""))


def _env_or_dotenv(name: str, default: str = "") -> str:
    """Environment first, then a `KEY=value` .env file next to this module, then
    the project-root .env (where the real secrets live)."""
    val = os.environ.get(name)
    if val:
        return val
    for env_path in (Path(__file__).resolve().parent / ".env",
                     ROOT / ".env"):
        if env_path.exists():
            for line in env_path.read_text(encoding="utf-8").splitlines():
                line = line.strip()
                if line.startswith(name + "="):
                    return line.split("=", 1)[1].strip()
    return default


N8N_BASE_URL = _env_or_dotenv("N8N_BASE_URL", "http://localhost:5678")
N8N_API_KEY = _env_or_dotenv("N8N_API_KEY", "")


class StabilityResult:
    def __init__(self, status: str, attempts_log: list, consecutive_reached: int,
                 max_consecutive_reached: int, pattern: str):
        self.status = status                      # STABLE_VERIFIED | UNSTABLE_REJECTED
        self.attempts_log = attempts_log
        self.consecutive_reached = consecutive_reached
        self.max_consecutive_reached = max_consecutive_reached
        self.pattern = pattern                    # STABLE | FLAT_FAILURE | FLAKY

    def to_dict(self) -> dict:
        return {
            "status": self.status,
            "pattern": self.pattern,
            "consecutive_reached": self.consecutive_reached,
            "max_consecutive_reached": self.max_consecutive_reached,
            "attempts_log": self.attempts_log,
        }


def get_execution_method(workflow_json: dict) -> str:
    """Decides how a workflow can be run for real: 'webhook' if it exposes a
    webhook/form/chat trigger node, otherwise 'cli' (requires shell access to
    the n8n host, e.g. `n8n execute --id=<id>` for Manual/Schedule triggers)."""
    for node in workflow_json.get("nodes", []):
        ntype = (node.get("type") or "").lower()
        if "webhook" in ntype or ntype.endswith((".formtrigger", ".chattrigger")):
            return "webhook"
    return "cli"


def fetch_workflow(workflow_id: str, base_url: str | None = None,
                   api_key: str | None = None) -> dict:
    """GET /api/v1/workflows/{id} — the public-API read that works on any n8n
    deployment. Used to discover the webhook trigger when triggering by
    workflow id. Returns {} on any failure (caller handles it)."""
    base_url = base_url or N8N_BASE_URL
    api_key = api_key if api_key is not None else N8N_API_KEY
    if not api_key:
        return {}
    try:
        resp = _http_get(f"{base_url}/api/v1/workflows/{workflow_id}",
                         headers={"X-N8N-API-KEY": api_key},
                         timeout=TIMEOUT_PER_EXECUTION)
        if resp.status_code == 200:
            return resp.json()
    except (_HttpTimeout, _HttpConnectionError):
        pass
    return {}


def _webhook_trigger_path(workflow_json: dict) -> tuple[str | None, str]:
    """Returns (webhook_path, http_method) of the first webhook trigger node."""
    for node in workflow_json.get("nodes", []):
        ntype = node.get("type", "")
        if "webhook" in ntype:
            return (node.get("parameters", {}).get("path"),
                    node.get("parameters", {}).get("httpMethod", "POST"))
    return None, "POST"


def _execution_output(exec_data: dict) -> list | None:
    """Extract the last node's output from an n8n 2.x execution payload. The
    public API returns runData = {nodeName: [{data: {main: [[{json: ...}]]}}]},
    so the actual items live at data.main[0][*].json — resultData.runData alone
    is just a metadata shell. Returns a list of {json: ...} items for the last
    executed node, or None if nothing usable is present."""
    data = exec_data.get("data") or {}
    run_data = (data.get("resultData") or {}).get("runData") or {}
    if not run_data:
        return None
    last_node = (data.get("resultData") or {}).get("lastNodeExecuted")
    target = last_node if last_node in run_data else list(run_data)[-1]
    entries = run_data.get(target) or []
    items: list = []
    for entry in entries:
        main = ((entry.get("data") or {}).get("main") or [])
        for branch in main:
            for item in branch:
                if isinstance(item, dict) and "json" in item:
                    items.append(item["json"])
    return items if items else None


def _latest_execution_id(workflow_id: str, base_url: str, api_key: str):
    """Latest execution id for a workflow via GET /api/v1/executions?workflowId=
    (the public-API read used to verify a webhook run actually completed)."""
    try:
        resp = _http_get(
            f"{base_url}/api/v1/executions?workflowId={workflow_id}&limit=1",
            headers={"X-N8N-API-KEY": api_key}, timeout=TIMEOUT_PER_EXECUTION)
        if resp.status_code == 200:
            items = resp.json().get("data", [])
            if items:
                return items[0].get("id")
    except (_HttpTimeout, _HttpConnectionError):
        pass
    return None


def _fetch_execution(execution_id: int, base_url: str, api_key: str) -> dict:
    """Full execution payload via GET /api/v1/executions/{id} (includeData=true
    is required for the public API to return resultData/runData)."""
    try:
        resp = _http_get(f"{base_url}/api/v1/executions/{execution_id}?includeData=true",
                         headers={"X-N8N-API-KEY": api_key},
                         timeout=TIMEOUT_PER_EXECUTION)
        if resp.status_code == 200:
            return resp.json()
    except (_HttpTimeout, _HttpConnectionError):
        pass
    return {}


def _trigger_via_webhook(workflow_id: str, test_input: dict, base_url: str,
                         api_key: str, webhook_path: str | None = None) -> dict:
    """Webhook path (the ONLY public-API execution route on a self-hosted n8n):
    POST the test input to the workflow's webhook URL, then verify the run via
    GET /api/v1/executions — the webhook response can return BEFORE the run
    finishes, so we poll for a NEW finished execution."""
    start = time.time()
    if not webhook_path:
        wf = fetch_workflow(workflow_id, base_url, api_key)
        webhook_path, _method = _webhook_trigger_path(wf)
        if not webhook_path:
            return {"success": False,
                    "reason": "No webhook trigger node with a path found in the "
                              "workflow — cannot trigger via webhook (use CLI for "
                              "Manual/Schedule-triggered workflows)",
                    "node_failed": None, "duration_sec": time.time() - start}

    before = _latest_execution_id(workflow_id, base_url, api_key)
    url = f"{base_url.rstrip('/')}/webhook/{webhook_path.lstrip('/')}"
    try:
        resp = _http_post(url, payload=test_input, timeout=TIMEOUT_PER_EXECUTION)
    except _HttpTimeout:
        return {"success": False, "reason": f"Timed out after {TIMEOUT_PER_EXECUTION}s "
                "(webhook POST)", "node_failed": None,
                "duration_sec": TIMEOUT_PER_EXECUTION}
    except _HttpConnectionError as e:
        return {"success": False, "reason": f"Cannot reach n8n webhook: {e}",
                "node_failed": None, "duration_sec": 0}
    if resp.status_code not in (200, 201, 202):
        return {"success": False,
                "reason": f"Webhook HTTP {resp.status_code}: {resp.text[:300]}",
                "node_failed": None, "duration_sec": time.time() - start}

    deadline = start + TIMEOUT_PER_EXECUTION
    while time.time() < deadline:
        latest = _latest_execution_id(workflow_id, base_url, api_key)
        if latest is not None and latest != before:
            exec_data = _fetch_execution(latest, base_url, api_key)
            if exec_data:
                if exec_data.get("finished"):
                    return {"success": True,
                            "output": _execution_output(exec_data),
                            "execution_id": latest,
                            "duration_sec": time.time() - start}
                if exec_data.get("status") in ("error", "crashed", "failed"):
                    data = exec_data.get("data") or {}
                    err = (data.get("resultData") or {}).get("error") or {}
                    return {"success": False,
                            "reason": f"Execution {latest} failed: "
                                      f"{err.get('message', 'unknown')}",
                            "node_failed": (err.get("node") or {}).get("name"),
                            "execution_id": latest,
                            "duration_sec": time.time() - start}
        time.sleep(1)
    return {"success": False,
            "reason": "Webhook accepted but no finished execution was observed "
                      "within the timeout (check the workflow is ACTIVE)",
            "node_failed": None, "duration_sec": deadline - start}


def trigger_workflow_execution(workflow_id: str, test_input: dict,
                               base_url: str | None = None,
                               api_key: str | None = None,
                               method: str | None = None,
                               webhook_path: str | None = None) -> dict:
    """Runs the workflow for real on the n8n instance and returns the raw
    execution result — never a mock, never pinned data.

    method=None -> legacy REST path (POST /api/v1/workflows/{id}/execute, which
    most self-hosted deployments do NOT expose — kept for compatibility).
    method='webhook' -> POST to the workflow's webhook URL then verify via the
    executions endpoint (works on any deployment that has a webhook trigger).
    method='cli' -> requires shell access to the n8n host (`n8n execute --id`);
    not callable from inside the gate, returns an explicit reason."""
    base_url = base_url or N8N_BASE_URL
    api_key = api_key if api_key is not None else N8N_API_KEY
    if not api_key:
        return {"success": False, "reason": "N8N_API_KEY not configured "
                "(set it in .env or the environment)", "duration_sec": 0}
    if method == "webhook":
        return _trigger_via_webhook(workflow_id, test_input, base_url, api_key,
                                    webhook_path)
    if method == "cli":
        return {"success": False,
                "reason": "CLI execution (n8n execute --id) requires shell access "
                          "to the n8n host — not available from the gate; run "
                          "`n8n execute --id=<workflow_id>` manually instead",
                "node_failed": None, "duration_sec": 0}
    url = f"{base_url}/api/v1/workflows/{workflow_id}/execute"
    headers = {"X-N8N-API-KEY": api_key}
    start = time.time()
    try:
        resp = _http_post(url, headers=headers, payload={"data": test_input},
                          timeout=TIMEOUT_PER_EXECUTION)
        duration = time.time() - start
        if resp.status_code != 200:
            return {"success": False,
                    "reason": f"HTTP {resp.status_code}: {resp.text[:300]}",
                    "node_failed": None,
                    "duration_sec": duration}
        execution_data = resp.json()
        data = execution_data.get("data", {})
        exec_error = (data.get("resultData") or {}).get("error")
        if exec_error:
            return {
                "success": False,
                "reason": f"Execution error: {exec_error.get('message', 'unknown')}",
                "node_failed": (exec_error.get("node") or {}).get("name"),
                "duration_sec": duration,
            }
        if not data.get("finished"):
            return {"success": False, "reason": "Execution did not finish (timeout/hung)",
                    "duration_sec": duration}
        return {"success": True,
                "output": (data.get("resultData") or {}).get("runData"),
                "duration_sec": duration}
    except _HttpTimeout:
        return {"success": False, "reason": f"Timed out after {TIMEOUT_PER_EXECUTION}s",
                "node_failed": None, "duration_sec": TIMEOUT_PER_EXECUTION}
    except _HttpConnectionError as e:
        return {"success": False, "reason": f"Cannot reach n8n instance: {e}",
                "node_failed": None, "duration_sec": 0}


def compare_with_expected(actual_output, expected_output) -> bool:
    """Exact structural match against the output defined at design time. If no
    expected output was defined this FAILS by design — a workflow whose output
    was never specified cannot be declared stable."""
    if expected_output is None:
        return False
    return json.dumps(actual_output, sort_keys=True) == json.dumps(expected_output, sort_keys=True)


def log_attempt(workflow_id: str, attempt_num: int, consecutive_count: int, result: dict):
    """Appends every FAILED attempt to the human-readable error-pattern log so
    fixed-vs-flaky bugs are distinguishable from the history."""
    if result.get("success"):
        return
    try:
        ERROR_LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
        with ERROR_LOG_PATH.open("a", encoding="utf-8") as f:
            f.write(
                f"\n- [{datetime.now(timezone.utc).isoformat()}] workflow={workflow_id} "
                f"attempt={attempt_num} consecutive_before_fail={consecutive_count} "
                f"reason={result.get('reason')} node={result.get('node_failed', 'N/A')}\n"
            )
    except OSError:
        pass


def verify_stability(workflow_id: str, test_input: dict, expected_output,
                     method: str | None = None,
                     webhook_path: str | None = None) -> StabilityResult:
    """Main entry: runs the workflow for real, requires
    REQUIRED_CONSECUTIVE_PASSES successes with exact expected-output match.
    Any failure resets the counter to zero. Classifies the final outcome as
    STABLE / FLAT_FAILURE / FLAKY (the requested 'failure is not consistent'
    signal — e.g. succeeded 3, failed, succeeded again).

    method=None -> legacy REST trigger path (may 405 on self-hosted n8n);
    method='webhook' -> trigger via the workflow's webhook URL then verify via
    GET /api/v1/executions; method='cli' -> requires shell access."""
    if not workflow_id:
        return StabilityResult("UNSTABLE_REJECTED", [], 0, 0, "FLAT_FAILURE")
    consecutive = 0
    max_consecutive = 0
    total_attempts = 0
    attempts_log = []

    while consecutive < REQUIRED_CONSECUTIVE_PASSES:
        total_attempts += 1
        if total_attempts > MAX_TOTAL_ATTEMPTS:
            pattern = "FLAT_FAILURE" if max_consecutive == 0 else "FLAKY"
            return StabilityResult("UNSTABLE_REJECTED", attempts_log, consecutive,
                                   max_consecutive, pattern)

        result = trigger_workflow_execution(workflow_id, test_input,
                                            method=method,
                                            webhook_path=webhook_path)
        matched = bool(result.get("success")) and compare_with_expected(result.get("output"), expected_output)
        result["matched_expected"] = matched

        attempts_log.append({"attempt": total_attempts, **result})
        log_attempt(workflow_id, total_attempts, consecutive, result)

        if matched:
            consecutive += 1
            max_consecutive = max(max_consecutive, consecutive)
        else:
            consecutive = 0

    return StabilityResult("STABLE_VERIFIED", attempts_log, consecutive,
                           max_consecutive, "STABLE")
