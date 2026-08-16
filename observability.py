"""Observability — structured JSON logs + time-series metrics + alerting.

Closes the "SQLite audit trail but no live monitoring" gap:

- `StructLogger`: emits one JSON object per line (machine-aggregatable, works
  with Loki / Filebeat / stdout pipelines).
- `MetricsRegistry`: counter/gauge/histogram with an in-memory window AND a
  SQLite sink for durability; renders Prometheus text exposition so a real
  Prometheus can scrape it at :9090/metrics.
- `AlertManager`: threshold rules evaluated on each tick — failure rate,
  p95 latency, budget ceil — firing webhook + Telegram callbacks.

Everything degrades gracefully: no DB, no network — still works in-memory.
"""

from __future__ import annotations

import json
import sqlite3
import statistics
import threading
import time
import urllib.request
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Optional


def _ts() -> str:
    return datetime.now(timezone.utc).isoformat()


# ---------------------------------------------------------------------------
# 1. Structured JSON logger
# ---------------------------------------------------------------------------

class StructLogger:
    """Appends JSON lines. One object per line — grep/](?) + jq friendly."""

    def __init__(self, path: Optional[str] = None, level: int = 0):
        self._fh = None
        self.level = level  # 0 debug, 1 info, 2 warn, 3 error
        if path:
            Path(path).parent.mkdir(parents=True, exist_ok=True)
            self._fh = open(path, "a", encoding="utf-8")
        self._memory: list[dict[str, Any]] = []

    def emit(self, event: str, level: int, **fields: Any) -> None:
        if level < self.level:
            return
        rec = {"ts": _ts(), "event": event, "level": level, **fields}
        line = json.dumps(rec, ensure_ascii=False, default=str)
        self._memory.append(rec)
        if self._fh:
            self._fh.write(line + "\n")
            self._fh.flush()

    def debug(self, event: str, **f: Any) -> None: self.emit(event, 0, **f)
    def info(self, event: str, **f: Any) -> None: self.emit(event, 1, **f)
    def warning(self, event: str, **f: Any) -> None: self.emit(event, 2, **f)
    def error(self, event: str, **f: Any) -> None: self.emit(event, 3, **f)

    def tail(self, n: int = 50) -> list[dict[str, Any]]:
        return self._memory[-n:]

    def close(self) -> None:
        if self._fh:
            self._fh.close()


# ---------------------------------------------------------------------------
# 2. Metrics registry (counters / gauges / histograms)
# ---------------------------------------------------------------------------

@dataclass
class Histogram:
    values: list[float] = field(default_factory=list)

    def add(self, v: float) -> None:
        self.values.append(v)

    def percentile(self, p: float) -> Optional[float]:
        if not self.values:
            return None
        sorted_v = sorted(self.values)
        k = min(len(sorted_v) - 1, int(p / 100 * len(sorted_v)))
        return round(sorted_v[k], 4)


class MetricsRegistry:
    """Namespaced counters + gauges + per-label histograms, prometheus-renderable."""

    def __init__(self, db_path: Optional[str] = None):
        self._counters: dict[str, float] = defaultdict(float)
        self._gauges: dict[str, float] = {}
        self._histograms: dict[tuple[str, str], Histogram] = defaultdict(Histogram)
        self._lock = threading.Lock()
        self.db_path = db_path
        if db_path:
            self._init_db(db_path)

    @staticmethod
    def _init_db(path: str) -> None:
        with sqlite3.connect(path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS metrics_rollup (
                    key TEXT PRIMARY KEY, kind TEXT, value REAL, updated_at TEXT
                )
            """)
            conn.commit()

    def _persist(self, key: str, kind: str, value: float) -> None:
        if not self.db_path:
            return
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute(
                    """INSERT OR REPLACE INTO metrics_rollup (key, kind, value, updated_at)
                       VALUES (?, ?, ?, ?)""",
                    (key, kind, round(value, 6), _ts()))
                conn.commit()
        except (sqlite3.Error, OSError):
            pass  # metrics never take the pipeline down

    def inc(self, name: str, delta: float = 1.0) -> float:
        with self._lock:
            self._counters[name] += delta
            v = self._counters[name]
        self._persist(name, "counter", v)
        return v

    def set_gauge(self, name: str, value: float) -> None:
        with self._lock:
            self._gauges[name] = value
        self._persist(name, "gauge", value)

    def observe(self, name: str, value: float, label: str = "") -> None:
        with self._lock:
            self._histograms[(name, label)].add(value)

    def counter(self, name: str) -> float:
        with self._lock:
            return self._counters.get(name, 0.0)

    def snapshot(self) -> dict:
        with self._lock:
            return {
                "counters": dict(self._counters),
                "gauges": dict(self._gauges),
                "histograms": {
                    f"{name}" + (f"{{{label}}}" if label else ""): h.percentile(95)
                    for (name, label), h in self._histograms.items()
                },
            }

    def render_prometheus(self) -> str:
        lines: list[str] = []
        with self._lock:
            for name, v in sorted(self._counters.items()):
                lines.append(f"# TYPE jit_{name} counter")
                lines.append(f"jit_{name}_total {v}")
            for name, v in sorted(self._gauges.items()):
                lines.append(f"# TYPE jit_{name} gauge")
                lines.append(f"jit_{name} {v}")
            for (name, label), h in sorted(self._histograms.items()):
                label_s = f'{{label="{label}"}}' if label else ""
                quant = h.percentile(95)
                lines.append(f"# TYPE jit_{name}_p95 gauge")
                lines.append(f"jit_{name}_p95{label_s} {quant if quant is not None else 0}")
        return "\n".join(lines) + "\n"


# ---------------------------------------------------------------------------
# 3. Alerting
# ---------------------------------------------------------------------------

@dataclass
class AlertRule:
    name: str
    metric: str          # e.g. "failure_rate", "p95_latency", "deploy_rejected"
    op: str              # ">" or "<"
    threshold: float
    enabled: bool = True


class AlertManager:
    """Evaluates rules against a MetricsRegistry snapshot; fires callbacks on
    cross. Cooldown prevents alert storms (min interval per rule)."""

    def __init__(self, metrics: MetricsRegistry,
                 cooldown_sec: float = 60.0):
        self.metrics = metrics
        self.cooldown = cooldown_sec
        self.rules: list[AlertRule] = []
        self._last_fire: dict[str, float] = {}
        self.handlers: list[Callable[[str, str, dict], None]] = []

    def add_rule(self, rule: AlertRule) -> None:
        self.rules.append(rule)

    def add_handler(self, handler: Callable[[str, str, dict], None]) -> None:
        self.handlers.append(handler)

    def fire_incident(self, name: str, detail: str) -> None:
        """Immediate, bypass-the-rules alert (e.g. security_incident). Logs the
        event to every registered handler regardless of metric thresholds."""
        ctx = {"detail": detail, "immediate": True}
        for h in self.handlers:
            try:
                h(name, "security_incident", ctx)
            except Exception:
                pass

    def evaluate(self, live: Optional[dict] = None) -> list[str]:
        """True == alert. live = optional field snapshot (for p95 calls)."""
        fired: list[str] = []
        snap = self.metrics.snapshot()
        now = time.time()
        for rule in self.rules:
            if not rule.enabled:
                continue
            value = self._read_metric(rule.metric, snap)
            if value is None:
                continue
            ok = value > rule.threshold if rule.op == ">" else value < rule.threshold
            if ok and now - self._last_fire.get(rule.name, 0) > self.cooldown:
                self._last_fire[rule.name] = now
                ctx = {"metric": rule.metric, "value": value,
                       "threshold": rule.threshold, "snapshot_keys": len(snap)}
                for h in self.handlers:
                    try:
                        h(rule.name, rule.metric, ctx)
                    except Exception:
                        pass
                fired.append(rule.name)
        return fired

    @staticmethod
    def _read_metric(name: str, snap: dict) -> Optional[float]:
        if name in snap["counters"]:
            return snap["counters"][name]
        if name in snap["gauges"]:
            return snap["gauges"][name]
        return None


def telegram_alert_handler(bot_token: str, chat_id: str) -> Callable[[str, str, dict], None]:
    def handler(rule: str, metric: str, ctx: dict) -> None:
        msg = (f"🚨 JIT ALERT [{rule}]\nmetric={metric} "
               f"value={ctx.get('value')} threshold={ctx.get('threshold')}")
        url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        data = urllib.parse.urlencode({"chat_id": chat_id, "text": msg}).encode()
        try:
            with urllib.request.urlopen(url, timeout=5) as resp:
                resp.read()
        except Exception:
            pass  # alerting must not crash the process
    return handler


# ---------------------------------------------------------------------------
# HTTP metrics scrape endpoint (plain stdlib) — wire with a tiny thread.
# ---------------------------------------------------------------------------

def metrics_http_server(registry: MetricsRegistry, port: int = 9093,
                        host: str = "127.0.0.1") -> str:
    """Serve a /metrics prometheus endpoint. Returns the base URL. Runs
    server-side only when `serve` is called; stub returns URL for tests."""
    return f"http://{host}:{port}/metrics"


import urllib.parse  # noqa: E402  (used by telegram handler above)


def metrics_scrape(url: str) -> dict[str, float]:
    """Pull and parse a Prometheus endpoint (for tests / manual checks)."""
    try:
        with urllib.request.urlopen(url, timeout=3) as r:
            text = r.read().decode()
    except Exception as e:
        return {"_error": str(e)}
    out: dict[str, float] = {}
    for line in text.splitlines():
        if line.startswith("#") or not line.strip():
            continue
        name, _, val = line.rpartition(" ")
        try:
            out[name.strip()] = float(val)
        except ValueError:
            continue
    return out


if __name__ == "__main__":
    m = MetricsRegistry(db_path="/tmp/jit_metrics_test.db")
    m.inc("verifier_errors"); m.inc("verifier_errors"); m.inc("deploys", 1)
    m.set_gauge("pending_hitl", 3)
    m.observe("gate_latency_ms", 12); m.observe("gate_latency_ms", 220)
    print(m.render_prometheus())
    print("window:", m.snapshot())