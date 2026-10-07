#!/usr/bin/env python3
"""mcp_trust.py — explicit MCP trust policy (TLS is transport, not trust).

TLS alone never answers: WHO is this server, WHAT may it do, and WHAT CHANGED.
This module enforces an allowlist with per-server identity, endpoint pinning,
authentication, capability grants, and tool allowlists.

Verdicts: ALLOW (trusted + tool/caps within grant), ASK (known-pending server
or trusted server requesting a NEW capability -> human re-authorization),
DENY (unknown/disabled/wrong-cert/expired/hostname-mismatch/revoked/tool
outside allowlist).

Certificate checks take an injected cert descriptor (as observed by the
transport): {hostname, valid_from, valid_to, fingerprint, revoked}.
Transport TLS termination stays where it is; this layer adds the trust
decision on top. Live-network cert fetching is intentionally NOT done here
(unit scope = policy logic; transport proves the bytes).

Usage: python3 scripts/mcp_trust.py selftest
Policy file: scripts/mcp_trust_policy.json (edit = re-authorization event).
"""
import hashlib
import json
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
POLICY_FILE = HERE / "mcp_trust_policy.json"


def load_policy():
    try:
        pol = json.loads(POLICY_FILE.read_text())
        assert isinstance(pol.get("servers"), dict)
        return pol, None
    except Exception as e:
        return None, f"trust policy unloadable ({e}) -> fail closed"


def _cert_problems(server, cert):
    """cert: dict(hostname, valid_to epoch, fingerprint, revoked)."""
    probs = []
    now = time.time()
    if not isinstance(cert, dict):
        return ["no-cert-descriptor"]
    if cert.get("revoked"):
        probs.append("revoked")
    try:
        if float(cert.get("valid_to", 0)) < now:
            probs.append("expired")
    except Exception:
        probs.append("bad-validity")
    want_host = server.get("hostname")
    if want_host and cert.get("hostname") != want_host:
        probs.append(f"hostname-mismatch (got {cert.get('hostname')!r})")
    pin = server.get("pin_sha256")
    if pin and cert.get("fingerprint") != pin:
        probs.append("pin-mismatch (possible impersonation)")
    return probs


def evaluate_server(server_id, cert=None, requested_caps=()):
    """Decide whether a server session may proceed. Returns (tier, reason)."""
    policy, err = load_policy()
    if policy is None:
        return "deny", {"reason": err}
    srv = policy["servers"].get(server_id)
    if srv is None:
        return "deny", {"reason": "unknown-server (allowlist only)"}
    if srv.get("status") == "disabled":
        return "deny", {"reason": "server disabled in policy"}
    probs = _cert_problems(srv, cert or {})
    if probs:
        return "deny", {"reason": "cert: " + ",".join(probs)}
    if srv.get("status") == "pending":
        return "ask", {"reason": "new server needs human approval"}
    granted = set(srv.get("capabilities", []))
    new = [c for c in (requested_caps or []) if c not in granted]
    if new:
        return "ask", {"reason": f"new capabilities need re-auth: {new}"}
    return "allow", {"reason": "trusted within granted capabilities"}


def check_tool(server_id, tool, cert=None):
    """Tool call gate. Returns (tier, reason)."""
    tier, why = evaluate_server(server_id, cert)
    if tier != "allow":
        return tier, why
    policy, _ = load_policy()
    allowed = policy["servers"][server_id].get("allowed_tools", [])
    if tool in allowed or "*" in allowed:
        return "allow", {"reason": f"tool {tool} in allowlist"}
    return "deny", {"reason": f"tool {tool} outside allowlist"}


def main(argv):
    if len(argv) == 2 and argv[1] == "selftest":
        good = {"hostname": "mcp.firecrawl.dev", "valid_to": time.time() + 86400,
                "fingerprint": "PIN-FIRECRAWL", "revoked": False}
        cases = [
            (evaluate_server("nope", good), "deny"),
            (evaluate_server("firecrawl",
                             {**good, "hostname": "evil.example"}), "deny"),
            (evaluate_server("firecrawl",
                             {**good, "valid_to": time.time() - 1}), "deny"),
            (evaluate_server("firecrawl", {**good, "revoked": True}), "deny"),
            (evaluate_server("figma", good), "deny"),
            (check_tool("firecrawl", "firecrawl_scrape", good), "allow"),
            (check_tool("firecrawl", "os_exec", good), "deny"),
        ]
        bad = 0
        for (tier, why), want in cases:
            ok = tier == want
            bad += not ok
            print(f"{'PASS' if ok else 'FAIL'} got={tier} want={want} ({why})")
        print("SELFTEST " + ("OK" if not bad else "FAILED"))
        return 0 if not bad else 1
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv))
