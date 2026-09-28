"""Tests for contract_test.py and schema_evolve.py."""


def _cal_probe():
    return ({"date": "2026-09-28"}, {"id": "e1", "ok": True}, 0.2, "v3")


def test_contract_green_and_breaches():
    from contract_test import ContractRegistry
    r = ContractRegistry()
    r.declare("cal", input_schema={"date": "str"},
              output_schema={"id": "str", "ok": "bool"},
              errors=["busy"], timeout_s=2.0, auth="oauth", version="v3")
    out = r.verify("cal", _cal_probe)
    assert out["ok"] and not out["breaches"]
    out = r.verify("ghost", _cal_probe)
    assert not out["ok"]
    out = r.verify("cal", lambda: ({"date": "x"}, {"id": 1}, 0.1, "v3"))
    assert not out["ok"] and any("id" in b for b in out["breaches"])
    out = r.verify("cal", lambda: ({"date": "x"}, {"error": "weird"},
                                   0.1, "v3"))
    assert not out["ok"]
    out = r.verify("cal", lambda: ({"date": "x"}, {"id": "e", "ok": True},
                                   9.0, "v3"))
    assert not out["ok"]
    out = r.verify("cal", lambda: ({"date": "x"}, {"id": "e", "ok": True},
                                   0.1, "v9"))
    assert not out["ok"] and any("version" in b for b in out["breaches"])


def test_contract_persist(tmp_path):
    from contract_test import ContractRegistry
    p = tmp_path / "c.json"
    r = ContractRegistry(str(p))
    r.declare("t", input_schema={}, output_schema={}, errors=[],
              timeout_s=1.0, auth="key", version="v1")
    r.save()
    r2 = ContractRegistry(str(p))
    assert r2.verify("t", lambda: ({}, {}, 0.0, "v1"))["ok"]


def test_schema_additive_audit():
    from schema_evolve import SchemaRegistry
    r = SchemaRegistry()
    r.declare("v1", {"name": "str", "age": "int"})
    r.declare("v2", {"name": "str", "age": "float", "nick": "str"})
    out = r.audit_additive("v1", "v2")
    assert out["ok"] and out["added"] == ["nick"]
    r.declare("v3", {"name": "str"})
    out = r.audit_additive("v2", "v3")
    assert not out["ok"] and "age" in out["dropped"]


def test_schema_migrate_chain_and_dual():
    from schema_evolve import SchemaRegistry
    r = SchemaRegistry()
    r.add_migration("v1", "v2", lambda rec: {**rec, "nick": ""})
    r.add_migration("v2", "v3", lambda rec: {**rec, "v": 3})
    out = r.migrate({"a": 1}, "v1", "v3", ["v1", "v2", "v3"])
    assert out == {"a": 1, "nick": "", "v": 3}
    dual = r.dual_read({"a": 1, "b": 1}, {"a": 1, "b": 2})
    assert dual["b"] == 2 and dual["_legacy"]["b"] == 1
    import pytest
    with pytest.raises(KeyError):
        r.migrate({"a": 1}, "v1", "v9", ["v1", "v2"])
