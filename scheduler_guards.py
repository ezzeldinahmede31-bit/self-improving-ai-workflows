"""Scheduler guards: deadlock cycles, starvation aging, perf memory.

Complements the existing lease-recovery tick with three platform
invariants:
  - Deadlock: wait-for graph cycle detection over declared task
    dependencies (A waits B waits C waits A) — named cycle, no run.
  - Starvation: per-task wait aging; tasks skipped past the aging
    ceiling get priority boost + a flag for the operator.
  - Performance memory: per agent/model/skill rolling stats
    (success, latency, cost, tool errors, rework) feeding scheduler
    choice via best_for(task_kind) ranking.

Only stdlib is used. This module advises; the scheduler enforces.
"""

from __future__ import annotations

import time
from collections import defaultdict, deque


def find_cycle(wait_for: dict[str, list[str]]) -> list[str] | None:
    """First dependency cycle found (DFS), or None when acyclic."""
    WHITE, GRAY, BLACK = 0, 1, 2
    color = {node: WHITE for node in wait_for}
    stack: list[str] = []

    def visit(node: str) -> list[str] | None:
        color[node] = GRAY
        stack.append(node)
        for dep in wait_for.get(node, []):
            if dep not in color:
                continue
            if color[dep] == GRAY:
                return stack[stack.index(dep):] + [dep]
            if color[dep] == WHITE:
                hit = visit(dep)
                if hit:
                    return hit
        stack.pop()
        color[node] = BLACK
        return None

    for node in wait_for:
        if color[node] == WHITE:
            hit = visit(node)
            if hit:
                return hit
    return None


class StarvationWatch:
    """Wait aging with boost ceiling + operator flags."""

    def __init__(self, *, boost_after_s: float = 300.0):
        self._wait_since: dict[str, float] = {}
        self._boost_after = float(boost_after_s)

    def waiting(self, task_id: str, now: float | None = None) -> None:
        """Mark a task waiting (idempotent start of its clock)."""
        self._wait_since.setdefault(str(task_id),
                                    now if now is not None else time.time())

    def served(self, task_id: str) -> None:
        """Stop the clock when a task gets execution."""
        self._wait_since.pop(str(task_id), None)

    def starved(self, now: float | None = None) -> list[dict]:
        """Tasks past the aging ceiling, oldest first."""
        at = now if now is not None else time.time()
        late = [{"task": tid, "waited_s": round(at - t0, 1)}
                for tid, t0 in self._wait_since.items()
                if at - t0 >= self._boost_after]
        return sorted(late, key=lambda r: -r["waited_s"])


class PerfMemory:
    """Rolling per-agent/model/skill stats for scheduler ranking."""

    def __init__(self, window: int = 100):
        self._window = int(window)
        self._stats: dict[str, deque] = defaultdict(
            lambda: deque(maxlen=self._window))

    def record(self, key: str, *, ok: bool, latency_s: float = 0.0,
               cost: float = 0.0, tool_errors: int = 0,
               rework: int = 0) -> None:
        """Append one execution sample for an agent/model/skill key."""
        self._stats[str(key)].append(
            {"ok": bool(ok), "lat": float(latency_s), "cost": float(cost),
             "err": int(tool_errors), "rework": int(rework)})

    def summary(self, key: str) -> dict:
        """Aggregate rates for one key (empty store = unknown)."""
        rows = list(self._stats.get(str(key), []))
        if not rows:
            return {"key": str(key), "samples": 0}
        n = len(rows)
        return {"key": str(key), "samples": n,
                "success": round(sum(1 for r in rows if r["ok"]) / n, 3),
                "avg_latency": round(sum(r["lat"] for r in rows) / n, 3),
                "total_cost": round(sum(r["cost"] for r in rows), 6),
                "tool_errors": sum(r["err"] for r in rows),
                "rework": sum(r["rework"] for r in rows)}

    def best_for(self, keys: list[str], *, max_cost: float | None = None,
                 min_success: float = 0.0) -> str | None:
        """Top success rate within cost/success floors (None = no fit)."""
        scored = []
        for key in keys:
            s = self.summary(key)
            if s["samples"] == 0 or s["success"] < min_success:
                continue
            if max_cost is not None and s["total_cost"] > max_cost:
                continue
            scored.append((s["success"], -s["avg_latency"], key))
        if not scored:
            return None
        return sorted(scored, reverse=True)[0][2]
