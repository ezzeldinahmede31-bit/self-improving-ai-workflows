import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from scripts.gate_first_pass_avoidlist import ERROR_PATTERNS_PATH, emit, load_patterns


@pytest.fixture(autouse=True)
def db_path(monkeypatch):
    """Keep the fixture hermetic: the real DB may change; use a temp copy."""
    import json
    import tempfile

    tmpdir = tempfile.mkdtemp()
    db_path = Path(tmpdir) / "n8n_error_patterns.json"
    if ERROR_PATTERNS_PATH.exists():
        with open(ERROR_PATTERNS_PATH, encoding="utf-8") as f:
            data = json.load(f)
    else:
        data = []
    db_path.write_text(json.dumps(data), encoding="utf-8")
    monkeypatch.setattr("scripts.gate_first_pass_avoidlist.ERROR_PATTERNS_PATH", db_path)
    yield db_path


def _seed(db_path, patterns):
    import json

    db_path.write_text(json.dumps(patterns), encoding="utf-8")


def test_load_patterns_empty(tmp_path):
    p = tmp_path / "missing.json"
    assert load_patterns(p) == []


def test_load_patterns_roundtrip(db_path):
    _seed(db_path, [{"gate": "security", "pattern": "x", "count": 1}])
    assert load_patterns(db_path) == [{"gate": "security", "pattern": "x", "count": 1}]


def test_emit_empty_db(db_path, capsys):
    _seed(db_path, [])
    assert emit(10, None, False) == 0
    out = capsys.readouterr().out
    assert "No recorded" in out


def test_emit_orders_by_count_desc(db_path, capsys):
    _seed(db_path, [
        {"gate": "quality", "pattern": "low", "count": 1},
        {"gate": "preflight", "pattern": "high", "count": 14},
    ])
    emit(10, None, False)
    out = capsys.readouterr().out
    assert out.index("high") < out.index("low")
    assert "x14" in out


def test_emit_honors_top_limit(db_path, capsys):
    _seed(db_path, [
        {"gate": "quality", "pattern": f"p{i}", "count": i}
        for i in range(1, 6)
    ])
    emit(2, None, False)
    out = capsys.readouterr().out
    assert "p5" in out and "p4" in out
    assert "p1" not in out


def test_emit_gate_filter(db_path, capsys):
    _seed(db_path, [
        {"gate": "security", "pattern": "sec", "count": 5},
        {"gate": "quality", "pattern": "qual", "count": 9},
    ])
    emit(10, "security", False)
    out = capsys.readouterr().out
    assert "sec" in out and "qual" not in out


def test_emit_json_mode(db_path, capsys):
    _seed(db_path, [{"gate": "security", "pattern": "p", "count": 2, "first_seen": "a", "last_seen": "b"}])
    emit(10, None, True)
    import json

    out = capsys.readouterr().out
    data = json.loads(out)
    assert data == [{"gate": "security", "pattern": "p", "count": 2, "first_seen": "a", "last_seen": "b"}]


def test_emit_json_gate_filter(db_path, capsys):
    _seed(db_path, [
        {"gate": "security", "pattern": "sec", "count": 2},
        {"gate": "quality", "pattern": "qual", "count": 9},
    ])
    emit(10, "security", True)
    import json

    out = capsys.readouterr().out
    data = json.loads(out)
    assert [d["pattern"] for d in data] == ["sec"]


def test_stale_false_positives_absent_from_real_db():
    """The historical non-agent TOOL_SCOPE_LOCK patterns must stay gone."""
    real = load_patterns(Path(__file__).resolve().parent.parent / "memory" / "n8n_error_patterns.json")
    for p in real:
        text = p["pattern"]
        for bogus in ("Qdrant Insert", "Chat Trigger", "NVIDIA Embeddings", "Load Document", "Split Text", "NVIDIA Chat Model", "Query Vector Store", "Qdrant Retrieve"):
            assert f"Agent '{bogus}'" not in text, text


def test_main_cli(tmp_path, capsys, monkeypatch):
    import scripts.gate_first_pass_avoidlist as mod

    monkeypatch.setattr(mod, "ERROR_PATTERNS_PATH", tmp_path / "db.json")
    (tmp_path / "db.json").write_text("[]", encoding="utf-8")
    assert mod.main(["--top", "3"]) == 0
