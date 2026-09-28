"""Agent behavioral evaluation: did the agent behave correctly?

Beyond "did the code run?" — intent recognition, tool selection,
factual grounding, response language, and hallucination avoidance are
scored per scenario through weighted check callables. Agent functions
return {"intent": str, "tools": [...], "response": str, "facts": {...}}
and each check inspects the scenario + result. Totals gate promotion
of agent changes (clinic booking shape included as a worked pattern).

Only stdlib is used.
"""

from __future__ import annotations


def intent_is(*intents: str):
    """Check: recognized intent is among the accepted set."""
    def _check(scenario, result) -> tuple[bool, str]:
        got = str((result or {}).get("intent", ""))
        if got in intents:
            return True, ""
        return False, f"intent={got!r} not in {list(intents)!r}"
    return _check


def tools_used(*names: str, forbid: tuple[str, ...] = ()):
    """Check: required tools present, forbidden tools absent."""
    def _check(scenario, result) -> tuple[bool, str]:
        used = list((result or {}).get("tools", []))
        missing = [n for n in names if n not in used]
        bad = [n for n in forbid if n in used]
        if missing or bad:
            return False, f"missing={missing} forbidden_used={bad}"
        return True, ""
    return _check


def response_holds(predicate, label: str = "response rule"):
    """Check: caller predicate over the response text holds."""
    def _check(scenario, result) -> tuple[bool, str]:
        text = str((result or {}).get("response", ""))
        try:
            ok = bool(predicate(text))
        except Exception as exc:  # noqa: BLE001 - fail closed
            return False, f"{label} crashed: {exc}"
        return (True, "") if ok else (False, f"{label} violated")
    return _check


def facts_match(expected: dict):
    """Check: reported facts equal the independently known values."""
    def _check(scenario, result) -> tuple[bool, str]:
        facts = (result or {}).get("facts", {}) or {}
        bad = {k: facts.get(k) for k, v in expected.items()
               if facts.get(k) != v}
        if bad:
            return False, f"fact drift: {bad}"
        return True, ""
    return _check


class BehavioralEval:
    """Scenario registry + weighted behavior scoring."""

    def __init__(self):
        self._scenarios: list[dict] = []

    def add_scenario(self, scenario_id: str, context: dict,
                     checks: list[tuple[str, float, object]]) -> None:
        """Register a scenario with (name, weight, check-fn) triples."""
        for name, weight, fn in checks:
            if not callable(fn):
                raise TypeError(f"check {name} must be callable")
        self._scenarios.append({"id": str(scenario_id),
                                "context": dict(context),
                                "checks": [(str(n), float(w), f)
                                           for n, w, f in checks]})

    def run(self, agent_fn, *, scenario_id: str | None = None) -> dict:
        """Score one agent function across scenarios (or one)."""
        if not callable(agent_fn):
            raise TypeError("agent_fn must be callable")
        targets = [s for s in self._scenarios
                   if scenario_id is None or s["id"] == scenario_id]
        if scenario_id is not None and not targets:
            raise KeyError(f"unknown scenario: {scenario_id}")
        per_scenario, grand_ok, grand_total = [], 0.0, 0.0
        for scen in targets:
            try:
                result = agent_fn(scen["context"]) or {}
            except Exception as exc:  # noqa: BLE001 - record, continue
                result = {"_error": str(exc)}
            s_ok, s_total, rows = 0.0, 0.0, []
            for name, weight, fn in scen["checks"]:
                try:
                    ok, note = fn(scen["context"], result)
                except Exception as exc:  # noqa: BLE001 - fail closed
                    ok, note = False, f"check crashed: {exc}"
                s_total += weight
                if ok:
                    s_ok += weight
                rows.append({"check": name, "ok": bool(ok),
                             "note": str(note)})
            grand_ok += s_ok
            grand_total += s_total
            per_scenario.append(
                {"scenario": scen["id"],
                 "score": (s_ok / s_total) if s_total else 1.0,
                 "rows": rows})
        total = (grand_ok / grand_total) if grand_total else 1.0
        return {"score": total, "scenarios": per_scenario}
