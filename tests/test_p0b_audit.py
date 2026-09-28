"""Tests for immutable_audit.py."""

import sqlite3

from immutable_audit import AuditChain


def test_append_and_verify(tmp_path):
    c = AuditChain(str(tmp_path / "chain.db"), secret=b"3" * 32)
    c.append(kind="deploy", actor="agent-1", subject="wf-9", detail="ok")
    c.append(kind="approve", actor="human", subject="wf-9", detail="yes")
    out = c.verify()
    assert out == {"ok": True, "checked": 2, "broken_at": None}


def test_tamper_detected(tmp_path):
    p = tmp_path / "chain.db"
    c = AuditChain(str(p), secret=b"3" * 32)
    c.append(kind="a", actor="x", subject="s")
    c.append(kind="b", actor="x", subject="s")
    conn = sqlite3.connect(str(p))
    conn.execute("UPDATE events SET detail='forged' WHERE id=1")
    conn.commit()
    conn.close()
    out = AuditChain(str(p), secret=b"3" * 32).verify()
    assert out["ok"] is False and out["broken_at"] == 1


def test_reorder_detected(tmp_path):
    p = tmp_path / "chain.db"
    c = AuditChain(str(p))
    c.append(kind="a", actor="x", subject="s")
    c.append(kind="b", actor="x", subject="s")
    conn = sqlite3.connect(str(p))
    conn.execute("DELETE FROM events WHERE id=1")
    conn.commit()
    conn.close()
    out = AuditChain(str(p)).verify()
    assert out["ok"] is False


def test_tail_view(tmp_path):
    c = AuditChain(str(tmp_path / "chain.db"))
    c.append(kind="a", actor="x", subject="s", detail="d1")
    rows = c.tail(limit=5)
    assert len(rows) == 1 and rows[0]["detail"] == "d1"


def test_no_update_api():
    assert not hasattr(AuditChain, "update")
    assert not hasattr(AuditChain, "delete")
