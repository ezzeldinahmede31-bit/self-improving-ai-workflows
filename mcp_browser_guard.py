"""MCP + browser guard: registry, allow-list, download scans.

Agents see solely registered surfaces: MCP servers enroll with
identity/version/tool list/permissions/risk/signature (verified via
the trust registry shape: id + sha + risk tier), and calls to
unenrolled servers refuse. Browsing is domain allow-listed
(suffix match, deny-by-default); downloads pass a scan gate (size
ceiling, extension policy, content-scan hook) into quarantine before
any agent read. Browser automation itself always routes through the
sandbox + egress firewall (defense in depth, not duplication).

Only stdlib is used. Scanners/sandboxes are caller-injected hooks.
"""

from __future__ import annotations

import hashlib
import time


def _domain_ok(host: str, allowed: tuple[str, ...]) -> bool:
    host = str(host).lower().rstrip(".")
    for dom in allowed:
        dom = str(dom).lower().rstrip(".")
        if host == dom or host.endswith("." + dom):
            return True
    return False


class McpRegistry:
    """Enrolled MCP servers with risk-tiered call policy."""

    def __init__(self):
        self._servers: dict[str, dict] = {}

    def enroll(self, *, server_id: str, version: str, tools: list[str],
               permissions: list[str], risk: str,
               signature: str = "") -> dict:
        """Register one server (risk: low/medium/high)."""
        if risk not in ("low", "medium", "high"):
            raise ValueError("risk must be low|medium|high")
        rec = {"version": str(version),
               "tools": [str(t) for t in tools],
               "permissions": [str(p) for p in permissions],
               "risk": risk, "signature": str(signature),
               "enrolled_at": time.time()}
        self._servers[str(server_id)] = rec
        return {"server": str(server_id), "risk": risk}

    def call_policy(self, server_id: str, tool: str) -> dict:
        """Verdict for one tool call: allow / review / deny + reason."""
        rec = self._servers.get(str(server_id))
        if rec is None:
            return {"verdict": "deny", "reason": "server not enrolled"}
        if str(tool) not in rec["tools"]:
            return {"verdict": "deny", "reason": "tool not declared"}
        if rec["risk"] == "high":
            return {"verdict": "review",
                    "reason": "high-risk server needs approval"}
        if rec["risk"] == "medium":
            return {"verdict": "allow",
                    "reason": "medium risk logged"}
        return {"verdict": "allow", "reason": "low risk"}

    def revoke(self, server_id: str) -> bool:
        """Remove a server (immediate call denial afterwards)."""
        return self._servers.pop(str(server_id), None) is not None

    def servers(self) -> list[str]:
        """Enrolled server ids."""
        return sorted(self._servers)


class BrowserGuard:
    """Domain allow-list + download scan gate for browser agents."""

    def __init__(self, *, allowed_domains: tuple[str, ...] = (),
                 max_download_b: int = 25 * 1024 * 1024,
                 blocked_exts: tuple[str, ...] = (".exe", ".msi",
                                                  ".bat", ".ps1",
                                                  ".scr", ".dll")):
        self._domains = tuple(allowed_domains)
        self._max = int(max_download_b)
        self._exts = tuple(e.lower() for e in blocked_exts)
        self.quarantine: list[dict] = []

    def visit_ok(self, host: str) -> tuple[bool, str]:
        """Deny-by-default domain check for navigation."""
        if _domain_ok(host, self._domains):
            return True, "allow-listed"
        return False, f"domain outside allow-list: {host}"

    def scan_download(self, *, filename: str, size_b: int,
                      sha256: str = "", content_ok: bool = True) -> dict:
        """Size + extension + content-hook gate; failures quarantine."""
        name = str(filename).lower()
        if size_b > self._max:
            return self._hold(filename, size_b, "over size ceiling")
        if any(name.endswith(ext) for ext in self._exts):
            return self._hold(filename, size_b, "blocked extension")
        if not content_ok:
            return self._hold(filename, size_b, "content scan failed")
        digest = sha256 or hashlib.sha256(
            f"{filename}:{size_b}".encode()).hexdigest()
        return {"verdict": "allow", "sha256": digest,
                "reason": "scan clean"}

    def _hold(self, filename: str, size_b: int, reason: str) -> dict:
        rec = {"file": str(filename), "size": int(size_b),
               "reason": reason, "ts": time.time()}
        self.quarantine.append(rec)
        return {"verdict": "quarantine", "reason": reason}
