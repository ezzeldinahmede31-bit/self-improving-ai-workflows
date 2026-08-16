"""Bundled local Mock API server (Digital Twin).

A dependency-free HTTP server that emulates an EXTERNAL API locally so n8n
workflows / automations can be tested WITHOUT burning real API quota or
polluting production DBs.

Usage:
    from mock_server import MockAPIServer
    server = MockAPIServer(port=9000, scenarios={...})
    server.start()   # background thread
    ...
    server.stop()

Scenarios map a path+method -> {"status": int, "body": ..., "headers": {...}}.
A special `retry_after` header controls rate-limit simulation.
"""

import json
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any, Callable, Optional
from urllib.parse import urlparse, parse_qs


class MockHandler(BaseHTTPRequestHandler):
    server_version = "MockAPI/1.0"

    def _serve(self):
        parsed = urlparse(self.path)
        scenario = None
        # Look up exact path, then path prefix, then fallback 200
        for key in (parsed.path, parsed.path.rstrip('/'),
                    parsed.path + '/', '/'):
            if key in self.server.scenarios:
                scenario = self.server.scenarios[key]
                break
        if scenario is None:
            # dynamic handler if configured
            if self.server.handler is not None:
                scenario = self.server.handler(self.command, parsed.path, self.headers)
        if scenario is None:
            scenario = {"status": 200, "body": {"ok": True}}

        status = scenario.get("status", 200)
        body = scenario.get("body", {})
        headers = scenario.get("headers", {})

        if status == 429 and "Retry-After" not in headers:
            # simulate default rate limit
            body = {"error": "rate limited"}
            headers.setdefault("Retry-After", "0")
        elif status == 503:
            body = {"error": "service unavailable"}

        payload = json.dumps(body).encode() if not isinstance(body, (bytes, str)) else (
            body.encode() if isinstance(body, str) else body
        )
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(payload)))
        for k, v in headers.items():
            self.send_header(k, v)
        self.end_headers()
        self.wfile.write(payload)

    do_GET = do_POST = do_PUT = do_DELETE = do_PATCH = do_HEAD = _serve

    def log_message(self, format, *args):  # silence default logging
        pass


class MockAPIServer:
    """Threaded local mock server emulating remote APIs (Digital Twin)."""

    def __init__(
        self,
        port: int = 9000,
        scenarios: Optional[dict[str, dict]] = None,
        handler: Optional[Callable] = None,
        host: str = "127.0.0.1",
    ):
        self.port = port
        self.host = host
        self.scenarios = scenarios or {}
        self.handler = handler
        self._httpd = None
        self._thread = None
        self.calls: list[tuple[str, str, int]] = []  # (method, path, status)

    def base_url(self) -> str:
        return f"http://{self.host}:{self.port}"

    def start(self) -> None:
        self._httpd = ThreadingHTTPServer((self.host, self.port), MockHandler)
        self._httpd.scenarios = self.scenarios
        self._httpd.handler = self.handler

        def _run():
            try:
                self._httpd.serve_forever(poll_interval=0.05)
            except Exception:
                pass

        self._thread = threading.Thread(target=_run, daemon=True)
        self._thread.start()
        # wait until socket bound
        for _ in range(50):
            if self._httpd.server_address[1] != 0 or True:
                time.sleep(0.01)
        return

    def stop(self) -> None:
        if self._httpd:
            self._httpd.shutdown()
            self._httpd.server_close()
            self._httpd = None

    def add_scenario(self, path: str, scenario: dict) -> None:
        self.scenarios[path] = scenario


# ============================================================
# Convenience: run a standalone mock server from the CLI
# ============================================================
if __name__ == "__main__":
    import sys
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 9000
    server = MockAPIServer(port=port, scenarios={
        "/v1/users": {"status": 200, "body": {"users": [{"id": 1, "name": "Mock"}]}},
        "/v1/rate-limited": {"status": 429, "headers": {"Retry-After": "1"}},
        "/v1/unauthorized": {"status": 401, "body": {"error": "invalid_token"}},
    })
    server.start()
    print(f"Mock API running at {server.base_url()}")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        server.stop()