"""Platform-wide idempotency: same request twice = same result.

Exactly-once effects via idempotency keys: the first execution runs
the operation and records (key -> result digest + result); replays
with the same key return the recorded result WITHOUT re-executing.
Keys scope to a namespace (tenant + operation family) so unrelated
flows never collide. Records persist to JSON for crash recovery.

Only stdlib is used. Operations are caller callables.
"""

from __future__ import annotations

import hashlib
import json
import time
from pathlib import Path


def _digest(result) -> str:
    return hashlib.sha256(json.dumps(
        result, sort_keys=True, separators=(",", ":"),
        default=str).encode("utf-8")).hexdigest()


class IdempotencyStore:
    """Keyed exactly-once execution records with replay."""

    def __init__(self, path: str = "idempotency.json"):
        self._path = Path(path)
        self._records: dict[str, dict] = {}
        self._load()

    def _load(self) -> None:
        if not self._path.is_file():
            return
        try:
            data = json.loads(self._path.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            return
        if isinstance(data, dict):
            self._records = {str(k): v for k, v in data.items()
                             if isinstance(v, dict)}

    def _save(self) -> None:
        self._path.parent.mkdir(parents=True, exist_ok=True)
        self._path.write_text(json.dumps(self._records, sort_keys=True,
                                         indent=1, default=str),
                              encoding="utf-8")

    @staticmethod
    def make_key(namespace: str, *parts) -> str:
        """Deterministic key from namespace + request fields."""
        blob = json.dumps([str(namespace)] + [str(p) for p in parts],
                          separators=(",", ":"))
        return hashlib.sha256(blob.encode("utf-8")).hexdigest()[:32]

    def execute(self, key: str, operation) -> dict:
        """Run once; replay returns the recorded result.

        Returns {executed: bool, result, digest}. A crashing operation
        records nothing, so retry re-executes (safe: no phantom success).
        """
        if not callable(operation):
            raise TypeError("operation must be callable")
        key = str(key)
        hit = self._records.get(key)
        if hit is not None:
            return {"executed": False, "result": hit["result"],
                    "digest": hit["digest"]}
        result = operation()
        rec = {"result": result, "digest": _digest(result),
               "ts": time.time()}
        self._records[key] = rec
        self._save()
        return {"executed": True, "result": result, "digest": rec["digest"]}

    def forget(self, key: str) -> bool:
        """Drop one record (explicit operator action)."""
        if str(key) in self._records:
            del self._records[str(key)]
            self._save()
            return True
        return False

    def keys(self) -> list[str]:
        """Stored keys (audit surface)."""
        return sorted(self._records)
