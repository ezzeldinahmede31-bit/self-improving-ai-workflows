"""Tests for scripts/router_register.py — the find-skills auto-registration
step that adds a routing row + registry entry for every newly installed skill.

Covers: frontmatter parsing, bucket classification (existing + fallback),
routing-row insertion + idempotency, registry entry on existing buckets
(including suffixed headers like '### Automation (per-tool) (37)'), fallback
bucket creation, total bump semantics, and full main() integration on a temp
router + temp skills dir. Deterministic — no network, no real memory writes.
"""

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from scripts.router_register import (
    read_frontmatter, classify, ensure_routing_row, ensure_registry_entry,
    bump_total, FALLBACK_BUCKET,
)


# ---------------------------------------------------------------------------
# Helpers / fixtures
# ---------------------------------------------------------------------------

def _router_text():
    """A minimal but realistic router: decision table above, registry below,
    one suffixed Automation bucket, one plain bucket."""
    return (
        "# Router\n\n"
        "## Decision table\n"
        "| trigger | primary | notes |\n"
        "| - | - | - |\n"
        "\n"
        "## Full skill registry (complete inventory — 10 installed)\n"
        "\n"
        "### Automation (per-tool) (2)\n"
        "`sheets-automation` (D) - `jira-automation` (D)\n"
        "\n"
        "### Security (1)\n"
        "`security-review` (D)\n"
    )


def _make_skill(tmp_path, name, description):
    d = tmp_path / name
    d.mkdir(parents=True, exist_ok=True)
    (d / "SKILL.md").write_text(
        f"---\nname: {name}\ndescription: {description}\n---\n# {name}\n",
        encoding="utf-8",
    )
    return d

# ---------------------------------------------------------------------------
# read_frontmatter
# ---------------------------------------------------------------------------

def test_read_frontmatter_extracts_name_and_description(tmp_path):
    d = _make_skill(tmp_path, "mytool", "Automates mytool workflows end to end.")
    (name, desc), txt = read_frontmatter(d / "SKILL.md")
    assert name == "mytool"
    assert desc == "Automates mytool workflows end to end."
    assert "# mytool" in txt


def test_read_frontmatter_missing_description(tmp_path):
    d = tmp_path / "noskill"
    d.mkdir()
    (d / "SKILL.md").write_text("---\nname: noskill\n---\n", encoding="utf-8")
    (name, desc), _ = read_frontmatter(d / "SKILL.md")
    assert name == "noskill"
    assert desc == ""


def test_read_frontmatter_no_frontmatter(tmp_path):
    d = tmp_path / "raw"
    d.mkdir()
    p = d / "SKILL.md"
    p.write_text("# no frontmatter\n", encoding="utf-8")
    fm, txt = read_frontmatter(p)
    assert fm is None
    assert "# no frontmatter" in txt


# ---------------------------------------------------------------------------
# classify
# ---------------------------------------------------------------------------

def test_classify_matches_keyword_bucket():
    assert classify("Automate google sheets and excel sync") == "Automation"


def test_classify_n8n_preferred_bucket():
    assert classify("n8n agent workflow design patterns") == "n8n"


def test_classify_fallback_bucket_for_unmatched():
    assert classify("koala farming regulation and quantum origami taxonomy") == FALLBACK_BUCKET


# ---------------------------------------------------------------------------
# ensure_routing_row
# ---------------------------------------------------------------------------

def test_routing_row_inserted_before_decision_table():
    txt, added = ensure_routing_row(_router_text(), "zztest", "Test skill for router tests.")
    assert added is True
    assert "## Decision table" in txt
    # row lands just above the table
    assert "`zztest` |" in txt
    assert txt.index("(Auto-registered)") < txt.index("## Decision table")


def test_routing_row_idempotent():
    txt, _ = ensure_routing_row(_router_text(), "zztest", "Test skill for router tests.")
    txt, added = ensure_routing_row(txt, "zztest", "Test skill for router tests.")
    assert added is False
    assert txt.count("(Auto-registered)") == 1


def test_routing_row_noop_without_decision_table():
    txt, added = ensure_routing_row("no table here", "zztest", "Test.")
    assert added is False
    assert txt == "no table here"


# ---------------------------------------------------------------------------
# ensure_registry_entry
# ---------------------------------------------------------------------------

def test_registry_entry_appended_to_existing_bucket():
    txt, added = ensure_registry_entry(_router_text(), "zznew", "Automation")
    assert added is True
    assert "### Automation (per-tool) (3)" in txt
    assert txt.count("`zznew` (D)") == 1


def test_registry_entry_idempotent():
    txt, _ = ensure_registry_entry(_router_text(), "zznew", "Automation")
    txt, added = ensure_registry_entry(txt, "zznew", "Automation")
    assert added is False
    assert "### Automation (per-tool) (3)" in txt  # not 4


def test_registry_entry_not_fooled_by_routing_row_mention():
    # The routing row above also mentions the name in backticks; the presence
    # check must be scoped to the registry section only.
    txt, _ = ensure_routing_row(_router_text(), "zznew", "Test skill for router tests.")
    txt, added = ensure_registry_entry(txt, "zznew", "Automation")
    assert added is True
    assert "`zznew` (D)" in txt


def test_fallback_bucket_created_at_end():
    txt, added = ensure_registry_entry(_router_text(), "zzodd", "unmatched-topic-bucket")
    assert added is True
    assert "### unmatched-topic-bucket (1)" in txt
    assert "`zzodd` (D)" in txt


def test_fallback_bucket_presence_check_scoped_to_registry():
    # Regression: the fallback else-branch must not treat the routing row's
    # backtick mention as 'already present'.
    txt, _ = ensure_routing_row(_router_text(), "zzodd", "koala farming regulation topic")
    txt, added = ensure_registry_entry(txt, "zzodd", FALLBACK_BUCKET)
    assert added is True
    assert f"### {FALLBACK_BUCKET} (1)" in txt


def test_registry_entry_noop_without_registry_header():
    txt, added = ensure_registry_entry("### Automation (1)\n`a` (D)\n", "zznew", "Automation")
    assert added is False


# ---------------------------------------------------------------------------
# bump_total
# ---------------------------------------------------------------------------

def test_bump_total_by_n():
    txt = _router_text()
    assert "10 installed" in txt
    txt = bump_total(txt, 2)
    assert "12 installed" in txt


def test_bump_total_noop_when_n_zero():
    txt = bump_total(_router_text(), 0)
    assert "10 installed" in txt


# ---------------------------------------------------------------------------
# main() integration (monkeypatched paths)
# ---------------------------------------------------------------------------

def test_main_full_run_adds_row_registry_and_total(tmp_path, monkeypatch):
    import scripts.router_register as rr
    skills_dir = tmp_path / "skills"
    router_path = tmp_path / "router" / "SKILL.md"
    router_path.parent.mkdir(parents=True)
    router_path.write_text(_router_text(), encoding="utf-8")

    monkeypatch.setattr(rr, "SKILLS_DIR", skills_dir)
    monkeypatch.setattr(rr, "ROUTER", router_path)

    _make_skill(skills_dir, "zznew", "Automates spreadsheet sync for sales teams.")
    assert rr.main(["zznew"]) == 0

    out = router_path.read_text(encoding="utf-8")
    assert "(Auto-registered)" in out
    assert "### Automation (per-tool) (3)" in out
    assert "11 installed" in out


def test_main_idempotent_rerun_is_noop(tmp_path, monkeypatch):
    import scripts.router_register as rr
    skills_dir = tmp_path / "skills"
    router_path = tmp_path / "router" / "SKILL.md"
    router_path.parent.mkdir(parents=True)
    router_path.write_text(_router_text(), encoding="utf-8")

    monkeypatch.setattr(rr, "SKILLS_DIR", skills_dir)
    monkeypatch.setattr(rr, "ROUTER", router_path)

    _make_skill(skills_dir, "zznew", "Automates spreadsheet sync for sales teams.")
    assert rr.main(["zznew"]) == 0
    assert rr.main(["zznew"]) == 0

    out = router_path.read_text(encoding="utf-8")
    assert out.count("(Auto-registered)") == 1
    assert "11 installed" in out  # not 12


def test_main_multi_add_bumps_total_by_exact_count(tmp_path, monkeypatch):
    import scripts.router_register as rr
    skills_dir = tmp_path / "skills"
    router_path = tmp_path / "router" / "SKILL.md"
    router_path.parent.mkdir(parents=True)
    router_path.write_text(_router_text(), encoding="utf-8")

    monkeypatch.setattr(rr, "SKILLS_DIR", skills_dir)
    monkeypatch.setattr(rr, "ROUTER", router_path)

    _make_skill(skills_dir, "zznew", "Automates spreadsheet sync for sales teams.")
    _make_skill(skills_dir, "zzsec", "Hardens auth with firebase rules.")
    assert rr.main(["zznew", "zzsec"]) == 0

    out = router_path.read_text(encoding="utf-8")
    assert "12 installed" in out
    assert "`zznew` (D)" in out
    assert "`zzsec` (D)" in out


def test_main_skips_missing_skill(tmp_path, monkeypatch, capsys):
    import scripts.router_register as rr
    skills_dir = tmp_path / "skills"
    router_path = tmp_path / "router" / "SKILL.md"
    router_path.parent.mkdir(parents=True)
    router_path.write_text(_router_text(), encoding="utf-8")

    monkeypatch.setattr(rr, "SKILLS_DIR", skills_dir)
    monkeypatch.setattr(rr, "ROUTER", router_path)

    assert rr.main(["ghost-skill"]) == 0
    out = router_path.read_text(encoding="utf-8")
    assert "10 installed" in out
    assert "ghost-skill" not in out
    assert "[skip] ghost-skill: not found" in capsys.readouterr().out
