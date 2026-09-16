"""Per-attempt structured log: the evidence trail for every task.

One JSON line per attempt completion: task_id, worker ids, attempt number,
start/end, result, QA outcome, files changed, failure reason. The StateStore
events mirror this; the JSONL file is the human/audit-readable copy.
"""
from __future__ import annotations
import datetime
import json
import os


def _iso(ts: float) -> str:
    return datetime.datetime.fromtimestamp(ts).isoformat(timespec="seconds")


class TaskLog:
    def __init__(self, path: str):
        self.path = path
        os.makedirs(os.path.dirname(path) or ".", exist_ok=True)

    def emit(self, record: dict) -> None:
        rec = dict(record)
        rec.setdefault("logged_at", _iso(__import__("time").time()))
        with open(self.path, "a", encoding="utf-8") as fh:
            fh.write(json.dumps(rec, ensure_ascii=False) + "\n")

    def read_all(self) -> list[dict]:
        if not os.path.exists(self.path):
            return []
        out = []
        with open(self.path, encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if line:
                    out.append(json.loads(line))
        return out
