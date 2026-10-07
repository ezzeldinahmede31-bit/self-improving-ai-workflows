"""Safe browser-write E2E test app + permission gate (fixtures only).

Isolated local web app (127.0.0.1, ephemeral port) with a disposable test
account (test/test) — NEVER production accounts, cookies, or profiles.
The server records every received action so writes are verified INDEPENDENTLY
of what the DOM claims.
"""
import json
import threading
import urllib.parse
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

STATE = {"actions": [], "session_valid": True, "drafts": {}}
TEST_USER = ("test", "test")
SESSION_COOKIE = "tbwsession=valid-test-session"


def reset():
    STATE["actions"] = []
    STATE["session_valid"] = True
    STATE["drafts"] = {}


PAGE = """<!doctype html><html><head><meta charset=utf-8><title>TBW App</title></head>
<body>
<h1>Test App</h1>
<div id="status">ready</div>
<form id="f1" action="/submit" method="post">
 <input id="name" name="name" type="text" value="">
 <input id="agree" name="agree" type="checkbox" value="yes">
 <select id="color" name="color"><option value="">--</option>
  <option value="red">red</option><option value="blue">blue</option></select>
 <input id="up" type="file" name="upfile">
 <button id="save" type="submit">Save</button>
</form>
<button id="toggle">Enable hidden</button>
<button id="hiddenBtn" disabled>Hidden action</button>
<button id="crash">Simulate stale (replace me)</button>
<div id="wiz">
 <div id="step1">Step 1 <input id="w1" value=""><button id="next">Next</button></div>
 <div id="step2" style="display:none">Step 2 <input id="w2" value="">
  <button id="finish">Finish</button></div>
</div>
<a id="pop" href="/popup" target="_blank">open popup</a>
<a id="dl" href="/download">download</a>
<a id="gone-link" href="/needs-auth">auth area</a>
<script>
const st = document.getElementById('status');
document.getElementById('f1').addEventListener('submit', async (e) => {
  e.preventDefault();
  const fd = new FormData(e.target);
  const r = await fetch('/submit', {method: 'POST', body: fd});
  st.textContent = 'saved:' + (await r.text());
});
document.getElementById('toggle').onclick = () => {
  document.getElementById('hiddenBtn').disabled = false; };
document.getElementById('hiddenBtn').onclick = async () => {
  const r = await fetch('/hidden', {method: 'POST'}); st.textContent = await r.text(); };
document.getElementById('crash').onclick = (e) => {
  const b = document.createElement('button'); b.id = 'crash'; b.textContent = 'replaced';
  b.onclick = () => { document.getElementById('status').textContent = 'replaced-clicked'; };
  e.target.replaceWith(b); };
document.getElementById('next').onclick = () => {
  document.getElementById('step1').style.display = 'none';
  document.getElementById('step2').style.display = 'block'; };
document.getElementById('finish').onclick = async () => {
  const v = document.getElementById('w2').value;
  const r = await fetch('/wizard?step2=' + encodeURIComponent(v), {method: 'POST'});
  st.textContent = 'wizard:' + (await r.text()); };
const draft = document.getElementById('name');
draft.value = localStorage.getItem('draft') || '';
draft.addEventListener('input', () => localStorage.setItem('draft', draft.value));
document.getElementById('up').addEventListener('change', async (e) => {
  const fd = new FormData(); fd.append('upfile', e.target.files[0]);
  const r = await fetch('/upload', {method: 'POST', body: fd});
  st.textContent = 'uploaded:' + (await r.text()); });
if (!document.cookie.includes('tbwsession')) {
  document.getElementById('status').textContent = 'LOGIN_REQUIRED'; }
</script>
</body></html>"""

LOGIN_PAGE = """<!doctype html><html><body><h1>Login</h1>
<form action="/login" method="post">
<input id="u" name="u"><input id="p" name="p" type="password">
<button id="go" type="submit">Login</button></form></body></html>"""


class H(BaseHTTPRequestHandler):
    def log_message(self, *a):
        pass

    def _authed(self):
        return "tbwsession=valid-test-session" in (self.headers.get("Cookie") or "")

    def _send(self, body, code=200, ctype="text/html", headers=None):
        raw = body.encode() if isinstance(body, str) else body
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(raw)))
        for k, v in (headers or {}).items():
            self.send_header(k, v)
        self.end_headers()
        self.wfile.write(raw)

    def do_GET(self):
        if self.path == "/":
            if not self._authed():
                return self._send(LOGIN_PAGE)
            return self._send(PAGE)
        if self.path == "/popup":
            return self._send("<html><body><h1 id='ph'>popup-ok</h1></body></html>")
        if self.path == "/download":
            if not self._authed():
                return self._send("denied", 403, "text/plain")
            STATE["actions"].append({"type": "download"})
            return self._send(b"col1,col2\n1,2\n", 200, "text/csv",
                              {"Content-Disposition":
                               "attachment; filename=test.csv"})
        if self.path == "/needs-auth":
            if not self._authed() or not STATE["session_valid"]:
                return self._send(LOGIN_PAGE)
            return self._send("<html><body>auth-ok</body></html>", 200)
        if self.path == "/expire":
            STATE["session_valid"] = False
            return self._send("expired", 200, "text/plain")
        return self._send("not found", 404, "text/plain")

    def do_POST(self):
        ln = int(self.headers.get("Content-Length") or 0)
        body = self.rfile.read(ln) if ln else b""
        ctype = self.headers.get("Content-Type") or ""
        if self.path == "/login":
            q = urllib.parse.parse_qs(body.decode())
            if (q.get("u", [""])[0], q.get("p", [""])[0]) == tuple(TEST_USER):
                STATE["session_valid"] = True
                return self._send("ok", 200, "text/plain",
                                   {"Set-Cookie": SESSION_COOKIE + "; Path=/"})
            return self._send("bad login", 403, "text/plain")
        if self.path == "/logout":
            STATE["session_valid"] = False
            return self._send("logged out", 200, "text/plain",
                               {"Set-Cookie": "tbwsession=; Max-Age=0; Path=/"})
        if not self._authed() or not STATE["session_valid"]:
            return self._send("LOGIN_REQUIRED", 401, "text/plain")
        if self.path == "/submit":
            if "multipart" in ctype:
                STATE["actions"].append({"type": "form", "size": len(body)})
            else:
                q = urllib.parse.parse_qs(body.decode())
                STATE["actions"].append({"type": "form",
                                         "name": q.get("name", [""])[0],
                                         "agree": q.get("agree", [""])[0],
                                         "color": q.get("color", [""])[0]})
            return self._send("ok", 200, "text/plain")
        if self.path == "/hidden":
            STATE["actions"].append({"type": "hidden-click"})
            return self._send("hidden-ok", 200, "text/plain")
        if self.path.startswith("/wizard"):
            q = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
            STATE["actions"].append({"type": "wizard",
                                     "step2": q.get("step2", [""])[0]})
            return self._send("done", 200, "text/plain")
        if self.path == "/upload":
            STATE["actions"].append({"type": "upload", "size": len(body),
                                     "has_name": b"filename=" in body})
            return self._send("file-ok", 200, "text/plain")
        return self._send("not found", 404, "text/plain")


def start_server():
    reset()
    srv = ThreadingHTTPServer(("127.0.0.1", 0), H)
    t = threading.Thread(target=srv.serve_forever, daemon=True)
    t.start()
    return srv, f"http://127.0.0.1:{srv.server_port}"
