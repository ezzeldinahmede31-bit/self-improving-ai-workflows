"""Golden failure corpus: past failures must stay fixed.

Every real failure the platform ever hit becomes a permanent case:
reproducer + detector expectation + fix reference. gate_update() runs
the corpus against a candidate change and blocks on ANY regression —
new work must pass the present suite AND the entire failure history.
Cases persist to JSON; provenance links tie each case to its incident.

Only stdlib is used. Checks are caller callables (pure predicates).
"""

from __future__ import annotations

import json
import time
from pathlib import Path


class GoldenCorpus:
    """Append-mostly failure history with blocking gate runs."""

    def __init__(self, path: str = "golden_corpus.json"):
        self._path = Path(path)
        self._cases: dict[str, dict] = {}
        self._load()

    def _load(self) -> None:
        if not self._path.is_file():
            return
        try:
            data = json.loads(self._path.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            return
        if isinstance(data, dict):
            self._cases = {str(k): v for k, v in data.items()
                           if isinstance(v, dict)}

    def save(self) -> None:
        """Persist the corpus (creates parent dirs)."""
        self._path.parent.mkdir(parents=True, exist_ok=True)
        self._path.write_text(json.dumps(self._cases, sort_keys=True,
                                         indent=1, default=str),
                              encoding="utf-8")

    def add_case(self, case_id: str, *, reproducer: str, expect: str,
                 incident: str = "", fix_ref: str = "") -> dict:
        """Record one failure with its expectation + references."""
        if not reproducer or not expect:
            raise ValueError("reproducer and expect are required")
        rec = {"reproducer": str(reproducer), "expect": str(expect),
               "incident": str(incident), "fix_ref": str(fix_ref),
               "added_at": time.time()}
        self._cases[str(case_id)] = rec
        return rec

    def gate_update(self, checks: dict) -> dict:
        """Run checks {case_id: fn() -> (ok, note)}; block on any miss.

        Unknown case ids in checks are ignored; corpus cases WITHOUT a
        check are reported uncovered (a gate hole, not a pass).
        """
        passed, failed, uncovered = [], [], []
        for cid in self._cases:
            fn = checks.get(cid)
            if fn is None:
                uncovered.append(cid)
                continue
            if not callable(fn):
                failed.append({"case": cid, "note": "check not callable"})
                continue
            try:
                ok, note = fn()
            except Exception as exc:  # noqa: BLE001 - fail the case
                ok, note = False, f"check raised: {exc}"
            (passed if ok else failed).append(
                {"case": cid, "note": str(note)} if not ok else cid)
        passed_ids = [p if isinstance(p, str) else p["case"] for p in passed]
        blocked = bool(failed) or bool(uncovered)
        return {"blocked": blocked, "passed": passed_ids, "failed": failed,
                "uncovered": uncovered, "total": len(self._cases)}
