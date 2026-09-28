"""Provenance / lineage: requirement-to-deploy chain per artifact.

Every built artifact answers "why is this node shaped this way?" via an
explicit link chain across stages:
  requirement -> research -> decision -> task -> agent -> model ->
  skill -> code -> workflow -> test -> deployment
Links accrue incrementally (`link()`), read back in stage order
(`trace()`), and completeness is asserted before delivery
(`gaps(required)`). Storage is a caller-chosen JSONL file
(`provenance_chain.jsonl` default) — append-only, separate from any
existing database, re-indexed into memory on load.

Only stdlib is used.
"""

from __future__ import annotations

import json
import time
from pathlib import Path

STAGES = ("requirement", "research", "decision", "task", "agent",
          "model", "skill", "code", "workflow", "test", "deployment")


class ProvenanceLog:
    """Append-only lineage records with gap analysis."""

    def __init__(self, path: str = "provenance_chain.jsonl"):
        self._path = Path(path)
        self._index: dict[str, dict[str, list[dict]]] = {}
        self._load()

    def _load(self) -> None:
        if not self._path.is_file():
            return
        try:
            lines = self._path.read_text(encoding="utf-8").splitlines()
        except OSError:
            return
        for line in lines:
            try:
                rec = json.loads(line)
            except ValueError:
                continue
            if (isinstance(rec, dict) and rec.get("artifact")
                    and rec.get("stage") in STAGES):
                self._index.setdefault(rec["artifact"], {}).setdefault(
                    rec["stage"], []).append(rec)

    def link(self, artifact_id: str, stage: str, ref: str,
             note: str = "") -> dict:
        """Record one stage link for an artifact."""
        if stage not in STAGES:
            raise ValueError(f"stage must be one of {STAGES}")
        rec = {"artifact": str(artifact_id), "stage": stage,
               "ref": str(ref), "note": str(note), "ts": time.time()}
        self._path.parent.mkdir(parents=True, exist_ok=True)
        with open(self._path, "a", encoding="utf-8") as fh:
            fh.write(json.dumps(rec, sort_keys=True) + "\n")
        self._index.setdefault(rec["artifact"], {}).setdefault(
            stage, []).append(rec)
        return rec

    def trace(self, artifact_id: str) -> list[dict]:
        """Links in canonical stage order (earliest first per stage)."""
        stages = self._index.get(str(artifact_id), {})
        out = []
        for stage in STAGES:
            out.extend(sorted(stages.get(stage, []),
                              key=lambda r: r.get("ts", 0)))
        return out

    def gaps(self, artifact_id: str,
             required: tuple[str, ...] = STAGES) -> list[str]:
        """Required stages with zero links (delivery blockers)."""
        stages = self._index.get(str(artifact_id), {})
        return [s for s in required if not stages.get(s)]

    def artifacts(self) -> list[str]:
        """All artifact ids holding one link or more."""
        return sorted(self._index)
