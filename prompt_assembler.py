"""Few-shot prompt assembler — #7.

Turns accumulated HITL rejections (from feedback_loop) into automatic few-shot
blocks for similar tasks. The weak model LEARNS from its actual mistakes instead
of repeating them. This is the "negative examples" complement to RagMemory's
positive examples.

Pipeline: feedback_loop writes rejection patterns + quirks -> this module
renders them into a prompt fragment that the generator consumes on every task
that touches the offending rule/vector.
"""

from __future__ import annotations

import re
from typing import Optional

from feedback_loop import FeedbackLoop
from quirks_memory import query_quirks


class FewShotAssembler:
    def __init__(self, feedback: Optional[FeedbackLoop] = None):
        self.feedback = feedback or FeedbackLoop()

    def negative_examples(self, rule_keywords: Optional[list[str]] = None,
                          limit: int = 5) -> list[dict]:
        """Pull the most-rejected rules as few-shot negatives. Returns
        [{rule, count, last_reason}] ordered by rejection count."""
        rows = self.feedback.rejection_summary()
        if rule_keywords:
            kw = " ".join(rule_keywords).lower()
            rows = [r for r in rows if any(
                k in f"{r['rule']} {r.get('last_reason','')}".lower()
                for k in re.findall(r"[a-z0-9_]{3,}", kw))]
        return rows[:limit]

    def render_prompt_block(self, rule_keywords: Optional[list[str]] = None) -> str:
        """The exact few-shot fragment injected into generation prompts."""
        negatives = self.negative_examples(rule_keywords)
        quirks = []
        try:
            quirks = query_quirks("hitl_feedback", limit=5)
        except Exception:
            quirks = []
        lines: list[str] = []
        if negatives:
            lines.append("# Few-shot NEGATIVE examples (humans rejected these):")
            for n in negatives:
                lines.append(f"- AVOID: {n['rule']} (rejected {n['count']}x; "
                             f"last: {n.get('last_reason','')[:100]})")
        if quirks:
            lines.append("# Learned quirks to honor:")
            for q in quirks:
                lines.append(f"- {q['symptom']} -> {q['fix']}")
        return "\n".join(lines) or ""


def build_generator_prompt(task: str, rag_context: str, few_shot: str,
                           schema_hint: str = "") -> str:
    """Assemble the final prompt given all the scaffolding fragments. Order
    matters: task -> constraints -> negative lessons -> context -> format."""
    parts = [
        "You are a precise n8n workflow builder. Produce a single valid JSON "
        "workflow for the task. Follow every instruction below EXACTLY.",
        f"## Task\n{task}",
    ]
    if few_shot:
        parts.append(f"## Do not repeat these mistakes\n{few_shot}")
    if rag_context:
        parts.append(f"## Reference context\n{rag_context}")
    if schema_hint:
        parts.append(f"## Output format\n{schema_hint}")
    parts.append("Return ONLY the JSON. No markdown fences, no commentary.")
    return "\n\n".join(parts)


if __name__ == "__main__":
    asm = FewShotAssembler()
    for i in range(3):
        asm.feedback.record_rejection("ssrf_internal_egress", "no localhost")
    print(asm.render_prompt_block(rule_keywords=["ssrf"]))