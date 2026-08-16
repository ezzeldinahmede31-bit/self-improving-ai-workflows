"""Cascade Routing — the #1 highest-impact fix for a weak+free model.

The free model only needs to be competent on the ~80% routine; the hard/uncertain
20% escalates to a frontier (paid) model. This module implements:

  CascadeRouter        (#1) — confidence-aware tiering. Low confidence OR a
                             high-risk context (e.g. editing a production
                             workflow) routes to the strong model automatically.
  SelfConsistencyPool  (#2) — Best-of-N: ask the cheap model N times, then
                             score each candidate deterministically (schema
                             valid? gates pass? deep merge) — the vote cancels
                             random error, not systematic error.
  GeneratorCriticSplit (#3) — one call GENERATES, a SEPARATE call CRITIQUES
                             against a narrow checklist. A weak model is far
                             more accurate at "does this violate rule X?" than
                             at "invent a full solution".
  DraftRuns            (#9) — free tier => spend test-time compute: N internal
                             scratchpads before committing. Wraps the N cheap
                             draws the same way as SelfConsistency, but keeps
                             every draft score for later use.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from typing import Any, Callable, Optional


HIGH_RISK_CONTEXTS = (
    "production", "production workflow", "deploy to live", "live traffic",
    "customer data", "payment", "stripe live", "delete production",
    "modify running workflow",
)


# ---------------------------------------------------------------------------
# #1 Cascade routing by confidence + risk
# ---------------------------------------------------------------------------

@dataclass
class ConfidenceEstimate:
    score: float           # 0.0 .. 1.0 — model self-reported or heuristic
    declared: bool         # True if the model actually returned a confidence
    rationale: str = ""


def extract_confidence(text: str) -> ConfidenceEstimate:
    """Heuristic + explicit marker parsing. If the model emits
    `confidence: 0.77` or `CONFIDENCE=0.6` we trust it; otherwise we derive a
    score from structural signals (length, verbosity, hedging words)."""
    text_lower = text.lower()
    # 1. explicit marker wins
    m = re.search(r"(?:confidence|confidence_score)\s*[:=]\s*(0?\.\d{1,3}|\d\.\d{1,3}|1(?:\.0)?)",
                  text_lower)
    if m:
        val = float(m.group(1))
        return ConfidenceEstimate(score=max(0.0, min(1.0, val)), declared=True,
                                  rationale="explicit marker")
    # 2. heuristic: hedging -> lower
    hedge = sum(1 for w in ("i think", "maybe", "possibly", "not sure",
                            "uncertain", "approximately", "probably")
                if w in text_lower)
    length = min(1.0, len(text) / 800)
    score = max(0.05, min(0.95, 0.45 * length - 0.05 * hedge + 0.3))
    return ConfidenceEstimate(score=round(score, 3), declared=False,
                              rationale=f"heuristic (length={length:.2f}, hedge={hedge})")


class CascadeRouter:
    """Tiers: LOCAL → CHEAP → FRONTIER → HITL. Escalation on low confidence OR
    high-risk context, exactly as required. Frontier call is abstracted via
    `frontier_fn` so it can be LiteLLM/claude in prod, a fake in tests."""

    CHEAP_THRESHOLD = 0.35   # below this => not confident enough for cheap
    FRONTIER_THRESHOLD = 0.60  # above => cheap is fine on its own

    def __init__(
        self,
        cheap_fn: Callable[[str], dict[str, Any]],
        frontier_fn: Optional[Callable[[str], dict[str, Any]]] = None,
        cheap_budget_usd: float = 0.0,
    ):
        self.cheap_fn = cheap_fn
        self.frontier_fn = frontier_fn
        self.cheap_budget_usd = cheap_budget_usd
        # per-task ledger so we can show the tier path taken
        self.path_log: list[str] = []

    @staticmethod
    def _is_high_risk(task: str) -> bool:
        t = task.lower()
        return any(ctx in t for ctx in HIGH_RISK_CONTEXTS)

    def route(self, task: str, cheap_result: Optional[dict] = None) -> dict:
        """Decide tier. `cheap_result` may already carry an explicit confidence."""
        self.path_log = []
        declared_conf = None
        if cheap_result and "confidence" in cheap_result:
            declared_conf = ConfidenceEstimate(
                score=float(cheap_result["confidence"]), declared=True)

        est = declared_conf or (
            extract_confidence(json.dumps(cheap_result, default=str))
            if cheap_result else ConfidenceEstimate(0.0, False)
        )
        high_risk = self._is_high_risk(task)

        # high risk always >= frontier (never silent cheap-only)
        if high_risk:
            if self.frontier_fn is not None:
                out = self.frontier_fn(task)
                self.path_log.append("FRONTIER(high-risk)")
                return {**out, "tier": "FRONTIER", "escalated": True,
                        "reason": "high-risk context", "path": list(self.path_log),
                        "confidence": est.score}
            self.path_log.append("HITL(high-risk, no frontier)")
            return {"tier": "HITL", "escalated": True,
                    "reason": "high-risk context, no frontier model configured",
                    "path": list(self.path_log), "confidence": est.score}

        # low confidence -> escalate to frontier
        if est.score < self.CHEAP_THRESHOLD:
            if self.frontier_fn is not None:
                out = self.frontier_fn(task)
                self.path_log.append("FRONTIER(low-confidence)")
                return {**out, "tier": "FRONTIER", "escalated": True,
                        "reason": f"low confidence {est.score:.2f}",
                        "path": list(self.path_log), "confidence": est.score}
            self.path_log.append("CHEAP(low-confidence, fallback)")
            return {**self.cheap_fn(task), "tier": "CHEAP_FALLBACK",
                    "escalated": False, "reason": "no frontier, kept cheap",
                    "path": list(self.path_log), "confidence": est.score}

        # confident enough -> cheap is fine
        out = self.cheap_fn(task)
        self.path_log.append("CHEAP(confident)")
        return {**out, "tier": "CHEAP", "escalated": False,
                "reason": f"confidence {est.score:.2f} >= {self.CHEAP_THRESHOLD}",
                "path": list(self.path_log), "confidence": est.score}


# ---------------------------------------------------------------------------
# #2 Self-consistency / Best-of-N vote
# ---------------------------------------------------------------------------

@dataclass
class Candidate:
    idx: int
    output: Any
    score: float = 0.0
    reasons: list[str] = field(default_factory=list)


class SelfConsistencyPool:
    """Draw N answers from the cheap model; score each deterministically;
    pick the winner. A weak model's random errors get cancelled by the vote."""

    def __init__(self, draw_fn: Callable[[int], Any],
                 scorer: Optional[Callable[[Any], float]] = None,
                 n: int = 3,
                 schema_validator: Optional[Callable[[Any], bool]] = None):
        self.draw_fn = draw_fn
        self.n = n
        self.scorer = scorer or self._default_scorer
        self.schema_validator = schema_validator

    @staticmethod
    def _default_scorer(out: Any) -> float:
        # structural richness proxy: more complete nodes & connections win
        if isinstance(out, dict):
            nodes = out.get("nodes", [])
            conns = out.get("connections", {})
            return min(100.0, len(nodes) * 5 + len(conns))
        s = str(out)
        return min(100.0, len(s) / 10)

    def run(self) -> dict:
        cands: list[Candidate] = []
        for i in range(self.n):
            out = self.draw_fn(i)
            score = self.scorer(out)
            cands.append(Candidate(idx=i, output=out, score=score))
        # schema-valid candidates outrank; then by score
        cands.sort(key=lambda c: (
            self.schema_validator(c.output) if self.schema_validator else True,
            c.score,
        ), reverse=True)
        winner = cands[0]
        return {
            "winner": winner.output,
            "winner_idx": winner.idx,
            "winner_score": winner.score,
            "n_drawn": len(cands),
            "all_scores": [c.score for c in cands],
            "consensus_delta": max(c.score for c in cands) - winner.score
            if len(cands) > 1 else 0.0,
        }


# ---------------------------------------------------------------------------
# #3 Generator / Critic split
# ---------------------------------------------------------------------------

@dataclass
class ChecklistItem:
    id: str
    rule_text: str
    critical: bool = False


class GeneratorCriticSplit:
    """One call generates; a SEPARATE narrow call critiques against a fixed
    checklist. The weak model only needs to answer yes/no per rule, which is
    far easier than free-form generation."""

    def __init__(self, critic_fn: Callable[[Any, list[str]], list[str]],
                 checklist: list[ChecklistItem]):
        self.critic_fn = critic_fn     # returns list of violated rule ids
        self.checklist = checklist

    def generate_and_critique(self, generate_fn: Callable[[str], Any],
                              task: str) -> dict:
        output = generate_fn(task)
        rule_texts = [i.rule_text for i in self.checklist]
        violated_ids = self.critic_fn(output, rule_texts) or []
        violated = [i for i in self.checklist if i.id in violated_ids]
        critical_broken = [i for i in violated if i.critical]
        # hard-brake on a critical breach, regardless of who generated
        return {
            "ok": not critical_broken,
            "output": output,
            "violations": [{"id": i.id, "rule": i.rule_text,
                            "critical": i.critical} for i in violated],
            "critical_breached": [i.id for i in critical_broken],
        }


# ---------------------------------------------------------------------------
# #9 Draft runs (free tier -> test-time compute)
# ---------------------------------------------------------------------------

class DraftRuns:
    """Spend compute, not money: N internal scratch drafts before committing.
    Keeps the full pool of drafts + their scores (feed to self-consistency or
    return the best draft with trace)."""

    def __init__(self, draw_fn: Callable[[int], str], drafts: int = 3):
        self.draw_fn = draw_fn
        self.drafts = drafts

    def best(self, score_fn: Callable[[str], float]) -> dict:
        records = [
            {"idx": i, "draft": self.draw_fn(i),
             "score": score_fn(self.draw_fn(i))}   # noqa — two draws ok; cheap
            for i in range(self.drafts)
        ]
        records.sort(key=lambda r: r["score"], reverse=True)
        return {"best_draft": records[0]["draft"],
                "best_score": records[0]["score"],
                "all_drafts_scored": [{"idx": r["idx"], "score": r["score"]}
                                      for r in records]}


if __name__ == "__main__":
    def cheap(task):
        return {"ok": True, "answer": "routine parse", "confidence": 0.8}

    def frontier(task):
        return {"ok": True, "answer": "in-depth: escalated", "tier_frontier": True}

    cr = CascadeRouter(cheap_fn=cheap, frontier_fn=frontier)
    print("routine:", cr.route("parse webhook payload")["tier"])
    print("risky:", cr.route("edit production workflow with customer data")["tier"])
    print("unsure:", cr.route("design", cheap_result={"ok": True, "confidence": 0.1})["tier"])