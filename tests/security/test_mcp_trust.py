"""test_mcp_trust.py — MCP trust model enforcement (10 vectors + report).

Policy under test: scripts/mcp_trust.py + scripts/mcp_trust_policy.json.
Verdicts use fixture cert descriptors (policy-logic scope; transport TLS
termination is the MCP client's job and is not re-tested here).
Report: /tmp/opencode-device/mcp_trust_report.json
"""
import json
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(HERE / "scripts"))

from mcp_trust import check_tool, evaluate_server  # noqa: E402

REPORT = Path("/tmp/opencode-device/mcp_trust_report.json")
RESULTS = {}


def rec(name, verdict, evidence, expected):
    RESULTS[name] = {"verdict": verdict, "evidence": evidence,
                     "expected": expected}
    print(f"[{verdict}] {name}: {evidence}")


def good_cert(host="mcp.firecrawl.dev", fp="PIN-FIRECRAWL"):
    return {"hostname": host, "valid_to": time.time() + 86400,
            "fingerprint": fp, "revoked": False}


def test_mcp_trust():
    # 1. unknown server -> DENY
    t, w = evaluate_server("evil-mcp", good_cert())
    rec("unknown_server", "DENY" if t == "deny" else "FAIL_OPEN", str(w),
        "DENY")
    # 2. wrong certificate (pin mismatch) -> DENY
    t, w = evaluate_server("firecrawl", good_cert(fp="WRONG-PIN"))
    rec("wrong_certificate", "DENY" if t == "deny" else "FAIL_OPEN", str(w),
        "DENY")
    # 3. expired certificate -> DENY
    c = good_cert()
    c["valid_to"] = time.time() - 10
    t, w = evaluate_server("firecrawl", c)
    rec("expired_certificate", "DENY" if t == "deny" else "FAIL_OPEN", str(w),
        "DENY")
    # 4. hostname mismatch -> DENY
    t, w = evaluate_server("firecrawl", good_cert(host="attacker.example"))
    rec("hostname_mismatch", "DENY" if t == "deny" else "FAIL_OPEN", str(w),
        "DENY")
    # 5. trusted server within grant -> ALLOW
    t, w = check_tool("firecrawl", "firecrawl_scrape", good_cert())
    rec("trusted_server", "ALLOW" if t == "allow" else "FAIL_OPEN", str(w),
        "ALLOW within capabilities")
    # 6. trusted server requesting NEW capability -> ASK (re-authorization)
    t, w = evaluate_server("firecrawl", good_cert(),
                           requested_caps=["web-scrape", "os-exec"])
    rec("new_capability", "ASK" if t == "ask" else "FAIL_OPEN", str(w),
        "ASK, never silent widening")
    # 7. tool outside allowlist -> DENY
    t, w = check_tool("firecrawl", "os_exec", good_cert())
    rec("tool_outside_allowlist", "DENY" if t == "deny" else "FAIL_OPEN",
        str(w), "DENY")
    # 8. malicious tool result -> rejected by independent verifier
    sys.path.insert(0, str(HERE))
    from tool_result_verifier import ResultVerifier
    import tempfile
    j = str(Path(tempfile.mkdtemp(prefix="mcpv-")) / "v.jsonl")
    rv = ResultVerifier(journal_path=j)
    probe = Path("/tmp/tbw-mcp-probe-should-exist.txt")
    probe.write_text("still here")
    claimed = {"file": str(probe), "deleted": True}  # tool SAYS deleted
    v = rv.verify(tool="mcp-test", claimed=claimed,
                  checker=lambda c: (Path(c["file"]).read_text() == "gone",
                                     "independent content re-read"))
    probe.unlink(missing_ok=True)
    rec("malicious_tool_result",
        "DENY" if not v["verified"] else "FAIL_OPEN",
        f"forged 'deleted' rejected: {v['note']}", "verification failure")
    # 9. server impersonation (right name, wrong pin) -> DENY
    t, w = evaluate_server("firecrawl", good_cert(fp="ATTACKER-PIN"))
    rec("impersonation", "DENY" if t == "deny" else "FAIL_OPEN", str(w),
        "DENY on pin mismatch")
    # 10. revoked server -> DENY
    t, w = evaluate_server("firecrawl", {**good_cert(), "revoked": True})
    rec("revoked_server", "DENY" if t == "deny" else "FAIL_OPEN", str(w),
        "DENY")
    # 11. disabled server (figma) -> DENY even with good cert shape
    t, w = evaluate_server("figma", {"hostname": "mcp.figma.com",
                                     "valid_to": time.time() + 99,
                                     "fingerprint": "x",
                                     "revoked": False})
    rec("disabled_server", "DENY" if t == "deny" else "FAIL_OPEN", str(w),
        "DENY while disabled")

    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(json.dumps(
        {"time": time.strftime("%Y-%m-%dT%H:%M:%S"), "tests": RESULTS},
        indent=1))
    fails = [k for k, v in RESULTS.items() if v["verdict"] == "FAIL_OPEN"]
    assert not fails, f"MCP trust FAIL_OPEN: {fails}"
