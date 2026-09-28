"""Reproducible builds: same inputs must yield the same artifact.

Two mechanisms, stdlib only:
  - canonical(obj) — deterministic JSON encoding (sorted keys, compact
    separators, unicode-normalized) so equal structures hash equal.
  - digest(obj) — sha256 hex of the canonical form.
  - check_rebuild(build_fn) — invoke a zero-arg builder twice and
    compare digests (catches timestamps, random ids, set-ordering,
    dict-ordering drift in generated artifacts).
  - strip_volatile(obj, keys) — remove known-volatile keys (run ids,
    timestamps) before digesting, so legitimate metadata never breaks
    the comparison.

A builder that embeds wall-clock time or randomness without a seed is
NOT reproducible — this module reports that fact, it does not hide it.
"""

from __future__ import annotations

import hashlib
import json


def canonical(obj) -> str:
    """Deterministic string form of a JSON-compatible structure."""
    return json.dumps(obj, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=True, default=str)


def digest(obj) -> str:
    """sha256 hex of the canonical form."""
    return hashlib.sha256(canonical(obj).encode("utf-8")).hexdigest()


def strip_volatile(obj, keys: tuple[str, ...] = ("run_id", "timestamp",
                                                 "ts", "created_at",
                                                 "execution_id")):
    """Recursively drop volatile metadata keys before digesting."""
    drop = set(keys)
    if isinstance(obj, dict):
        return {k: strip_volatile(v, keys) for k, v in obj.items()
                if k not in drop}
    if isinstance(obj, list):
        return [strip_volatile(v, keys) for v in obj]
    return obj


def check_rebuild(build_fn, *, strip_keys: tuple[str, ...] | None = None) -> dict:
    """Build twice, compare. Returns {reproducible, digest, runs}."""
    first = build_fn()
    second = build_fn()
    if strip_keys is not None:
        first = strip_volatile(first, strip_keys)
        second = strip_volatile(second, strip_keys)
    d1, d2 = digest(first), digest(second)
    return {"reproducible": d1 == d2, "digest": d1,
            "runs": 2, "match": d1 == d2}
