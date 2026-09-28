"""Spec + docs drift: implementation must match its promises.

Two drift classes, stdlib only:
  - SpecDrift: pin spec statements (hashes); re-assert live behavior
    probes on schedule — a changed behavior with an unchanged spec (or
    vice versa) opens a drift finding (e.g. reminder moved 24h -> 12h).
  - DocsDrift: cross-check code symbols (def/class names via ast)
    against doc mentions; symbols missing from docs and docs naming
    absent symbols both surface (neither direction trusted blindly).

Only stdlib is used (ast for the code side; plain text for docs).
"""

from __future__ import annotations

import ast
import hashlib
import re
import time


def _sha(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


class SpecDrift:
    """Pinned spec statements vs live behavior probes."""

    def __init__(self):
        self._specs: dict[str, dict] = {}
        self._probes: dict[str, object] = {}
        self.findings: list[dict] = []

    def pin(self, spec_id: str, statement: str) -> None:
        """Freeze one spec promise (hash + text)."""
        self._specs[str(spec_id)] = {"text": str(statement),
                                     "sha": _sha(str(statement))}

    def attach(self, spec_id: str, probe) -> None:
        """Bind a behavior probe fn() -> observed-string."""
        if spec_id not in self._specs:
            raise KeyError(f"unpinned spec: {spec_id}")
        if not callable(probe):
            raise TypeError("probe must be callable")
        self._probes[str(spec_id)] = probe

    def check(self, spec_id: str) -> dict:
        """Probe now; drift = observed differs from pinned text."""
        spec = self._specs.get(str(spec_id))
        if spec is None:
            return {"spec": str(spec_id), "drift": None,
                    "reason": "unpinned"}
        fn = self._probes.get(str(spec_id))
        if fn is None:
            return {"spec": str(spec_id), "drift": None,
                    "reason": "no probe bound"}
        try:
            observed = str(fn())
        except Exception as exc:  # noqa: BLE001 - finding, not crash
            finding = {"spec": str(spec_id), "ts": time.time(),
                       "kind": "probe-raised", "detail": str(exc)}
            self.findings.append(finding)
            return {"spec": str(spec_id), "drift": True,
                    "finding": finding}
        if _sha(observed) != spec["sha"] and observed != spec["text"]:
            finding = {"spec": str(spec_id), "ts": time.time(),
                       "kind": "behavior-moved",
                       "pinned": spec["text"][:120],
                       "observed": observed[:120]}
            self.findings.append(finding)
            return {"spec": str(spec_id), "drift": True,
                    "finding": finding}
        return {"spec": str(spec_id), "drift": False}


class DocsDrift:
    """Code symbols vs documentation mentions, both directions."""

    @staticmethod
    def code_symbols(python_source: str) -> set[str]:
        """Top-level def/class names via ast (syntax errors -> empty)."""
        try:
            tree = ast.parse(python_source)
        except SyntaxError:
            return set()
        return {node.name for node in tree.body
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef,
                                     ast.ClassDef))}

    @staticmethod
    def check(symbols: set[str], doc_text: str) -> dict:
        """Undocumented symbols + phantom doc names (word-boundary)."""
        doc = str(doc_text)
        undocumented = sorted(s for s in symbols
                              if not re.search(r"\b" + re.escape(s) + r"\b",
                                               doc))
        mentioned = set(re.findall(r"[A-Za-z_][A-Za-z0-9_]*", doc))
        phantom = sorted(m for m in mentioned
                         if m not in symbols and len(m) > 12
                         and "_" in m)
        return {"undocumented": undocumented, "phantom": phantom}
