"""Business invariant engine: domain rules checked per delivery.

Security asks "is it safe?", QA asks "does it run?", this module asks
"is it RIGHT?" — predicates like appointment.doctor == requested,
price == current list, timezone == operations zone. Predicates are
plain callables registered per domain; evaluate() runs them all and
reports pass/fail with reasons. A single failed invariant blocks the
delivery it guards (the caller enforces the block; this module
supplies the verdict).

Only stdlib is used. Predicates receive the delivery payload dict.
"""

from __future__ import annotations

from dataclasses import dataclass, field


def dotted(payload: dict, path: str, default=None):
    """Fetch nested values via 'a.b.c' paths (helper for predicates)."""
    cur = payload
    for part in str(path).split("."):
        if isinstance(cur, dict) and part in cur:
            cur = cur[part]
        else:
            return default
    return cur


@dataclass
class Invariant:
    domain: str
    name: str
    doc: str = ""


class InvariantEngine:
    """Registry + evaluator for business predicates."""

    def __init__(self):
        self._preds: dict[str, list[tuple[Invariant, object]]] = {}

    def register(self, domain: str, name: str, fn, doc: str = "") -> Invariant:
        """Register a predicate fn(payload) -> (bool, reason)."""
        if not callable(fn):
            raise TypeError("predicate must be callable")
        inv = Invariant(str(domain), str(name), str(doc))
        self._preds.setdefault(inv.domain, []).append((inv, fn))
        return inv

    def domains(self) -> list[str]:
        """Registered domain names."""
        return sorted(self._preds)

    def evaluate(self, domain: str, payload: dict) -> dict:
        """Run every predicate of a domain. Never raises on predicate bugs:
        a crashing predicate reports failed (fail-closed) with the error."""
        failed, passed = [], []
        for inv, fn in self._preds.get(str(domain), []):
            try:
                ok, reason = fn(payload)
            except Exception as exc:  # noqa: BLE001 - fail closed by design
                failed.append({"name": inv.name,
                               "reason": f"predicate crashed: {exc}"})
                continue
            if ok:
                passed.append(inv.name)
            else:
                failed.append({"name": inv.name, "reason": str(reason)})
        return {"domain": str(domain), "passed": passed, "failed": failed,
                "ok": not failed}

    @staticmethod
    def equals(path: str, want):
        """Predicate factory: dotted path must equal a fixed value."""
        def _check(payload: dict):
            got = dotted(payload, path, default=None)
            if got == want:
                return True, ""
            return False, f"{path}={got!r} expected {want!r}"
        return _check

    @staticmethod
    def one_of(path: str, options) -> object:
        """Predicate factory: dotted path must be among allowed options."""
        opts = list(options)

        def _check(payload: dict):
            got = dotted(payload, path, default=None)
            if got in opts:
                return True, ""
            return False, f"{path}={got!r} outside {opts!r}"
        return _check
