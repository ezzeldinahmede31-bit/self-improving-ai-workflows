"""test_browser_write_safe.py — P1: browser-write E2E in an ISOLATED fixture app.

Safety contract (hard):
- local http://127.0.0.1 ephemeral server only; disposable test/test account;
- FRESH disposable chromium profile per run (tmp dir); persistent-profile
  behavior tested with a THROWAWAY profile dir, never a production profile;
- no real accounts, cookies, credentials, or external network.

Closed loop per write: PLAN -> navigate -> inspect -> permission ->
write action -> observe -> INDEPENDENT server-side verify.

Report: /tmp/opencode-device/browser_write_report.json
"""
import json
import sys
import time
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent.parent.parent
SCRIPTS = HERE / "scripts"
sys.path.insert(0, str(SCRIPTS))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from tbw_app import STATE, reset, start_server  # noqa: E402

REPORT = Path("/tmp/opencode-device/browser_write_report.json")
RESULTS = {}

pytestmark = pytest.mark.skipif(
    __import__("importlib").util.find_spec("playwright") is None,
    reason="playwright not installed")


def rec(name, verdict, evidence):
    assert verdict in ("PASS", "FAIL", "BLOCKED")
    RESULTS[name] = {"verdict": verdict, "evidence": evidence}
    print(f"[{verdict}] {name}: {evidence}")


class WriteGate:
    """Ask-first gate for browser writes: no token -> BLOCKED (fail-closed)."""

    def __init__(self):
        from device_permissions import cmd_approve, cmd_consume
        import io
        from contextlib import redirect_stdout
        self._approve, self._consume = cmd_approve, cmd_consume
        self._io, self._rs = io, redirect_stdout
        self.session = f"tbw-{int(time.time()*1000)%100000}"

    def permit(self, step, action):
        buf = self._io.StringIO()
        with self._rs(buf):
            self._approve(self.session, step, "BrowserWrite", action, ttl=300)
        return buf.getvalue().strip()

    def attempt(self, step, action, token=None):
        """Returns True iff the write may proceed (valid single-use token)."""
        if not token:
            return False
        from device_permissions import cmd_consume  # noqa
        import io
        from contextlib import redirect_stdout
        # consume via CLI-equivalent: emulate single-use binding check
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = self._consume(self.session, step, "BrowserWrite", action,
                               token)
        return rc == 0


def _login(page, base):
    page.goto(base + "/")
    if page.locator("#u").count():
        page.fill("#u", "test")
        page.fill("#p", "test")
        page.click("#go")
        page.wait_for_load_state("domcontentloaded")
        page.goto(base + "/")  # /login returns plain ok; re-enter app
        page.wait_for_load_state("domcontentloaded")
    assert page.locator("#f1").count() == 1, "fixture app did not load"


def test_browser_write_safe(tmp_path):
    from playwright.sync_api import sync_playwright
    gate = WriteGate()
    srv, base = start_server()
    try:
        with sync_playwright() as pw:
            profile = str(tmp_path / "disposable-profile")
            ctx = pw.chromium.launch_persistent_context(
                profile, headless=True,
                args=["--no-sandbox", "--disable-dev-shm-usage"])
            page = ctx.new_page()
            try:
                # --- 1..5: basic writes (each gated, each server-verified) ---
                _login(page, base)
                rec("navigate_login", "PASS", "disposable account login ok")
                tok = gate.permit("fill-name", "fill #name")
                assert gate.attempt("fill-name", "fill #name", tok)
                page.fill("#name", "hello-tbw")
                assert page.input_value("#name") == "hello-tbw"
                rec("text_input", "PASS", "input_value roundtrip ok")

                tok = gate.permit("check", "check #agree")
                assert gate.attempt("check", "check #agree", tok)
                page.check("#agree")
                assert page.is_checked("#agree")
                rec("checkbox", "PASS", "checked state ok")

                tok = gate.permit("select", "select #color=blue")
                assert gate.attempt("select", "select #color=blue", tok)
                page.select_option("#color", "blue")
                assert page.input_value("#color") == "blue"
                rec("select", "PASS", "option=blue ok")

                tok = gate.permit("submit", "submit form")
                assert gate.attempt("submit", "submit form", tok)
                page.click("#save")
                page.wait_for_function(
                    "() => document.getElementById('status').textContent"
                    ".includes('saved:')", timeout=5000)
                forms = [a for a in STATE["actions"] if a["type"] == "form"]
                assert forms, "server saw no form submit"
                rec("form_fill_submit", "PASS",
                    f"server-recorded submit size={forms[-1].get('size')}")

                # --- write without permission = BLOCKED ---
                assert not gate.attempt("evil", "fill #name", None)
                rec("write_without_permission", "BLOCKED",
                    "no token -> gate refuses before touching DOM")

                # --- read-only never becomes write ---
                before = len(STATE["actions"])
                _ = page.text_content("#status")
                _ = page.input_value("#name")
                assert len(STATE["actions"]) == before
                rec("read_stays_read", "PASS", "reads produced zero actions")

                # --- 6: controlled upload ---
                up = tmp_path / "up.txt"
                up.write_text("upload-fixture-bytes")
                tok = gate.permit("upload", "upload fixture file")
                assert gate.attempt("upload", "upload fixture file", tok)
                page.set_input_files("#up", str(up))
                page.wait_for_function(
                    "() => document.getElementById('status').textContent"
                    ".includes('uploaded:')", timeout=5000)
                ups = [a for a in STATE["actions"] if a["type"] == "upload"]
                assert ups and ups[-1]["has_name"]
                rec("controlled_upload", "PASS",
                    f"server recorded upload size={ups[-1]['size']}")

                # --- 7: controlled download ---
                tok = gate.permit("dl", "download test.csv")
                assert gate.attempt("dl", "download test.csv", tok)
                with page.expect_download(timeout=5000) as dl:
                    page.click("#dl")
                path = dl.value.path()
                assert Path(path).read_bytes().startswith(b"col1")
                assert any(a["type"] == "download" for a in STATE["actions"])
                rec("controlled_download", "PASS", "bytes verified locally")

                # --- 8: multi-step form ---
                page.fill("#w1", "s1")
                page.click("#next")
                assert page.locator("#step2").is_visible()
                tok = gate.permit("wiz", "wizard finish")
                assert gate.attempt("wiz", "wizard finish", tok)
                page.fill("#w2", "s2-final")
                page.click("#finish")
                page.wait_for_function(
                    "() => document.getElementById('status').textContent"
                    ".includes('wizard:')", timeout=5000)
                wiz = [a for a in STATE["actions"] if a["type"] == "wizard"]
                assert wiz and wiz[-1]["step2"] == "s2-final"
                rec("multi_step_form", "PASS", "server step2=s2-final")

                # --- 9: popup/tab ---
                with page.expect_popup(timeout=5000) as pop:
                    page.click("#pop")
                popup = pop.value
                popup.wait_for_load_state("domcontentloaded")
                assert popup.locator("#ph").text_content() == "popup-ok"
                popup.close()
                rec("popup_tab", "PASS", "popup content verified, closed")

                # --- 10: navigation ---
                page.goto(base + "/needs-auth")
                assert "auth-ok" in page.content()
                rec("navigation", "PASS", "auth area reached")

                # --- 11: stale DOM + recovery ---
                page.goto(base + "/")
                page.wait_for_selector("#crash")
                stale = page.query_selector("#crash")
                page.click("#crash")  # replaces the node
                try:
                    stale.click(timeout=2000)
                    rec("stale_dom", "FAIL", "stale handle clicked?!")
                except Exception:
                    page.locator("#crash").click()  # re-query = recovery
                    assert "replaced-clicked" in page.text_content("#status")
                    rec("stale_dom_recovery", "PASS",
                        "stale detected, re-queried, recovered")

                # --- 12: page reload keeps server truth ---
                n_before = len([a for a in STATE["actions"]
                                if a["type"] == "form"])
                page.reload()
                page.wait_for_selector("#f1")
                n_after = len([a for a in STATE["actions"]
                               if a["type"] == "form"])
                assert n_before == n_after
                rec("page_reload", "PASS", "no phantom duplicate submits")

                # --- 13/14: action failure + recovery ---
                try:
                    page.click("#hiddenBtn", timeout=2000)
                    rec("action_failure", "FAIL", "disabled click passed?!")
                except Exception:
                    page.click("#toggle")  # recovery: enable first
                    tok = gate.permit("hidden", "click hiddenBtn")
                    assert gate.attempt("hidden", "click hiddenBtn", tok)
                    page.click("#hiddenBtn")
                    page.wait_for_function(
                        "() => document.getElementById('status').textContent"
                        ".includes('hidden-ok')", timeout=5000)
                    assert any(a["type"] == "hidden-click"
                               for a in STATE["actions"])
                    rec("action_failure_recovery", "PASS",
                        "disabled->enabled->server-verified click")

                # --- fake DOM success rejected ---
                try:
                    page.fill("#no-such-field", "x", timeout=2000)
                    rec("fake_dom_success", "FAIL", "phantom fill passed?!")
                except Exception:
                    rec("fake_dom_success_rejected", "PASS",
                        "phantom selector raises, no success claimed")

                # --- 15: session expiration -> fail-closed -> re-login ---
                page.goto(base + "/expire")
                page.context.clear_cookies()
                page.goto(base + "/needs-auth")
                assert page.locator("#u").count() == 1, \
                    "expected login page after expiry"
                rec("session_expiration", "PASS",
                    "expired session lands on login (fail-closed)")
                _login(page, base)
                rec("session_recovery", "PASS", "re-login restores loop")

                # --- 16: crash/reconnect with SAME disposable profile ---
                tok = gate.permit("draft", "type draft")
                assert gate.attempt("draft", "type draft", tok)
                page.fill("#name", "draft-before-crash")
                page.wait_for_timeout(300)  # let localStorage autosave
                ctx.close()  # simulated crash
                ctx2 = pw.chromium.launch_persistent_context(
                    profile, headless=True,
                    args=["--no-sandbox", "--disable-dev-shm-usage"])
                page2 = ctx2.new_page()
                _login(page2, base)
                assert page2.input_value("#name") == "draft-before-crash", \
                    "draft did not survive reconnect"
                rec("crash_reconnect", "PASS",
                    "disposable profile restored draft after restart")
                ctx2.close()
                ctx = None
            finally:
                try:
                    if ctx is not None:
                        ctx.close()
                except Exception:
                    pass
    finally:
        srv.shutdown()
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(json.dumps(
        {"time": time.strftime("%Y-%m-%dT%H:%M:%S"),
         "profile": "disposable-fixture-only",
         "tests": RESULTS}, indent=1))
    fails = [k for k, v in RESULTS.items() if v["verdict"] == "FAIL"]
    assert not fails, f"browser write FAILs: {fails}"
