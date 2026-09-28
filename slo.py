"""SLO engine: declare targets, evaluate windows, burn alerts.

Targets like availability >= 99.9%, tool success >= 99%, p95 latency
under a ceiling are registered per service; observations feed bounded
windows; evaluate() compares window aggregates vs targets and raises
ok / at-risk / breached with burn multiples. Alerts name the target,
the window, and the observed value — evidence a human can act on.

Only stdlib is used. Percentiles computed by nearest-rank on the
window (honest for small samples; windows are bounded by design).
"""

from __future__ import annotations

from collections import deque


def _percentile(vals: list[float], pct: float) -> float:
    if not vals:
        return 0.0
    ordered = sorted(vals)
    rank = min(len(ordered) - 1, max(0, int(len(ordered) * pct / 100.0)))
    return ordered[rank]


class SLOEngine:
    """Target registry + windowed evaluation + burn states."""

    def __init__(self, window: int = 200):
        if window <= 0:
            raise ValueError("window must be positive")
        self._window = int(window)
        self._targets: dict[str, dict] = {}
        self._series: dict[str, deque] = {}

    def add_target(self, service: str, metric: str, *, op: str,
                   threshold: float, kind: str = "rate") -> None:
        """Register one target. op: >= or <=. kind: rate|p95|avg|max."""
        if op not in (">=", "<="):
            raise ValueError("op must be >=|<=")
        if kind not in ("rate", "p95", "avg", "max"):
            raise ValueError("kind must be rate|p95|avg|max")
        key = f"{service}:{metric}"
        self._targets[key] = {"service": str(service), "metric": str(metric),
                              "op": op, "threshold": float(threshold),
                              "kind": kind}
        self._series.setdefault(key, deque(maxlen=self._window))

    def observe(self, service: str, metric: str, value: float,
                *, good: bool | None = None) -> None:
        """Record one sample. rate-kind uses good flags; others raw values."""
        key = f"{service}:{metric}"
        if key not in self._targets:
            raise KeyError(f"no target: {key}")
        kind = self._targets[key]["kind"]
        if kind == "rate":
            if good is None:
                raise ValueError("rate observations need good=True|False")
            self._series[key].append(1.0 if good else 0.0)
        else:
            self._series[key].append(float(value))

    def _aggregate(self, key: str) -> float | None:
        vals = list(self._series.get(key, []))
        if not vals:
            return None
        kind = self._targets[key]["kind"]
        if kind == "rate":
            return sum(vals) / len(vals)
        if kind == "p95":
            return _percentile(vals, 95)
        if kind == "avg":
            return sum(vals) / len(vals)
        return max(vals)

    def evaluate(self, service: str, metric: str,
                 *, min_samples: int = 20) -> dict:
        """ok / at-risk (within 10% of edge) / breached for one target."""
        key = f"{service}:{metric}"
        spec = self._targets.get(key)
        if spec is None:
            return {"target": key, "state": "unknown"}
        vals = list(self._series.get(key, []))
        if len(vals) < min_samples:
            return {"target": key, "state": "warming",
                    "samples": len(vals)}
        cur = self._aggregate(key)
        thr, op = spec["threshold"], spec["op"]
        met = (cur >= thr) if op == ">=" else (cur <= thr)
        if op == ">=":
            near = (cur < thr) and (cur >= thr * 0.9)
        else:
            near = (cur <= thr) and (cur >= thr * 0.9)
        state = "ok" if met else "breached"
        if met and near:
            state = "at-risk"
        return {"target": key, "state": state, "observed": round(cur, 4),
                "threshold": thr, "op": op, "samples": len(vals)}

    def evaluate_all(self, *, min_samples: int = 20) -> dict:
        """Every target's verdict (breaches listed first by insertion)."""
        return {k: self.evaluate(*k.split(":", 1), min_samples=min_samples)
                for k in self._targets}
