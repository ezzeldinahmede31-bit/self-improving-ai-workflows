"""Requirement-to-test traceability: no requirement ships unproven.

Each requirement carries an id, a statement, and acceptance criteria.
Tests (with evidence refs) link to requirements; coverage() names the
unlinked remainder; assert_ready() blocks delivery while gaps remain.
Storage is a caller-chosen JSON file (traceability.json default) —
separate from any existing database.

Only stdlib is used.
"""

from __future__ import annotations

import json
import time
from pathlib import Path


class Traceability:
    """Requirement registry with test linkage and gap analysis."""

    def __init__(self, path: str = "traceability.json"):
        self._path = Path(path)
        self._reqs: dict[str, dict] = {}
        self._links: dict[str, list[dict]] = {}
        self._load()

    def _load(self) -> None:
        if not self._path.is_file():
            return
        try:
            data = json.loads(self._path.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            return
        if isinstance(data, dict):
            self._reqs = dict(data.get("requirements", {}) or {})
            self._links = dict(data.get("links", {}) or {})

    def save(self) -> None:
        """Persist registry + links (creates parent dirs)."""
        self._path.parent.mkdir(parents=True, exist_ok=True)
        self._path.write_text(json.dumps(
            {"requirements": self._reqs, "links": self._links},
            sort_keys=True, indent=1), encoding="utf-8")

    def add_requirement(self, req_id: str, statement: str,
                        acceptance: list[str]) -> dict:
        """Register a requirement with acceptance criteria."""
        if not req_id or not statement:
            raise ValueError("id and statement are required")
        rec = {"id": str(req_id), "statement": str(statement),
               "acceptance": [str(a) for a in acceptance],
               "created_at": time.time()}
        self._reqs[rec["id"]] = rec
        return rec

    def link_test(self, req_id: str, test_ref: str, evidence: str = "") -> dict:
        """Attach a test (+ evidence pointer) to a requirement."""
        if req_id not in self._reqs:
            raise KeyError(f"unknown requirement: {req_id}")
        rec = {"test": str(test_ref), "evidence": str(evidence),
               "linked_at": time.time()}
        self._links.setdefault(req_id, []).append(rec)
        return rec

    def coverage(self) -> dict:
        """Linked vs unlinked requirement ids."""
        linked = sorted(r for r in self._reqs if self._links.get(r))
        unlinked = sorted(r for r in self._reqs if not self._links.get(r))
        total = len(self._reqs)
        rate = (len(linked) / total) if total else 1.0
        return {"total": total, "linked": linked, "unlinked": unlinked,
                "rate": rate}

    def assert_ready(self, required_ids: list[str] | None = None) -> dict:
        """Delivery gate: ok only when every required id has a test link."""
        want = list(required_ids) if required_ids is not None else list(
            self._reqs)
        gaps = [r for r in want
                if r not in self._reqs or not self._links.get(r)]
        unknown = [r for r in want if r not in self._reqs]
        return {"ok": not gaps, "gaps": gaps, "unknown": unknown}

    def requirement(self, req_id: str) -> dict | None:
        """Read one requirement with its test links attached."""
        rec = self._reqs.get(str(req_id))
        if rec is None:
            return None
        return {**rec, "tests": list(self._links.get(str(req_id), []))}
