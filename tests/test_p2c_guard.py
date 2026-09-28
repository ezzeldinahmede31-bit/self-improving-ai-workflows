"""Tests for mcp_browser_guard.py."""


def test_mcp_policy_tiers():
    from mcp_browser_guard import McpRegistry
    r = McpRegistry()
    r.enroll(server_id="fs", version="1.0", tools=["read"],
             permissions=["fs.read"], risk="low")
    r.enroll(server_id="crm", version="2.0", tools=["lookup"],
             permissions=["crm.read"], risk="medium")
    r.enroll(server_id="shell", version="0.3", tools=["exec"],
             permissions=["*"], risk="high")
    assert r.call_policy("fs", "read")["verdict"] == "allow"
    assert r.call_policy("crm", "lookup")["reason"] == "medium risk logged"
    assert r.call_policy("shell", "exec")["verdict"] == "review"
    assert r.call_policy("ghost", "read")["verdict"] == "deny"
    assert r.call_policy("fs", "write")["verdict"] == "deny"
    assert r.revoke("fs") and r.call_policy("fs", "read")["verdict"] == "deny"
    import pytest
    with pytest.raises(ValueError):
        r.enroll(server_id="x", version="1", tools=[], permissions=[],
                 risk="wild")


def test_browser_allowlist_and_downloads():
    from mcp_browser_guard import BrowserGuard
    g = BrowserGuard(allowed_domains=("example.com",))
    assert g.visit_ok("app.example.com") == (True, "allow-listed")
    assert g.visit_ok("evil.example.net")[0] is False
    ok = g.scan_download(filename="report.pdf", size_b=1000)
    assert ok["verdict"] == "allow" and ok["sha256"]
    q = g.scan_download(filename="tool.exe", size_b=100)
    assert q["verdict"] == "quarantine"
    q = g.scan_download(filename="big.zip", size_b=10 ** 12)
    assert q["verdict"] == "quarantine"
    q = g.scan_download(filename="doc.pdf", size_b=10, content_ok=False)
    assert q["verdict"] == "quarantine" and len(g.quarantine) == 3
