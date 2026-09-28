"""Tests for advanced_testing.py and spec_drift.py."""


def test_property_holds_and_fails():
    from advanced_testing import property_check
    out = property_check(lambda rng: rng.randint(0, 100),
                         [lambda v: (v >= 0, "negative")], trials=50)
    assert out["holds"] is True
    out = property_check(lambda rng: rng.randint(0, 100),
                         [lambda v: (v < 50, "too big")], trials=200)
    assert out["holds"] is False and out["input"] >= 50


def test_metamorphic_and_differential():
    from advanced_testing import differential, metamorphic
    out = metamorphic([2, 3], lambda x: x + 1,
                      lambda a, b: (b == a + 1, "shift broken"))
    assert out["holds"] and out["checked"] == 2
    out = differential([1, 2], {"left": lambda x: x * 2,
                                "right": lambda x: x * 2})
    assert out["agree_all"]
    out = differential([1], {"left": lambda x: x,
                             "right": lambda x: x + 1})
    assert not out["agree_all"] and len(out["disagreements"]) == 1


def test_mutation_score_and_negatives():
    from advanced_testing import mutation_score, negative_cases
    base = lambda x: x > 0
    mutants = [("flip", lambda f: (lambda x: not f(x)))]
    suite = lambda v: v(1) is True and v(-1) is False
    out = mutation_score(base, mutants, suite)
    assert out["score"] == 1.0 and out["killed"] == ["flip"]
    weak = lambda v: True  # suite that passes everything
    out = mutation_score(base, mutants, weak)
    assert out["survived"] == ["flip"] and out["score"] == 0.0
    negs = negative_cases()
    assert "" in negs and any(len(n) > 10000 for n in negs)


def test_spec_drift_pin_and_move():
    from spec_drift import SpecDrift
    s = SpecDrift()
    s.pin("remind", "reminder fires 24h before")
    s.attach("remind", lambda: "reminder fires 24h before")
    assert s.check("remind")["drift"] is False
    s.attach("remind", lambda: "reminder fires 12h before")
    out = s.check("remind")
    assert out["drift"] is True and s.findings
    assert s.check("ghost")["reason"] == "unpinned"


def test_docs_drift_both_directions():
    from spec_drift import DocsDrift
    src = "def alpha():\n    pass\n\ndef beta_thing():\n    pass\n"
    syms = DocsDrift.code_symbols(src)
    assert syms == {"alpha", "beta_thing"}
    out = DocsDrift.check(syms, "alpha does the work.")
    assert out["undocumented"] == ["beta_thing"]
    out = DocsDrift.check({"alpha"},
                          "see phantom_module_helper for details")
    assert "phantom_module_helper" in out["phantom"]
    assert DocsDrift.code_symbols("def broken(:") == set()
