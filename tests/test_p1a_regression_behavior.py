"""Tests for prompt_regression.py and behavioral_eval.py."""


def _checker_factory(word):
    def _c(_inp, out):
        return (word in out, f"want {word}")
    return _c


def test_regression_blocks_on_loss():
    from prompt_regression import PromptRegression
    pr = PromptRegression()
    pr.add_prompt("v1", "t1", lambda i: "hello world")
    pr.add_prompt("v2", "t2", lambda i: "hello")
    pr.add_golden("g1", "in", _checker_factory("hello"))
    pr.add_golden("g2", "in", _checker_factory("world"))
    out = pr.compare("v1", "v2")
    assert out["old"] == 1.0 and out["new"] == 0.5
    assert out["regressions"] == ["g2"] and out["blocked"] is True


def test_regression_pass_when_stable():
    from prompt_regression import PromptRegression
    pr = PromptRegression()
    pr.add_prompt("v1", "t", lambda i: "same answer")
    pr.add_prompt("v2", "t", lambda i: "same answer")
    pr.add_golden("g1", "in", _checker_factory("same"))
    out = pr.compare("v1", "v2")
    assert out["blocked"] is False and out["delta"] == 0.0


def test_behavioral_clinic_shape():
    from behavioral_eval import (BehavioralEval, facts_match, intent_is,
                                 response_holds, tools_used)
    ev = BehavioralEval()
    ev.add_scenario("book-fallback",
                    {"utterance": "book tomorrow, 5 else 6"},
                    [("intent", 2.0, intent_is("book_appointment")),
                     ("tools", 2.0, tools_used("calendar.read",
                                               "calendar.book")),
                     ("no-invented-slots", 3.0, response_holds(
                         lambda t: "available" not in t.lower()
                         or "calendar" in t.lower(), "grounding")),
                     ("facts", 3.0, facts_match({"day": "tomorrow"}))])

    def agent(ctx):
        return {"intent": "book_appointment",
                "tools": ["calendar.read", "calendar.book"],
                "response": "Booked per calendar.",
                "facts": {"day": "tomorrow"}}

    out = ev.run(agent)
    assert out["score"] == 1.0

    def sloppy(ctx):
        return {"intent": "chit_chat", "tools": ["calendar.book"],
                "response": "5pm available!", "facts": {"day": "friday"}}

    out2 = ev.run(sloppy)
    assert out2["score"] < 1.0
    names = [r["check"] for r in out2["scenarios"][0]["rows"] if not r["ok"]]
    assert "intent" in names and "facts" in names
