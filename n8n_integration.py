"""n8n Integration Adapter: trigger, wait, verify on live n8n.

This module wraps the existing n8n_stability_verifier.py logic into
a callable interface for the orchestrator. It does NOT add new logic —
it exposes the existing verifier as an async-compatible call with
the same strict gates (5 consecutive passes, 15 total attempts).

Transport is connection-pinned stdlib (fetch_pinned): every call is
egress-validated AND the socket opens the authorized IP literally, so
DNS between check and connect cannot reroute API or webhook traffic.
No `requests` dependency — stdlib only.

Usage:
    n8n = N8NIntegration(base_url, api_key, egress_policy=...)
    result = n8n.trigger_and_verify(workflow_id, webhook_path, payload, expected_output)
    # result = {"ok": bool, "runs": [...], "status": "stable|flat|flaky|timeout"}

Only stdlib. No new dependencies.
"""

from __future__ import annotations

import hashlib
import json
import os
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Optional

from egress_firewall import (check_url as _check_url, EgressPolicy,
                             fetch_pinned as _fetch_pinned,
                             PinnedFetchBlocked as _PinnedBlocked)

REQUIRED_CONSECUTIVE_PASSES = 5
MAX_TOTAL_ATTEMPTS = 15
TIMEOUT_PER_EXECUTION = 30


def _load_env(name: str, default: str = "") -> str:
    val = os.environ.get(name)
    if val:
        return val
    for env_path in (Path(__file__).resolve().parent / ".env",
                     Path(__file__).resolve().parent.parent / ".env"):
        if env_path.exists():
            for line in env_path.read_text(encoding="utf-8").splitlines():
                line = line.strip()
                if line.startswith(name + "="):
                    return line.split("=", 1)[1].strip()
    return default


@dataclass
class N8NConfig:
    base_url: str = "http://localhost:5678"
    api_key: str = ""
    webhook_base: str = ""


class N8NIntegration:
    """Trigger an n8n workflow and verify its output stability."""

    def __init__(
        self,
        config: N8NConfig | None = None,
        *,
        egress_policy: EgressPolicy | None = None,
        capability_issuer: Any = None,
        capability_token: str | None = None,
        strict: bool = False,
    ):
        """strict=True (production): egress_policy is MANDATORY at
        construction; per-call, a missing egress gate or a missing task
        capability fails closed instead of skipping the check (the
        capability is minted per-task at step 0d and injected later, so it
        is enforced at call time, not here). strict=False keeps the legacy
        dev/test shape where absent gates skip checks."""
        if strict and egress_policy is None:
            raise RuntimeError(
                "N8NIntegration strict mode requires egress_policy")
        self.strict = bool(strict)
        self.config = config or N8NConfig(
            base_url=_load_env("N8N_BASE_URL", "http://localhost:5678"),
            api_key=_load_env("N8N_API_KEY", ""),
            webhook_base=_load_env("N8N_WEBHOOK_BASE", ""),
        )
        self.egress_policy = egress_policy
        self.capability_issuer = capability_issuer
        self.capability_token = capability_token

    def _api_headers(self) -> dict:
        headers = {"Accept": "application/json"}
        if self.config.api_key:
            headers["X-N8N-API-KEY"] = self.config.api_key
        return headers

    def _gates(self, url: str, base_url: str) -> None:
        """Egress + capability gates. Raises RuntimeError on refusal."""
        if self.egress_policy is not None:
            verdict = _check_url(url, self.egress_policy)
            if not verdict.allowed:
                raise RuntimeError(f"Egress blocked: {verdict.reason}")
        elif self.strict:
            raise RuntimeError("strict mode: egress gate missing")
        if self.capability_issuer is not None and self.capability_token:
            from platform_wiring import check_capability as _check_cap
            import urllib.parse
            host = urllib.parse.urlparse(base_url).hostname or ""
            chk = _check_cap(self.capability_issuer, self.capability_token,
                             action="net.fetch", resource=host or "*")
            if not chk["ok"]:
                raise RuntimeError(f"Capability rejected: {chk['reason']}")
        elif self.strict:
            raise RuntimeError("strict mode: task capability missing")

    def _pinned_policy(self) -> EgressPolicy:
        # Pinned transport always runs under A policy: the configured one,
        # else the default deny-by-default policy (tolerant legacy shape —
        # denials surface as None/False, never as unfirewalled fetches).
        return self.egress_policy or EgressPolicy()

    def _get_json(self, url: str) -> dict | None:
        self._gates(url, self.config.base_url)
        try:
            out = _fetch_pinned(url, self._pinned_policy(), method="GET",
                                headers=self._api_headers(),
                                timeout_s=TIMEOUT_PER_EXECUTION)
        except _PinnedBlocked as e:
            if self.strict:
                raise RuntimeError(f"Egress blocked: {e}")
            return None
        except Exception:
            return None
        if out.get("status") != 200:
            return None
        try:
            body = out.get("body", b"")
            return json.loads(body.decode("utf-8"))
        except (ValueError, UnicodeDecodeError):
            return None

    def _fetch_workflow(self, workflow_id: str) -> dict | None:
        url = f"{self.config.base_url}/api/v1/workflows/{workflow_id}"
        return self._get_json(url)

    def _latest_execution_id(self, workflow_id: str) -> str | None:
        url = f"{self.config.base_url}/api/v1/executions?workflowId={workflow_id}&limit=1"
        data = self._get_json(url)
        if data and data.get("data"):
            return data["data"][0].get("id")
        return None

    def _fetch_execution(self, execution_id: str) -> dict | None:
        url = f"{self.config.base_url}/api/v1/executions/{execution_id}?includeData=true"
        return self._get_json(url)

    def _trigger_via_webhook(self, webhook_path: str, payload: dict) -> bool:
        """POST to webhook. Returns True if HTTP 2xx, else False."""
        url = f"{self.config.webhook_base or self.config.base_url}/webhook/{webhook_path}"
        self._gates(url,
                    self.config.webhook_base or self.config.base_url)
        try:
            out = _fetch_pinned(
                url, self._pinned_policy(), method="POST",
                data=json.dumps(payload).encode("utf-8"),
                headers={**self._api_headers(),
                         "Content-Type": "application/json"},
                timeout_s=TIMEOUT_PER_EXECUTION)
            return 200 <= int(out.get("status", 0)) < 300
        except _PinnedBlocked as e:
            if self.strict:
                raise RuntimeError(f"Egress blocked: {e}")
            return False
        except Exception:
            return False

    def trigger_and_verify(self,
                           workflow_id: str,
                           webhook_path: str,
                           payload: dict,
                           expected_output: dict,
                           webhook_base: str = "",
                           required_passes: int = REQUIRED_CONSECUTIVE_PASSES,
                           max_attempts: int = MAX_TOTAL_ATTEMPTS) -> dict:
        """
        Trigger workflow via webhook and verify its output stability.

        Returns:
            {"ok": bool, "status": "stable|flat|flaky|timeout|error",
             "runs": [...], "consecutive": int, "attempts": int,
             "details": str}
        """
        if not self.config.api_key and not os.environ.get("N8N_API_KEY"):
            return {"ok": False, "status": "error",
                    "details": "No API key configured"}

        # Verify workflow exists
        if not self._fetch_workflow(workflow_id):
            return {"ok": False, "status": "error",
                    "details": f"Workflow {workflow_id} not found"}

        consecutive = 0
        runs = []
        attempts = 0
        webhook_url = f"{webhook_base or self.config.webhook_base or self.config.base_url}/webhook/{webhook_path}"

        for attempt in range(max_attempts):
            attempts += 1
            ok = self._trigger_via_webhook(webhook_path, payload)
            if not ok:
                runs.append({"attempt": attempt, "trigger": "failed", "ok": False})
                consecutive = 0
                continue

            # Wait for execution to complete
            time.sleep(2)
            exec_id = self._latest_execution_id(workflow_id)
            if not exec_id:
                runs.append({"attempt": attempt, "exec_id": None, "ok": False})
                consecutive = 0
                continue

            # Wait for completion
            for _ in range(TIMEOUT_PER_EXECUTION // 2):
                exec_data = self._fetch_execution(exec_id)
                if exec_data and exec_data.get("finished"):
                    break
                time.sleep(0.5)
            else:
                runs.append({"attempt": attempt, "exec_id": exec_id, "ok": False,
                             "reason": "timeout"})
                consecutive = 0
                continue

            # Compare output
            output = exec_data.get("data", {}).get("resultData", {})
            ok = self._outputs_match(output, expected_output)
            runs.append({"attempt": attempt, "exec_id": exec_id,
                         "output": output, "ok": ok})

            if ok:
                consecutive += 1
                if consecutive >= required_passes:
                    return {"ok": True, "status": "stable",
                            "runs": runs, "consecutive": consecutive,
                            "attempts": attempts,
                            "details": f"{consecutive} consecutive passes"}
            else:
                consecutive = 0

        if consecutive > 0:
            return {"ok": False, "status": "flaky",
                    "runs": runs, "consecutive": consecutive,
                    "attempts": attempts,
                    "details": f"reached {consecutive} passes then regressed"}
        return {"ok": False, "status": "flat",
                "runs": runs, "consecutive": 0,
                "attempts": attempts,
                "details": "never achieved a single pass"}

    @staticmethod
    def _outputs_match(actual: dict, expected: dict) -> bool:
        """Exact match on expected keys; extra keys in actual are OK."""
        for k, v in expected.items():
            if actual.get(k) != v:
                return False
        return True


def make_n8n_adapter() -> Optional[Any]:
    """Factory returning N8NIntegration if credentials exist, else None."""
    api_key = os.environ.get("N8N_API_KEY") or _load_env("N8N_API_KEY")
    if not api_key:
        return None
    return N8NIntegration()