"""Capacity planning: snapshots, headroom verdicts, growth math.

Operators answer "can today's fleet take 10x?" from numbers, not hope:
workers, in-flight executions, queue depth, CPU/RAM utilization, API
rate-limit headroom feed one snapshot; headroom() verdicts green /
tight / over against per-resource ceilings; forecast() applies a
growth multiple with a queueing-flavored latency multiplier
(1/(1-utilization) capped and labeled approximate) to say which
resource breaks first and at what multiple.

Only stdlib is used. Callers sample the OS; this module does the math.
"""

from __future__ import annotations


class CapacityPlanner:
    """Resource snapshots + headroom + first-breaker forecast."""

    def __init__(self, *, ceilings: dict | None = None):
        self._ceil = dict(ceilings or {"cpu": 0.75, "ram": 0.80,
                                       "queue": 100, "api": 0.80})
        self._snaps: list[dict] = []

    def snapshot(self, *, workers: int, in_flight: int, queue: int,
                 cpu: float, ram: float, api_used: float,
                 api_limit: float) -> dict:
        """Record one fleet snapshot (fractions 0..1 for cpu/ram)."""
        for name, val in (("cpu", cpu), ("ram", ram)):
            if not 0.0 <= float(val) <= 1.0:
                raise ValueError(f"{name} must be a 0..1 fraction")
        api_ratio = (float(api_used) / float(api_limit)
                     if api_limit > 0 else 0.0)
        rec = {"workers": int(workers), "in_flight": int(in_flight),
               "queue": int(queue), "cpu": float(cpu), "ram": float(ram),
               "api_ratio": api_ratio}
        self._snaps.append(rec)
        return rec

    def headroom(self, snap: dict | None = None) -> dict:
        """green / tight (>80% of any ceiling) / over (any ceiling hit)."""
        s = snap or (self._snaps[-1] if self._snaps else None)
        if s is None:
            return {"state": "unknown", "reason": "no snapshots"}
        usage = {"cpu": s["cpu"] / self._ceil["cpu"],
                 "ram": s["ram"] / self._ceil["ram"],
                 "queue": s["queue"] / self._ceil["queue"],
                 "api": s["api_ratio"] / self._ceil["api"]}
        worst = max(usage, key=usage.get)
        peak = usage[worst]
        if peak >= 1.0:
            state = "over"
        elif peak >= 0.8:
            state = "tight"
        else:
            state = "green"
        return {"state": state, "binding": worst,
                "usage": {k: round(v, 3) for k, v in usage.items()}}

    def forecast(self, multiple: float) -> dict:
        """Scale the latest snapshot; name the first-breaking resource."""
        if multiple <= 0:
            raise ValueError("multiple must be positive")
        if not self._snaps:
            return {"multiple": multiple, "breaks_at": None,
                    "reason": "no snapshots"}
        s = self._snaps[-1]
        scaled = {"cpu": s["cpu"] * multiple, "ram": s["ram"] * multiple,
                  "queue": s["queue"] * multiple,
                  "api_ratio": s["api_ratio"] * multiple}
        breaks = [k for k, v in
                  (("cpu", scaled["cpu"] / self._ceil["cpu"]),
                   ("ram", scaled["ram"] / self._ceil["ram"]),
                   ("queue", scaled["queue"] / self._ceil["queue"]),
                   ("api", scaled["api_ratio"] / self._ceil["api"]))
                  if v >= 1.0]
        util = min(0.99, scaled["cpu"])
        latency_x = round(1.0 / (1.0 - util), 2)  # approximate M/M/1 shape
        return {"multiple": multiple,
                "breaks": breaks or None,
                "first_breaker": breaks[0] if breaks else None,
                "latency_multiplier_approx": latency_x}
