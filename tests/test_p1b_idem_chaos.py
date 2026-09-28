"""Tests for idempotency.py and chaos_drills.py."""


def test_replay_returns_recorded(tmp_path):
    from idempotency import IdempotencyStore
    st = IdempotencyStore(str(tmp_path / "idem.json"))
    calls = []
    key = IdempotencyStore.make_key("booking", "req-1")
    first = st.execute(key, lambda: (calls.append(1), {"ok": True})[1])
    second = st.execute(key, lambda: (calls.append(1), {"ok": False})[1])
    assert first["executed"] and not second["executed"]
    assert second["result"] == {"ok": True} and calls == [1]
    assert first["digest"] == second["digest"]


def test_crash_records_nothing(tmp_path):
    from idempotency import IdempotencyStore
    st = IdempotencyStore(str(tmp_path / "idem.json"))

    def boom():
        raise RuntimeError("transient")

    try:
        st.execute("k1", boom)
    except RuntimeError:
        pass
    assert st.keys() == []


def test_forget_and_namespaces(tmp_path):
    from idempotency import IdempotencyStore
    st = IdempotencyStore(str(tmp_path / "idem.json"))
    k1 = IdempotencyStore.make_key("a", "x")
    k2 = IdempotencyStore.make_key("b", "x")
    assert k1 != k2
    st.execute(k1, lambda: 1)
    assert st.forget(k1) and not st.forget(k1)


def test_chaos_drill_full_cycle():
    from chaos_drills import ChaosDrills
    d = ChaosDrills()
    state = {"alive": True}
    d.register("dead-redis", lambda: state.update(alive=False),
               lambda: (_ for _ in ()).throw(AssertionError())
               if state["alive"] else None,
               lambda: state.update(alive=True),
               lambda: (_ for _ in ()).throw(AssertionError())
               if not state["alive"] else None)
    out = d.run_drill("dead-redis")
    assert out["recovered"] and out["phases"]["healthy"] == "ok"
    cov = d.coverage()
    assert "dead-redis" in cov["proven"] and cov["missing"]


def test_chaos_unregistered_and_disaster(tmp_path=None):
    from chaos_drills import ChaosDrills, DisasterDrill
    d = ChaosDrills()
    out = d.run_drill("dead-n8n")
    assert out["recovered"] is False and "missing" in out["reason"]
    dd = DisasterDrill({"restore_db": lambda: None,
                        "restore_credentials": lambda: None,
                        "restore_workflows": lambda: None,
                        "restore_config": lambda: None,
                        "smoke": lambda: None})
    res = dd.run()
    assert res["ready"] and res["rto_s"] >= 0.0
    dd2 = DisasterDrill({})
    assert dd2.run()["ready"] is False
