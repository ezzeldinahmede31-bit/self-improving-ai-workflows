"""LoRA dataset exporter — #8.

Once you have hundreds of HITL-approved (+ rejected) examples, a narrow LoRA
fine-tune of the weak model on "n8n workflow construction" can beat a general
frontier model on THIS task. This module turns the accumulated artifacts into a
training-ready JSONL corpus (instruction / input / output / rejected?).

Honesty: we don't train here. We BUILD the dataset from real approvals/rejects
so a LoRA job (Unsloth/axolotl) can consume it later. Until then, the same
JSONL powers the few-shot assembler — zero waste.
"""

from __future__ import annotations

import json
import sqlite3
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from rag_engine import RagMemory, RAG_DB


@dataclass
class DatasetStats:
    total: int
    positive: int
    negative: int
    by_source: dict


class LoRADatasetExporter:
    def __init__(self, rag: Optional[RagMemory] = None,
                 feedback_db: Optional[str] = None):
        self.rag = rag or RagMemory()
        self.feedback_db = feedback_db

    def _approved_examples(self) -> list[dict]:
        conn = sqlite3.connect(self.rag.db_path)
        conn.row_factory = sqlite3.Row
        rows = conn.execute(
            "SELECT title, content FROM rag_docs "
            "WHERE source = 'approved-workflow' AND approved = 1").fetchall()
        conn.close()
        out = []
        for r in rows:
            try:
                workflow = json.loads(r["content"])
            except json.JSONDecodeError:
                workflow = {"_raw": r["content"]}
            out.append({"instruction": r["title"] or "build the workflow",
                        "input": "", "output": workflow,
                        "rejected": False})
        return out

    def _rejected_lessons(self) -> list[dict]:
        if not self.feedback_db:
            return []
        path = Path(self.feedback_db)
        if not path.exists():
            return []
        conn = sqlite3.connect(str(path))
        conn.row_factory = sqlite3.Row
        rows = conn.execute(
            "SELECT rule, count, last_reason FROM rejection_patterns "
            "ORDER BY count DESC LIMIT 200").fetchall()
        conn.close()
        return [{
            "instruction": f"Avoid generating patterns that trigger rule '{r['rule']}'",
            "input": r["last_reason"] or "",
            "output": {"action": "reject", "rule": r["rule"],
                       "count": r["count"]},
            "rejected": True,
        } for r in rows]

    def export_jsonl(self, out_path: str | Path) -> DatasetStats:
        """Write the full corpus as JSONL (one example per line)."""
        positives = self._approved_examples()
        negatives = self._rejected_lessons()
        rows = positives + negatives
        with open(out_path, "w", encoding="utf-8") as f:
            for ex in rows:
                f.write(json.dumps(ex, ensure_ascii=False, default=str) + "\n")
        return DatasetStats(
            total=len(rows),
            positive=len(positives),
            negative=len(negatives),
            by_source={"approved-workflow": len(positives),
                       "feedback-rejections": len(negatives)},
        )

    def few_shot_from_corpus(self, limit: int = 4) -> str:
        """Reuse the same corpus as few-shot without writing a file."""
        lines = []
        for ex in self._approved_examples()[:limit]:
            out_s = json.dumps(ex["output"])[:200]
            lines.append(f"- {ex['instruction']} => {out_s}")
        for ex in self._rejected_lessons()[:limit]:
            lines.append(f"- NEVER: {ex['output'].get('rule')} "
                         f"(rejected {ex['output'].get('count')}x)")
        return "\n".join(lines) or ""


if __name__ == "__main__":
    import tempfile
    exp = LoRADatasetExporter(feedback_db=str(Path(tempfile.mkdtemp()) / "fb.db"))
    out = Path(tempfile.mkdtemp()) / "lora.jsonl"
    stats = exp.export_jsonl(out)
    print(stats)
    print(out.read_text()[:300])