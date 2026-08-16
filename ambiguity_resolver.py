"""Ambiguity Resolver — forced-explicit ambiguity gate (weak-model hardening #1b).

A small model doesn't fail because it "doesn't notice" ambiguity — it fails
because it never stops to classify it. This module forces a mandatory JSON
contract BEFORE any execution step:

    {"ambiguity_score": 0-1, "assumptions_made": [...], "missing_info": [...],
     "clarifying_question": "..." | null}

Rules:
  - ambiguity_score > AMBIGUITY_CEILING  -> CLARIFY (route to HITL, default-deny)
  - ambiguity_score > CLEAR_CEILING      -> ESCALATE to frontier (or HITL if none)
  - otherwise                            -> PASSTHROUGH, but the declared
                                            assumptions/missing_info ride along
                                            into the generator prompt.

The model-classification JSON is *merged* with deterministic structural signals
(missing required fields, vague hedges, unresolved placeholders, Arabic implicit
phrasing) so the gate never depends on the model's honesty alone. The score that
wins is the worst of model vs structural heuristics.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from typing import Any, Callable, Optional

AMBIGUITY_CEILING = 0.4     # above => must clarify (HITL / block execution)
CLEAR_CEILING = 0.15        # at-or-above => escalate to frontier, still runnable

# Deterministic structural signals -> bonus ambiguity
VAGUE_TERMS = (
    "etc", "and so on", "whatever", "somehow", "handle it", "make it nice",
    "do your best", "roughly", "soon", "كده", "وشغال", "عادي", "ماشي",
)
PLACEHOLDER_PATTERNS = (
    (r"\bXXX\b", "unresolved placeholder XXX"),
    (r"<[^>]*>", "angle-bracket placeholder"),
    (r"\bTBD\b", "unresolved TBD"),
    (r"\[\s*\]", "empty brackets"),
)
MISSING_REQUIRED_SIGNALS = (
    "token", "url", "path", "chat_id", "webhook path", "endpoint",
    "api_key", "credentials", "channel", "workspace",
)
# An explicit clarifying question means the model itself flagged doubt.
EXPLICIT_QUESTION_TERMS = ("clarifying question", "more info", "please clarify",
                           "لوسمحت وضح", "محتاج أوضح", "not enough")


@dataclass
class AmbiguityAssessment:
    ambiguity_score: float
    assumptions_made: list[str] = field(default_factory=list)
    missing_info: list[str] = field(default_factory=list)
    clarifying_question: Optional[str] = None
    declared: bool = False                # model actually emitted the contract
    structural_floor: float = 0.0         # heuristic-only score (never trusted)
    verdict: str = "PASSTHROUGH"          # PASSTHROUGH | ESCALATE | CLARIFY

    def to_dict(self) -> dict:
        return {
            "ambiguity_score": self.ambiguity_score,
            "assumptions_made": self.assumptions_made,
            "missing_info": self.missing_info,
            "clarifying_question": self.clarifying_question,
            "declared": self.declared,
            "verdict": self.verdict,
        }


def structural_ambiguity(task_text: str, artifact_json: Optional[dict] = None) -> tuple[float, list[str]]:
    """Deterministic heuristic — the floor the model's self-report can never
    drop below. Returns (score, flags)."""
    t = (task_text or "").lower()
    blob = json.dumps(artifact_json or {}, default=str).lower()
    flags: list[str] = []
    score = 0.0

    for term in VAGUE_TERMS:
        if term in t:
            score += 0.15
            flags.append(f"vague term: '{term}'")

    for pat, label in PLACEHOLDER_PATTERNS:
        if re.search(pat, task_text or ""):
            score += 0.3
            flags.append(label)

    # short, underspecified instructions are ambiguous by construction — but a
    # terse label is fine when the artifact itself is concrete (the orchestrator
    # always ships a workflow_json), so this is only a mild signal.
    words = len(re.findall(r"\S+", t))
    if words < 6:
        score += 0.1
        flags.append(f"very short instruction ({words} words)")
        # terse + integration-oriented but names none of the required inputs
        for term in MISSING_REQUIRED_SIGNALS:
            if term in t and term not in blob:
                score += 0.08
                flags.append(f"required signal '{term}' absent from artifact")

    return max(0.0, min(1.0, score)), flags


def parse_contract(text: str) -> Optional[dict]:
    """Extract the mandatory JSON contract from a model response. Resilient to
    markdown fences and stray prose around the JSON."""
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
class AmbiguityResult:
    assessment: AmbiguityAssessment
    floored: bool                      # True when heuristics overrode the model


class AmbiguityResolver:
    """Pre-execution gate. `classify_fn` is the cheap-model call that must emit
    the JSON contract; when none is available the structural floor alone decides
    (still enforced, still deterministic)."""

    def __init__(
        self,
        classify_fn: Optional[Callable[[str], str]] = None,
        ambiguity_ceiling: float = AMBIGUITY_CEILING,
        clear_ceiling: float = CLEAR_CEILING,
    ):
        self.classify_fn = classify_fn
        self.ambiguity_ceiling = ambiguity_ceiling
        self.clear_ceiling = clear_ceiling

    @staticmethod
    def _contract_prompt(task_text: str) -> str:
        return (
            "Classify the ambiguity of this task BEFORE any execution. Reply "
            "with ONLY this JSON (no prose):\n"
            "{\n"
            '  "ambiguity_score": <0-1>,\n'
            '  "assumptions_made": ["..."],\n'
            '  "missing_info": ["..."],\n'
            '  "clarifying_question": "..." | null\n'
            "}\n"
            f"Task: {task_text}\n"
        )

    def assess(self, task_text: str, artifact_json: Optional[dict] = None) -> AmbiguityResult:
        floor, flags = structural_ambiguity(task_text, artifact_json)
        model = None
        model_score = 0.0
        if self.classify_fn is not None:
            try:
                raw = self.classify_fn(self._contract_prompt(task_text))
                model = parse_contract(raw)
            except Exception:
                model = None

        declared = model is not None
        if model is not None:
            score = float(model.get("ambiguity_score", 0.0))
            score = max(0.0, min(1.0, score))
            assessment = AmbiguityAssessment(
                ambiguity_score=max(floor, score),
                assumptions_made=list(model.get("assumptions_made", []) or []),
                missing_info=[*(model.get("missing_info", []) or []), *flags],
                clarifying_question=model.get("clarifying_question") or None,
                declared=True,
                structural_floor=floor,
            )
        else:
            assessment = AmbiguityAssessment(
                ambiguity_score=floor,
                assumptions_made=[],
                missing_info=flags,
                clarifying_question=(
                    "task is underspecified; please clarify requirements"
                    if floor > 0.3 else None),
                declared=False,
                structural_floor=floor,
            )

        if assessment.ambiguity_score > self.ambiguity_ceiling:
            assessment.verdict = "CLARIFY"
        elif assessment.ambiguity_score >= self.clear_ceiling:
            assessment.verdict = "ESCALATE"
        else:
            assessment.verdict = "PASSTHROUGH"

        return AmbiguityResult(
            assessment=assessment,
            floored=floor > (model_score if model is not None else 0.0))


def build_ambiguity_gate(
    resolver: AmbiguityResolver,
    hitl_create_fn: Callable,
    frontier_fn: Optional[Callable] = None,
    block_ceiling: float = AMBIGUITY_CEILING,
) -> Callable[[str, Optional[dict]], dict]:
    """Convenience gateway wired exactly as the user described:

      ambiguity-resolver (stops if unclear) -> context-enrichment (inject
      known implicit context) -> execution with chain-integrity-checker ->
      confidence-calibrator (decide real escalation).

    Returns a callable(task, artifact) -> {"status": ...}. CLARIFY always routes
    to HITL (or a frontier backend when configured). ESCALATE goes to the
    frontier when one exists, otherwise to HITL too — a borderline-ambiguous
    task must never continue with a guessed interpretation. Anything below the
    escalation band passes through with its assumptions attached.
    """
    def gate(task_text: str, artifact_json: Optional[dict] = None) -> dict:
        result = resolver.assess(task_text, artifact_json)
        a = result.assessment
        if a.verdict in ("CLARIFY", "ESCALATE"):
            if frontier_fn is not None:
                out = frontier_fn(task_text)
                return {**out, "status": "ESCALATED_FRONTIER",
                        "assessment": a.to_dict()}
            req = hitl_create_fn(
                task_text,
                violations=[f"ambiguity {a.ambiguity_score:.2f}",
                            *(a.missing_info or [])[:4]],
            )
            return {"status": "CLARIFY_HITL", "request_id": req.request_id,
                    "clarifying_question": a.clarifying_question,
                    "assessment": a.to_dict()}
        return {"status": "PASSTHROUGH", "assessment": a.to_dict()}

    return gate