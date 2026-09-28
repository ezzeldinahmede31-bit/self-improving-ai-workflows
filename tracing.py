"""Distributed tracing: one trace-id across every hop.

A trace starts at ingress (telegram/webhook/chat) and propagates as a
(trace_id, span_id, parent_id) triple through n8n -> AI -> tool ->
store hops. Spans append to JSONL with start/end timestamps so any
"where did the seconds go?" question answers from the log: per-span
latencies plus the critical path. Context vars keep concurrent traces
isolated without threading state through every signature.

Only stdlib is used.
"""

from __future__ import annotations

import contextvars
import json
import secrets
import time
from pathlib import Path

_current: contextvars.ContextVar = contextvars.ContextVar(
    "trace_ctx", default=None)


def _nid(n: int = 8) -> str:
    return secrets.token_hex(n)


class Tracer:
    """Trace factory + span recorder with JSONL sink."""

    def __init__(self, path: str = "traces.jsonl"):
        self._path = Path(path)

    def start_trace(self, *, name: str, meta: dict | None = None) -> dict:
        """Begin a trace; install it as the ambient context."""
        ctx = {"trace_id": _nid(12), "span_id": _nid(6),
               "parent_id": None, "name": str(name),
               "meta": dict(meta or {}), "t0": time.time()}
        _current.set(ctx)
        return {"trace_id": ctx["trace_id"], "span_id": ctx["span_id"]}

    def span(self, name: str):
        """Context manager recording one span under the ambient trace."""
        return _Span(self, name)

    def current_ids(self) -> dict | None:
        """Ambient (trace_id, span_id) for header propagation."""
        ctx = _current.get()
        if ctx is None:
            return None
        return {"trace_id": ctx["trace_id"], "span_id": ctx["span_id"]}

    def adopt(self, trace_id: str, parent_span: str,
              name: str = "hop") -> dict:
        """Continue a trace from propagated ids (downstream service)."""
        ctx = {"trace_id": str(trace_id), "span_id": _nid(6),
               "parent_id": str(parent_span), "name": str(name),
               "meta": {}, "t0": time.time()}
        _current.set(ctx)
        return {"trace_id": ctx["trace_id"], "span_id": ctx["span_id"]}

    def _emit(self, rec: dict) -> None:
        self._path.parent.mkdir(parents=True, exist_ok=True)
        with open(self._path, "a", encoding="utf-8") as fh:
            fh.write(json.dumps(rec, sort_keys=True, default=str) + "\n")

    def report(self, trace_id: str) -> dict:
        """Spans + per-span latency + critical-path total for one trace."""
        if not self._path.is_file():
            return {"trace_id": trace_id, "spans": [], "total_s": 0.0}
        spans = []
        try:
            lines = self._path.read_text(encoding="utf-8").splitlines()
        except OSError:
            lines = []
        for line in lines:
            try:
                rec = json.loads(line)
            except ValueError:
                continue
            if rec.get("trace_id") == trace_id:
                spans.append(rec)
        spans.sort(key=lambda r: r.get("t0", 0))
        total = round(sum(s.get("dur_s", 0.0) for s in spans), 3)
        return {"trace_id": trace_id, "spans": spans, "total_s": total}


class _Span:
    def __init__(self, tracer: Tracer, name: str):
        self._tracer = tracer
        self._name = str(name)
        self._token = None
        self._t0 = 0.0
        self._ctx = None

    def __enter__(self):
        parent = _current.get()
        self._ctx = {"trace_id": parent["trace_id"] if parent else _nid(12),
                     "span_id": _nid(6),
                     "parent_id": parent["span_id"] if parent else None,
                     "name": self._name, "t0": time.time()}
        self._t0 = self._ctx["t0"]
        self._token = _current.set(self._ctx)
        return self

    def __exit__(self, *exc):
        dur = time.time() - self._t0
        self._tracer._emit({"trace_id": self._ctx["trace_id"],
                            "span_id": self._ctx["span_id"],
                            "parent_id": self._ctx["parent_id"],
                            "name": self._ctx["name"], "t0": self._t0,
                            "dur_s": round(dur, 4)})
        _current.reset(self._token)
        return False
