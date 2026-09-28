"""Saga / compensation engine: multi-step work with undo on failure.

Forward chain: step_1 -> step_2 -> ... each step pairs an action with
a compensating undo. On mid-chain failure the engine runs compensations
in reverse for completed steps, then reports committed vs compensated
vs failed. Journals every transition to JSONL for audit. Compensation
best-effort is recorded honestly (a failing undo is reported, never
swallowed).

Only stdlib is used. Actions/undos are caller callables.
"""

from __future__ import annotations

import json
import time
from pathlib import Path


class Saga:
    """Forward actions with reverse compensations + journal."""

    def __init__(self, journal_path: str = "saga_runs.jsonl"):
        self._steps: list[dict] = []
        self._path = Path(journal_path)

    def add_step(self, name: str, action, compensate=None) -> None:
        """Register a step (compensate optional but recommended)."""
        if not callable(action):
            raise TypeError("action must be callable")
        if compensate is not None and not callable(compensate):
            raise TypeError("compensate must be callable or None")
        self._steps.append({"name": str(name), "action": action,
                            "compensate": compensate})

    def _journal(self, run: dict) -> None:
        self._path.parent.mkdir(parents=True, exist_ok=True)
        with open(self._path, "a", encoding="utf-8") as fh:
            fh.write(json.dumps(run, sort_keys=True, default=str) + "\n")

    def run(self, saga_id: str = "") -> dict:
        """Execute forward; compensate in reverse on first failure."""
        done, log = [], []
        failed_at = None
        for step in self._steps:
            try:
                result = step["action"]()
                done.append(step["name"])
                log.append({"step": step["name"], "phase": "done",
                            "result": result})
            except Exception as exc:  # noqa: BLE001 - compensate, report
                failed_at = step["name"]
                log.append({"step": step["name"], "phase": "failed",
                            "error": str(exc)})
                break
        compensated, comp_errors = [], []
        if failed_at is not None:
            for step in reversed(self._steps):
                if step["name"] not in done:
                    continue
                fn = step["compensate"]
                if fn is None:
                    comp_errors.append({"step": step["name"],
                                        "error": "no compensation defined"})
                    continue
                try:
                    fn()
                    compensated.append(step["name"])
                except Exception as exc:  # noqa: BLE001 - record honestly
                    comp_errors.append({"step": step["name"],
                                        "error": str(exc)})
        out = {"saga": str(saga_id), "ts": time.time(),
               "committed": failed_at is None, "failed_at": failed_at,
               "done": done, "compensated": compensated,
               "compensation_errors": comp_errors, "log": log}
        self._journal(out)
        return out
