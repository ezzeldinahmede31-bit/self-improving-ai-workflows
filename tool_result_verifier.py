"""Tool-result verification: never trust a bare 200.

A tool that answers {"booked": true} may be mistaken, stale, or
lying. This module enforces the verify-before-commit protocol: every
claimed result is re-checked by an INDEPENDENT checker (a re-read, a
second query, a predicate over fresh state) before the platform
commits dependent state. Verdicts append to a JSONL journal for audit.

Checkers are caller-supplied callables:
  checker(claimed) -> (bool, note)
Built-ins cover the common shapes (key presence, equality, predicate).
Only stdlib is used.
"""

from __future__ import annotations

import hashlib
import json
import time
from pathlib import Path


def _claim_hash(claimed) -> str:
    return hashlib.sha256(json.dumps(
        claimed, sort_keys=True, separators=(",", ":"),
        default=str).encode("utf-8")).hexdigest()


def has_keys(*keys: str):
    """Checker: claimed dict carries all named keys with set values."""
    def _check(claimed) -> tuple[bool, str]:
        if not isinstance(claimed, dict):
            return False, "claimed result is not an object"
        missing = [k for k in keys if claimed.get(k) in (None, "")]
        if missing:
            return False, f"missing keys: {missing}"
        return True, ""
    return _check


def matches(key: str, want) -> object:
    """Checker: claimed[key] equals an independently known value."""
    def _check(claimed) -> tuple[bool, str]:
        got = claimed.get(key) if isinstance(claimed, dict) else None
        if got == want:
            return True, ""
        return False, f"{key}={got!r} differs from verified {want!r}"
    return _check


class ResultVerifier:
    """Verify-before-commit journal for tool results."""

    def __init__(self, journal_path: str = "tool_verdicts.jsonl"):
        self._path = Path(journal_path)

    def verify(self, *, tool: str, claimed, checker,
               evidence: str = "") -> dict:
        """Run the checker; journal the verdict; return it."""
        if not callable(checker):
            raise TypeError("checker must be callable")
        try:
            ok, note = checker(claimed)
        except Exception as exc:  # noqa: BLE001 - fail closed by design
            ok, note = False, f"checker crashed: {exc}"
        verdict = {"ts": time.time(), "tool": str(tool),
                   "claim_hash": _claim_hash(claimed),
                   "verified": bool(ok), "note": str(note),
                   "evidence": str(evidence)}
        self._path.parent.mkdir(parents=True, exist_ok=True)
        with open(self._path, "a", encoding="utf-8") as fh:
            fh.write(json.dumps(verdict, sort_keys=True) + "\n")
        return verdict

    def commit_if_verified(self, *, tool: str, claimed, checker,
                           evidence: str = "",
                           commit_fn=None) -> dict:
        """Run checker; invoke commit_fn(claimed) ONLY on verified True.

        commit_fn absence with a verified result returns committed False
        (dry-run shape) so callers wire side effects explicitly.
        """
        verdict = self.verify(tool=tool, claimed=claimed, checker=checker,
                              evidence=evidence)
        if not verdict["verified"] or commit_fn is None:
            return {**verdict, "committed": False}
        try:
            commit_fn(claimed)
        except Exception as exc:  # noqa: BLE001 - record, do not hide
            return {**verdict, "committed": False,
                    "commit_error": str(exc)}
        return {**verdict, "committed": True}
