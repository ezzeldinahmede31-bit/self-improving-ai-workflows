"""Tests for incident.py (response + correlation + red-team loop)."""


def test_response_all_green_and_partial():
    from incident import IncidentResponse, RESPONSE_STEPS
    ir = IncidentResponse({s: (lambda i, c: None) for s in RESPONSE_STEPS})
    out = ir.respond("inc-1", {"why": "leak"})
    assert out["contained"] and len(out["steps"]) == 5

    def boom(i, c):
        raise RuntimeError("pager down")

    ir2 = IncidentResponse({"kill_session": lambda i, c: None,
                            "revoke_token": boom})
    out = ir2.respond("inc-2")
    assert out["contained"] is False
    by_step = {s["step"]: s["ok"] for s in out["steps"]}
    assert by_step["kill_session"] and not by_step["revoke_token"]
    assert by_step["alert_human"] is False  # unbound handler recorded


def test_correlation_fuses_incident():
    from incident import correlate
    base = 1000.0
    alerts = [{"agent": "a", "session": "s", "kind": "url", "ts": base},
              {"agent": "a", "session": "s", "kind": "cred", "ts": base + 5},
              {"agent": "a", "session": "s", "kind": "api", "ts": base + 9},
              {"agent": "b", "session": "t", "kind": "url", "ts": base}]
    out = correlate(alerts)
    assert len(out["incidents"]) == 1
    assert out["incidents"][0]["signals"] == 3
    assert len(out["lonely"]) == 1


def test_redteam_loop_feeds_golden():
    from incident import RedTeamLoop
    loop = RedTeamLoop()
    added = []
    suite = lambda: {"rows": [{"case": "c1", "family": "inj", "ok": True},
                              {"case": "c2", "family": "inj", "ok": False}]}
    out = loop.run_cycle(suite,
                         lambda cid, rep, exp: added.append(cid))
    assert out["checked"] == 2 and out["failures"] == 1
    assert added == ["rt-inj-c2"] and len(loop.runs) == 1
