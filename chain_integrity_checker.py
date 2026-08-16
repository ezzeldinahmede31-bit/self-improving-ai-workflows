"""Chain Integrity Checker — cumulative per-step consistency review
(weak-model hardening protocol). See .opencode/skills/chain-integrity-checker.

A small model doesn't err because it is "dumb" — it errs because long context
makes it forget or contradict itself. The fix is to SEPARATE execution from
review: every time the DAG adds one step, a separate narrow call (same cheap
model) reviews ONLY:

    completed_steps (so far) + the single new step

and answers a mandatory JSON contract:

    {
      "contradicts_previous": bool,
      "contradiction_details": "...",
      "skipped_dependency": bool,
      "confidence": 0-1
    }

Deterministic structural checks run in parallel and can NEVER be overridden by
the model (dependency closure, duplicate ids, orphan deps). Contradiction and
skipped-dependency are *semantic* and therefore model-assisted — but a
structural violation is a hard stop regardless.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from typing import Any, Callable, Optional

# Cheap-model judge contract parser (reuse pattern from ambiguity_resolver).
def _parse_json(text: str) -> Optional[dict]:
    if not text:
        return None
    stripped = text.strip()
    if stripped.startswith("```"):
        m = re.search(r"```(?:json)?\s*(.*?)```", stripped, re.S)
        if m:
            stripped = m.group(1).strip()
    start = stripped.find("{")
    end = stripped.rfind("}")
    if start == -1 or end == -1:
        return None
    try:
        return json.loads(stripped[start:end + 1])
    except json.JSONDecodeError:
        return None


@dataclass
class StepReview:
    step_label: str
    ok: bool
    contradicts_previous: bool = False
    contradiction_details: str = ""
    skipped_dependency: bool = False
    structural_issue: str = ""          # non-empty => hard fail, non-overridable
    confidence: float = 0.0
    started_from_review: bool = False   # duplicate/continuity flag

    def to_dict(self) -> dict:
        return {
            "ok": self.ok, "contradicts_previous": self.contradicts_previous,
            "contradiction_details": self.contradiction_details,
            "skipped_dependency": self.skipped_dependency,
            "structural_issue": self.structural_issue,
            "confidence": self.confidence,
            "step_label": self.step_label,
        }


def structural_integrity_check(
    completed: list[dict],
    new_step: dict,
    dep_key: str = "deps",
    id_key: str = "id",
) -> dict:
    """Pure deterministic check — never overridable by the model. Verifies:
      - no orphan dependency (new_step.deps are all in completed ids)
      - no duplicate id
      - no self-dependency
      - dependency closure (a dep's own deps are also present)

    Returns {"ok", "structural_issue"}."""
    issue = ""
    new_id = new_step.get(id_key, "???")
    new_deps = set(new_step.get(dep_key, []) or [])
    completed_ids = {c.get(id_key) for c in completed}

    if new_deps:
        missing = new_deps - completed_ids
        if missing:
            issue = f"step '{new_id}' depends on unproduced step(s): {sorted(missing)}"
            return {"ok": False, "structural_issue": issue}
    if new_id in completed_ids:
        issue = f"duplicate step id '{new_id}'"
        return {"ok": False, "structural_issue": issue}
    if new_id in new_deps:
        issue = f"step '{new_id}' depends on itself"
        return {"ok": False, "structural_issue": issue}
    # dependency closure: a dep's own deps must already exist too
    for dep in new_deps:
        dep_object = next((c for c in completed if c.get(id_key) == dep), None)
        if dep_object:
            transitive = set(dep_object.get(dep_key, []) or [])
            if transitive - completed_ids:
                issue = f"step '{new_id}' uses '{dep}' whose deps are missing: {sorted(transitive - completed_ids)}"
                return {"ok": False, "structural_issue": issue}
    return {"ok": True, "structural_issue": ""}


def _review_prompt(completed: list[dict], new_step: dict) -> str:
    return (
        "You verify ONE step of an automation plan for internal consistency. "
        "Steps completed so far:\n"
        f"{json.dumps(completed, ensure_ascii=False, indent=1)}\n"
        "New step just added:\n"
        f"{json.dumps(new_step, ensure_ascii=False, indent=1)}\n"
        'Reply with ONLY JSON: {"contradicts_previous": bool, '
        '"contradiction_details": "...", "skipped_dependency": bool, '
        '"confidence": 0-1}\n'
        "contradicts_previous=true only if the new step conflicts with a prior "
        "step's resource, credential, or ordering. skipped_dependency=true only "
        "if the new step logically needs a step that is missing."
    )


class ChainIntegrityChecker:
    """Cumulative review hook. Insert AFTER every node is added to the DAG —
    not only at the end. `judge_fn` is the cheap-model call; without one the
    structural checks alone enforce integrity (still deterministic)."""

    def __init__(
        self,
        judge_fn: Optional[Callable[[str], str]] = None,
        hard_on_model_semantic: bool = False,
    ):
        self.judge_fn = judge_fn
        # By default semantic contradictions just flag (escort) the step; the
        # planner may still continue. Set True to gate on the model verdict too.
        self.hard_on_model_semantic = hard_on_model_semantic

    def verify(
        self,
        completed: list[dict],
        new_step: dict,
    ) -> StepReview:
        structural = structural_integrity_check(completed, new_step)
        review = StepReview(
            step_label=str(new_step.get("label", new_step.get("id", "???"))),
            ok=structural["ok"],
            structural_issue=structural["structural_issue"],
        )
        if not structural["ok"]:
            review.contradicts_previous = True
            return review

        if self.judge_fn is not None:
            try:
                raw = self.judge_fn(_review_prompt(completed, new_step))
                verdict = _parse_json(raw) or {}
            except Exception:
                verdict = {}
        else:
            verdict = {}

        model_contradict = bool(verdict.get("contradicts_previous"))
        model_skipped = bool(verdict.get("skipped_dependency"))
        review.contradicts_previous = model_contradict
        review.contradiction_details = str(verdict.get("contradiction_details", ""))[:300]
        review.skipped_dependency = model_skipped
        try:
            review.confidence = float(verdict.get("confidence", 0.0))
        except (TypeError, ValueError):
            review.confidence = 0.0

        if review.contradicts_previous or review.skipped_dependency:
            if self.hard_on_model_semantic:
                review.ok = False
        return review


def check_dag_integrity(dag_nodes: list, judge_fn: Optional[Callable] = None) -> list[StepReview]:
    """Convenience: replay a whole DAG node list through the cumulative checker
    so the planner and tests share one verdict path. Returns per-step reviews."""
    checker = ChainIntegrityChecker(judge_fn=judge_fn)
    reviews: list[StepReview] = []
    completed: list[dict] = []
    for node in dag_nodes:
        step = {"id": node.id if hasattr(node, "id") else node.get("id"),
                "label": node.label if hasattr(node, "label") else node.get("label"),
                "deps": node.deps if hasattr(node, "deps") else node.get("deps", []),
                "resource": (node.resource if hasattr(node, "resource") else node.get("resource", ""))}
        reviews.append(checker.verify(completed, step))
        completed.append(step)
    return reviews