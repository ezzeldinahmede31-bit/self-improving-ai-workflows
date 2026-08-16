"""Confidence Calibrator — external-truth calibration of the weak model's
self-reported confidence (weak-model hardening protocol #3).

The model has no real self-knowledge: any confidence it voices is a linguistic
guess. The only honest calibration is MEASUREMENT: write down every
(stated_confidence, task_category) at HITL-decision time, record the actual
human/verifier outcome, then derive per-category accuracy.

Usage contract (this system is the feedback loop the design doc says is the
single most important piece):
    cal = ConfidenceCalibrator()
    req_id = cal.log_prediction(category, stated_confidence)   # at routing
    cal.record_outcome(req_id, accepted=True|False)            # when HITL decides
    threshold = cal.get_adjusted_threshold(category, base=0.5)
    effective = cal.effective_confidence(category, stated=0.8)

Interpretation: if the model says "0.8 confident" in a category where the real
human acceptance rate is 1/3, the calibrator returns an effective threshold that
DEMANDS bordering-on-certainty (escalate at much lower stated confidence).
"""

from __future__ import annotations

import json
import sqlite3
import threading
import uuid
from dataclasses import dataclass
from pathlib import Path
from typing import Any

DEFAULT_CAL_DB = Path(__file__).parent / "confidence_audit.db"
_LOCK = threading.Lock()

DEFAULT_BASE_THRESHOLD = 0.5     # standard hotline: accept cheap only if 0.5+
MIN_ACCURACY_FLOOR = 0.05        # avoid div-by-zero / absurd floors


class ConfidenceCalibrator:
    def __init__(self, db_path: str | Path = DEFAULT_CAL_DB):
        self.db_path = str(db_path)
        self._init_db()

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self) -> None:
        with _LOCK:
            conn = self._connect()
            conn.execute("""
                CREATE TABLE IF NOT EXISTS confidence_predictions (
                    prediction_id TEXT PRIMARY KEY,
                    task_category TEXT NOT NULL,
                    stated_confidence REAL NOT NULL,
                    accepted INTEGER,          -- 1/0; NULL until human decides
                    decided_at TEXT,
                    created_at TEXT NOT NULL DEFAULT (datetime('now'))
                )
            """)
            conn.execute("CREATE INDEX IF NOT EXISTS idx_conf_category "
                         "ON confidence_predictions(task_category)")
            conn.commit()
            conn.close()

    # ---------- write path : fed from hitl_gate decisions ----------

    def log_prediction(self, task_category: str, stated_confidence: float) -> str:
        """Log a model's stated confidence for a category BEFORE the outcome is
        known. Returns prediction_id that must accompany the outcome."""
        prediction_id = uuid.uuid4().hex[:16]
        conf = round(min(1.0, max(0.0, float(stated_confidence))), 3)
        with _LOCK:
            conn = self._connect()
            conn.execute(
                "INSERT INTO confidence_predictions "
                "(prediction_id, task_category, stated_confidence) VALUES (?, ?, ?)",
                (prediction_id, task_category, conf),
            )
            conn.commit()
            conn.close()
        return prediction_id

    def record_outcome(self, prediction_id: str, accepted: bool) -> None:
        """Record the TRUE outcome (from HITL approve/reject or verifier pass/
        fail). accepted=True means the artifact survived; False means the human
        /verifier rejected it."""
        with _LOCK:
            conn = self._connect()
            conn.execute(
                "UPDATE confidence_predictions SET accepted = ?, "
                "decided_at = datetime('now') WHERE prediction_id = ?",
                (1 if accepted else 0, prediction_id),
            )
            conn.commit()
            conn.close()

    # ---------- read path : adaptive threshold ----------

    @staticmethod
    def _accuracy(accepted_count: int, total_count: int) -> float:
        if total_count <= 0:
            return 1.0
        return accepted_count / total_count

    def _category_stats(self, task_category: str,
                        since: float = 0.3) -> dict:
        """History for one category among predictions whose stated confidence
        cleared the reporting floor (avoid noise from ultra-low claims)."""
        with _LOCK:
            conn = self._connect()
            rows = conn.execute(
                "SELECT stated_confidence, accepted FROM confidence_predictions "
                "WHERE task_category = ? AND accepted IS NOT NULL AND "
                "stated_confidence >= ?",
                (task_category, since),
            ).fetchall()
            conn.close()
        total = len(rows)
        accepted = sum(1 for r in rows if r["accepted"])
        return {"total": total, "accepted": accepted,
                "accuracy": self._accuracy(accepted, total)}

    def effective_confidence(self, task_category: str, stated: float) -> float:
        """Discounted confidence: stated * historical accuracy. Without history
        accuracy == 1.0 so effective == stated (no penalty, no free pass)."""
        stats = self._category_stats(task_category)
        acc = max(MIN_ACCURACY_FLOOR, stats["accuracy"])
        return round(stated * acc, 3)

    def get_adjusted_threshold(
        self,
        task_category: str,
        base: float = DEFAULT_BASE_THRESHOLD,
        calibration_weight: float = 0.5,
    ) -> float:
        """Adaptive escalation threshold per category. When the category's real
        acceptance rate is low (model overconfident), the threshold is RAISED so
        the cascade escalates to frontier/HITL earlier. `calibration_weight`
        blends history with the base (0 => pure base; 1 => pure history)."""
        stats = self._category_stats(task_category)
        if stats["total"] == 0:
            return round(base, 3)
        # threshold rises as accuracy falls: less trusted => escalate more
        adjusted = base + calibration_weight * (1.0 - stats["accuracy"])
        return round(min(1.0, max(0.0, adjusted)), 3)

    def category_report(self, task_category: str) -> dict:
        stats = self._category_stats(task_category)
        return {
            "category": task_category,
            "predictions_resolved": stats["total"],
            "accepted": stats["accepted"],
            "accuracy": round(stats["accuracy"], 3),
            "base_threshold": DEFAULT_BASE_THRESHOLD,
            "adjusted_threshold": self.get_adjusted_threshold(task_category),
        }


def build_calibrated_cascade(
    calibrator: ConfidenceCalibrator,
    cheap_threshold: float = 0.35,
) -> Callable[[str, float, Callable], str]:
    """Wrap a cascade decision with calibration: given (task_category,
    stated_confidence) decide CHEAP vs ESCALATE using the ADAPTIVE threshold
    instead of the fixed one.

    Returns callable(category, stated_conf, cheap_fn) -> "CHEAP" | "ESCALATE".
    """
    def decide(category: str, stated_conf: float,
               cheap_fn: Callable[[], str]) -> str:
        adjusted = calibrator.get_adjusted_threshold(
            category, base=cheap_threshold)
        if stated_conf < adjusted:
            return "ESCALATE"
        return cheap_fn()

    return decide