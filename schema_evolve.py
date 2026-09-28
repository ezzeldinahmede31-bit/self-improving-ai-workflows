"""Schema evolution: additive-only migrations with dual-read safety.

Long-lived workflows outlive their schemas. Migrations register as
ordered (from_version -> to_version) transform functions; migrate()
walks the chain step by step (no jumps, no gaps). Compatibility audit
rejects breaking edits: dropped keys and narrowed types fail the
additive-only rule, so existing clients never break silently.
Dual-read helper serves old+new shapes during transition windows.

Only stdlib is used. Schemas are {key: type-name} dicts.
"""

from __future__ import annotations

WIDEN_OK = {("int", "float"), ("float", "str"), ("int", "str"),
            ("bool", "str")}


class SchemaRegistry:
    """Versioned schemas + ordered migrations + additive audit."""

    def __init__(self):
        self._schemas: dict[str, dict] = {}
        self._migrations: dict[tuple[str, str], object] = {}

    def declare(self, version: str, schema: dict) -> None:
        """Pin one schema version ({field: type-name})."""
        self._schemas[str(version)] = dict(schema)

    def add_migration(self, from_v: str, to_v: str, fn) -> None:
        """Register a single-step transform fn(record)->record."""
        if not callable(fn):
            raise TypeError("migration must be callable")
        self._migrations[(str(from_v), str(to_v))] = fn

    def versions(self) -> list[str]:
        """Declared versions in registration order."""
        return list(self._schemas)

    def audit_additive(self, from_v: str, to_v: str) -> dict:
        """Additive-only check: no dropped keys, no narrowed types."""
        old = self._schemas.get(str(from_v), {})
        new = self._schemas.get(str(to_v), {})
        dropped = [k for k in old if k not in new]
        narrowed = [k for k in old if k in new and old[k] != new[k]
                    and (old[k], new[k]) not in WIDEN_OK]
        ok = not dropped and not narrowed
        return {"ok": ok, "dropped": dropped, "narrowed": narrowed,
                "added": [k for k in new if k not in old]}

    def migrate(self, record: dict, from_v: str, to_v: str,
                versions: list[str]) -> dict:
        """Walk the version chain applying each registered step."""
        chain = list(versions)
        if from_v not in chain or to_v not in chain:
            raise KeyError("versions outside declared chain")
        i, j = chain.index(from_v), chain.index(to_v)
        if j < i:
            raise ValueError("downgrade migrations unsupported")
        cur = dict(record)
        for a, b in zip(chain[i:j], chain[i + 1:j + 1]):
            fn = self._migrations.get((a, b))
            if fn is None:
                raise KeyError(f"missing migration step {a}->{b}")
            cur = fn(cur)
        return cur

    def dual_read(self, record_v1: dict, record_v2: dict,
                  prefer: str = "v2") -> dict:
        """Serve both shapes during transition; prefer names the winner
        on key conflicts (loser kept under _legacy for debugging)."""
        if prefer == "v2":
            return {**record_v1, **record_v2,
                    "_legacy": {k: v for k, v in record_v1.items()
                                if k in record_v2 and record_v2[k] != v}}
        return {**record_v2, **record_v1,
                "_legacy": {k: v for k, v in record_v2.items()
                            if k in record_v1 and record_v1[k] != v}}
