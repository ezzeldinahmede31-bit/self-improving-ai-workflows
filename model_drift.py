"""Model drift detection: catch silent behavior changes early.

Providers swap weights and behavior drifts: tool success yesterday
98%, today 89%. This module pins a baseline per metric, observes a
bounded window of fresh samples, and raises drifted with a recommended
action (watch / fallback / rollback) when the window mean leaves the
allowed band. Bands are absolute, relative, or both — configured per
metric, never global magic numbers.

Only stdlib is used. No network calls.
"""

from __future__ import annotations

from collections import deque


class DriftMonitor:
    """Per-metric baselines with windowed drift verdicts."""

    def __init__(self, window: int = 50):
        if window <= 0:
            raise ValueError("window must be positive")
        self._window = int(window)
        self._base: dict[str, dict] = {}
        self._samples: dict[str, deque] = {}

    def pin_baseline(self, metric: str, value: float, *,
                     abs_tol: float = 0.05, rel_tol: float = 0.10,
                     direction: str = "both") -> None:
        """Pin the reference value and tolerance band for a metric.

        direction: "both" | "drop" (only worsening trips) | "rise".
        """
        if direction not in ("both", "drop", "rise"):
            raise ValueError("direction must be both|drop|rise")
        self._base[str(metric)] = {"value": float(value),
                                   "abs_tol": float(abs_tol),
                                   "rel_tol": float(rel_tol),
                                   "direction": direction}
        self._samples.setdefault(str(metric), deque(maxlen=self._window))

    def observe(self, metric: str, value: float) -> None:
        """Append one fresh sample to the metric window."""
        key = str(metric)
        if key not in self._base:
            raise KeyError(f"no baseline pinned for {key}")
        self._samples[key].append(float(value))

    def mean(self, metric: str) -> float | None:
        """Current window mean, or None when the window is empty."""
        vals = list(self._samples.get(str(metric), []))
        if not vals:
            return None
        return sum(vals) / len(vals)

    def check(self, metric: str, *, min_samples: int = 10) -> dict:
        """Verdict for one metric: ok / drifted + recommended action."""
        key = str(metric)
        base = self._base.get(key)
        if base is None:
            return {"metric": key, "state": "unknown",
                    "reason": "no baseline"}
        vals = list(self._samples.get(key, []))
        if len(vals) < min_samples:
            return {"metric": key, "state": "warming",
                    "samples": len(vals), "need": min_samples}
        cur = sum(vals) / len(vals)
        ref = base["value"]
        gap = cur - ref
        tripped = (abs(gap) > base["abs_tol"]
                   or (abs(gap) > abs(ref) * base["rel_tol"] if ref else False))
        direction = base["direction"]
        bad_direction = (direction == "both"
                         or (direction == "drop" and gap < 0)
                         or (direction == "rise" and gap > 0))
        if tripped and bad_direction:
            mag = abs(gap) / (abs(ref) if ref else 1.0)
            action = "rollback" if mag > 0.25 else "fallback"
            return {"metric": key, "state": "drifted",
                    "baseline": ref, "current": round(cur, 4),
                    "action": action}
        return {"metric": key, "state": "ok", "baseline": ref,
                "current": round(cur, 4)}

    def check_all(self, *, min_samples: int = 10) -> dict:
        """Verdicts for every pinned metric."""
        return {m: self.check(m, min_samples=min_samples)
                for m in self._base}
