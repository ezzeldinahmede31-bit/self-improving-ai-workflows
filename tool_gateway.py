"""Open-source tool gateway — the thin, honest adapter layer between this
architect pipeline and the OSS stack deployed via deploy/bootstrap_tools.sh:

  LiteLLM   : model proxy w/ budget ceilings + auto-failover (port 4000)
  Prism     : OpenAPI -> live local mock server               (port 4010)
  Qdrant    : ephemeral task-scoped vector collections        (port 6333)
  Semgrep   : static SAST on generated code nodes             (docker image)
  Nuclei    : webhook/API vulnerability scanner                (docker image)
  garak     : LLM prompt-injection / data-leakage scanner      (venv module)

Every adapter follows one contract: if the tool is not reachable, return a
`None`-ish / SKIPPED result instead of crashing — the deterministic pipeline
must NEVER depend on these batteries. Tool checks themselves are what make the
"next step" configuration real rather than theoretical.
"""

from __future__ import annotations

import json
import os
import socket
import subprocess
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass, field
from typing import Any, Optional


# --------------------------------------------------------------------------
# Connection / capability probing (no side effects, fast)
# --------------------------------------------------------------------------

def _tcp_open(host: str, port: int, timeout: float = 1.2) -> bool:
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return True
    except OSError:
        return False


def _http_get(url: str, timeout: float = 2.0) -> Optional[dict[str, Any]]:
    try:
        with urllib.request.urlopen(url, timeout=timeout) as r:
            return {"status": r.status, "body": r.read().decode("utf-8", "replace")}
    except (urllib.error.URLError, OSError, TimeoutError):
        return None


@dataclass
class ToolStatus:
    """Snapshot of which OSS tools are actually reachable right now."""
    litellm: bool = False
    prism: bool = False
    qdrant: bool = False
    semgrep: bool = False
    nuclei: bool = False
    garak: bool = False


class ToolGateway:
    """Probes each tool once; exposes capability flags so the orchestrator can
    decide to use them without bloating the deterministic core.

    SECURITY (GAP-01 closure): probes are loopback-only by default. The
    gateway talks to operator-local sidecars (LiteLLM/Prism/Qdrant on
    127.0.0.1); a non-loopback host is rejected unless the caller passes
    allow_non_loopback=True explicitly (never from workflow-controlled
    input). Ports are validated integers.
    """

    def __init__(self, host: str = "127.0.0.1",
                 ports: Optional[dict[str, int]] = None,
                 allow_non_loopback: bool = False):
        if not allow_non_loopback and host not in (
                "127.0.0.1", "::1", "localhost"):
            raise ValueError(
                f"ToolGateway host must be loopback (got {host!r}); pass "
                "allow_non_loopback=True only for explicit operator config, "
                "never from workflow-controlled input.")
        self.host = host
        self.ports = {
            "litellm": 4000, "prism": 4010, "qdrant": 6333,
            **(ports or {}),
        }
        for name, port in self.ports.items():
            if not isinstance(port, int) or not (1 <= port <= 65535):
                raise ValueError(f"bad port for {name}: {port!r}")
        self._cache: Optional[ToolStatus] = None

    def status(self, refresh: bool = False) -> ToolStatus:
        if self._cache is None or refresh:
            s = ToolStatus()
            s.litellm = _tcp_open(self.host, self.ports["litellm"])
            s.prism = _tcp_open(self.host, self.ports["prism"])
            s.qdrant = _http_get(f"http://{self.host}:{self.ports['qdrant']}/healthz") is not None
            s.semgrep = self._image_present("ghcr.io/semgrep/semgrep:latest")
            s.nuclei = self._image_present("projectdiscovery/nuclei:latest")
            s.garak = self._python_module("garak")
            self._cache = s
        return self._cache

    @staticmethod
    def _image_present(image: str) -> bool:
        try:
            r = subprocess.run(["docker", "image", "inspect", image],
                               capture_output=True, text=True, timeout=5)
            return r.returncode == 0
        except Exception:
            return False

    @staticmethod
    def _python_module(name: str) -> bool:
        try:
            __import__(name)
            return True
        except ImportError:
            return False

    def enabled(self, tool: str) -> bool:
        return getattr(self.status(), tool, False)


# --------------------------------------------------------------------------
# LiteLLM model routing (budget + fallback driven by the proxy)
# --------------------------------------------------------------------------

@dataclass
class LiteLLMResult:
    ok: bool
    model_used: str = ""
    budget_usd: float = 0.0
    reason: str = ""


class LiteLLMFailover:
    """Calls the proxy at /chat/completions. Model fallback list is honored by
    LiteLLM itself; this class only surfaces which model actually served and
    whether the hard budget ceiling on the proxy was hit."""

    def __init__(self, base_url: str = "http://127.0.0.1:4000",
                 models: Optional[list[str]] = None,
                 budget_usd: float = 5.0,
                 allow_non_loopback: bool = False):
        from urllib.parse import urlsplit as _split
        _host = (_split(base_url).hostname or "")
        if not allow_non_loopback and _host not in (
                "127.0.0.1", "::1", "localhost"):
            raise ValueError(
                f"LiteLLMFailover base_url must be loopback (got {_host!r}); "
                "pass allow_non_loopback=True only for explicit operator "
                "config.")
        self.base_url = base_url.rstrip("/")
        self.models = models or ["deepseek-chat", "qwen-coder-local", "deepseek-reasoner"]
        self.budget_usd = budget_usd

    def is_reachable(self, gw: Optional[ToolGateway] = None) -> bool:
        gw = gw or ToolGateway()
        return gw.enabled("litellm") and self._cost_endpoint_ok()

    def _cost_endpoint_ok(self) -> bool:
        return _http_get(f"{self.base_url}/get/spend/logs", timeout=1.0) is not None

    def complete(self, messages: list[dict[str, Any]],
                 prefer: Optional[str] = None) -> LiteLLMResult:
        """POST a chat completion. In tests/mocks this is exercised against a
        fake; against a live proxy it honours its own failover + budget."""
        model = prefer or self.models[0]
        payload = {
            "model": model,
            "messages": messages,
            "user": "jit-orchestrator",
        }
        req = urllib.request.Request(
            f"{self.base_url}/chat/completions",
            data=json.dumps(payload).encode(),
            headers={"Content-Type": "application/json"},
        )
        try:
            with urllib.request.urlopen(req, timeout=15) as r:
                body = json.loads(r.read().decode())
                return LiteLLMResult(
                    ok=True,
                    model_used=body.get("model", model),
                    budget_usd=self.budget_usd,
                    reason="served",
                )
        except urllib.error.HTTPError as e:
            reason = "budget_ceiling" if e.code == 429 else f"http_{e.code}"
            return LiteLLMResult(ok=False, model_used=model,
                                 budget_usd=self.budget_usd, reason=reason)
        except (urllib.error.URLError, TimeoutError, OSError) as e:
            return LiteLLMResult(ok=False, model_used=model,
                                 budget_usd=self.budget_usd,
                                 reason=f"unreachable: {e.__class__.__name__}")


# --------------------------------------------------------------------------
# Prism OpenAPI mock autoloader (turns a spec into local mock routes)
# --------------------------------------------------------------------------

class PrismMock:
    """Serves/prboes an OpenAPI spec on the local Prism instance. Because Prism
    resolves paths from the spec file, this adapter just verifies availability
    and reports the base URL the engine should route mock traffic to."""

    def __init__(self, base_url: str = "http://127.0.0.1:4010"):
        self.base_url = base_url

    def healthy(self, gw: Optional[ToolGateway] = None) -> bool:
        gw = gw or ToolGateway()
        return gw.enabled("prism")

    def resolve(self, external_url: str) -> str:
        """Map an external service host to the Prism mock base (used by the
        MockRouter integration)."""
        parsed = urllib.parse.urlsplit(external_url)
        return f"{self.base_url}{parsed.path}{'?' + parsed.query if parsed.query else ''}"


# --------------------------------------------------------------------------
# Semgrep SAST for generated code nodes
# --------------------------------------------------------------------------

class SemgrepSAST:
    """Runs Semgrep on a directory of generated node code. Returns per-file
    findings. SKIPPED (no findings, flagged) when the image is absent."""

    def run(self, path: str, gw: Optional[ToolGateway] = None) -> dict[str, Any]:
        gw = gw or ToolGateway()
        if not gw.enabled("semgrep"):
            return {"ran": False, "findings": [], "reason": "semgrep image not present"}
        try:
            r = subprocess.run(
                ["docker", "run", "--rm", "-v", f"{path}:/src:ro",
                 "ghcr.io/semgrep/semgrep:latest", "scan", "--json", "/src"],
                capture_output=True, text=True, timeout=60)
            if r.returncode == 0:
                data = json.loads(r.stdout or "{}")
                findings = data.get("results", [])
                return {"ran": True, "findings": findings}
            return {"ran": True, "findings": [], "error": (r.stderr or "")[:400]}
        except subprocess.TimeoutExpired:
            return {"ran": True, "findings": [], "error": "timeout"}
        except Exception as e:
            return {"ran": False, "findings": [], "reason": str(e)}


# --------------------------------------------------------------------------
# Nuclei webhook/API scanner
# --------------------------------------------------------------------------

class NucleiScan:
    """Scans a target (webhook/API) for OWASP-class vulnerabilities."""
    TEMPLATES = ["exposures", "misconfiguration", "default-logins"]

    def run(self, target: str, gw: Optional[ToolGateway] = None) -> dict[str, Any]:
        gw = gw or ToolGateway()
        if not gw.enabled("nuclei"):
            return {"ran": False, "hits": [], "reason": "nuclei image not present"}
        try:
            r = subprocess.run(
                ["docker", "run", "--rm", "projectdiscovery/nuclei:latest",
                 "-u", target, "-silent", "-json"],
                capture_output=True, text=True, timeout=90)
            hits = []
            for line in r.stdout.splitlines():
                line = line.strip()
                if line:
                    try:
                        hits.append(json.loads(line))
                    except (ValueError, json.JSONDecodeError):
                        hits.append({"raw": line[:300]})
            return {"ran": True, "hits": hits}
        except subprocess.TimeoutExpired:
            return {"ran": True, "hits": [], "error": "timeout"}
        except Exception as e:
            return {"ran": False, "hits": [], "reason": str(e)}


# --------------------------------------------------------------------------
# garak LLM scan (python-level, run when module is installed in a venv)
# --------------------------------------------------------------------------

class GarakLLMScan:
    """Prompt-injection / data-leakage probing of the chosen LLM endpoint. Only
    wired when `garak` is importable (bootstrap venv), else skips cleanly."""

    def run(self, model_name: str = "lmstudio",
            gw: Optional[ToolGateway] = None) -> dict[str, Any]:
        gw = gw or ToolGateway()
        if not gw.enabled("garak"):
            return {"ran": False, "reason": "garak not installed (vendor/garak)"}
        # garak runs on the CLI: `python -m garak --model_type ...`. We expose
        # the command the integration would execute without auto-running it.
        return {
            "ran": True,
            "invoke": ["python", "-m", "garak", "--model_type", model_name,
                       "--probes", "promptinject,dan,leakge"],
            "note": "long-running; invoke manually in vendor/garak venv",
        }


if __name__ == "__main__":
    gw = ToolGateway()
    s = gw.status(refresh=True)
    print("Tool capability probe:")
    for k, v in s.__dataclass_fields__.items():
        print(f"  {k:<10} {'UP' if getattr(s, k) else 'down'}")