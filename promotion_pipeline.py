"""Governed promotion pipeline: candidates earn trust in stages.

Self-improvement must never equal self-modification without control.
A candidate (skill, rule, prompt, config) advances ONLY through:
  scan -> unit test -> regression -> sandbox run -> evaluation ->
  approval -> promote
Each stage is a caller-supplied fn(candidate) -> (ok, note). The
first failing stage halts the run with a full stage report; promote()
executes solely after an explicit approval-stage pass. Reports append
to a JSONL journal for audit.

Only stdlib is used. Stage functions run in-process; sandbox-relevant
work belongs inside the candidate's own sandbox stage fn.
"""

from __future__ import annotations

import json
import time
from pathlib import Path

STAGES = ("scan", "unit", "regression", "sandbox", "eval", "approval",
          "promote")


class PromotionPipeline:
    """Staged candidate promotion with halt-on-first-failure."""

    def __init__(self, journal_path: str = "promotion_runs.jsonl"):
        self._path = Path(journal_path)

    def run(self, candidate_id: str, candidate, stages: dict) -> dict:
        """Execute the chain. Returns {promoted, halted_at, stages}."""
        report: dict = {"candidate": str(candidate_id), "ts": time.time(),
                        "stages": {}, "promoted": False, "halted_at": None}
        for stage in STAGES:
            fn = stages.get(stage)
            if fn is None:
                report["stages"][stage] = {"ok": False,
                                           "note": "stage missing: halt"}
                report["halted_at"] = stage
                break
            if stage == "promote" and report["stages"].get(
                    "approval", {}).get("ok") is not True:
                report["stages"][stage] = {
                    "ok": False,
                    "note": "promote refused: no approval pass on record"}
                report["halted_at"] = stage
                break
            try:
                ok, note = fn(candidate)
            except Exception as exc:  # noqa: BLE001 - halt, do not hide
                ok, note = False, f"stage crashed: {exc}"
            report["stages"][stage] = {"ok": bool(ok), "note": str(note)}
            if not ok:
                report["halted_at"] = stage
                break
        else:
            report["promoted"] = True
        self._journal(report)
        return report

    def _journal(self, report: dict) -> None:
        self._path.parent.mkdir(parents=True, exist_ok=True)
        with open(self._path, "a", encoding="utf-8") as fh:
            fh.write(json.dumps(report, sort_keys=True,
                                default=str) + "\n")

    def history(self) -> list[dict]:
        """Past runs, newest last (read-only)."""
        if not self._path.is_file():
            return []
        out = []
        try:
            lines = self._path.read_text(encoding="utf-8").splitlines()
        except OSError:
            return []
        for line in lines:
            try:
                out.append(json.loads(line))
            except ValueError:
                continue
        return out
