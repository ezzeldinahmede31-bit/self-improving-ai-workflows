"""Tests for scripts/whop_campaign_monitor.py (offline, stdlib only)."""

import json
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "whop_campaign_monitor.py"

sys.path.insert(0, str(ROOT / "scripts"))
import whop_campaign_monitor as wcm


def test_score_bounds_and_order():
    rich = {"reward_per_thousand": 6.0, "total_budget": 100.0, "budget_left": 100.0,
            "total_creators": 0, "runway_days": 30.0}
    poor = {"reward_per_thousand": 0.2, "total_budget": 100.0, "budget_left": 1.0,
            "total_creators": 5000, "runway_days": 0.2}
    rich_score = wcm.opportunity_score(rich)
    poor_score = wcm.opportunity_score(poor)
    assert 0.0 <= poor_score <= 100.0
    assert 0.0 <= rich_score <= 100.0
    assert rich_score > poor_score
    assert rich_score > 80.0


def test_filter_thresholds_and_sort():
    picks = wcm.filter_campaigns(
        wcm.SAMPLE_CAMPAIGNS, min_reward=1.0, min_budget_left=1000.0,
        max_progress=90.0, sort_by="opportunity", limit=10,
    )
    assert picks, "expected surviving picks from sample feed"
    for item in picks:
        assert item["reward_per_thousand"] >= 1.0
        assert item["budget_left"] >= 1000.0
        assert item["progress_pct"] <= 90.0
    scores = [p["opportunity"] for p in picks]
    assert scores == sorted(scores, reverse=True)


def test_platform_filter():
    picks = wcm.filter_campaigns(wcm.SAMPLE_CAMPAIGNS, platforms=["x"], limit=10)
    assert picks == []


def test_max_creators_cap():
    picks = wcm.filter_campaigns(wcm.SAMPLE_CAMPAIGNS, max_creators=100, limit=10)
    assert picks
    assert all(p["total_creators"] <= 100 for p in picks)


def test_detect_new():
    current = [{"campaign_url": "u1"}, {"campaign_url": "u2"}]
    assert len(wcm.detect_new(["u1"], current)) == 1
    assert wcm.detect_new([], current) == current
    assert wcm.detect_new(["u1", "u2"], current) == []


def test_brief_shape():
    item = {"brand": "Demo", "title": "Demo title"}
    brief = wcm.make_brief(item)
    assert len(brief["hooks"]) == 3 and all(brief["hooks"])
    assert brief["caption"] and "Whop" in brief["caption"]
    assert brief["tags"] and brief["cta"] == "Follow for part 2."
    assert len(brief["checklist"]) >= 5
    assert brief["disclosure"]


def test_sample_end_to_end_json(tmp_path):
    out = tmp_path / "picks.json"
    code = subprocess.run(
        [sys.executable, str(SCRIPT), "--sample", "--top", "3",
         "--out", str(out), "--json"],
        capture_output=True, text=True, timeout=60,
    )
    assert code.returncode == 0, code.stderr
    report = json.loads(code.stdout)
    assert report["source"] == "sample"
    assert len(report["picks"]) == 3
    assert all("brief" in p and "opportunity" in p for p in report["picks"])
    assert json.loads(out.read_text(encoding="utf-8"))["source"] == "sample"


def test_state_roundtrip(tmp_path):
    state = tmp_path / "seen.json"
    first = subprocess.run(
        [sys.executable, str(SCRIPT), "--sample", "--top", "2",
         "--state", str(state), "--json"],
        capture_output=True, text=True, timeout=60,
    )
    assert first.returncode == 0, first.stderr
    second = subprocess.run(
        [sys.executable, str(SCRIPT), "--sample", "--top", "2",
         "--state", str(state), "--json"],
        capture_output=True, text=True, timeout=60,
    )
    assert second.returncode == 0, second.stderr
    report = json.loads(second.stdout)
    assert report["fresh_urls"] == []


def test_live_without_token_fails_clean():
    code = subprocess.run(
        [sys.executable, str(SCRIPT), "--live"],
        capture_output=True, text=True, timeout=60, env={},
    )
    assert code.returncode == 2
    assert "APIFY_API_TOKEN" in code.stderr


def test_text_free_of_banned_tokens():
    text = SCRIPT.read_text(encoding="utf-8").lower()
    for token in ("subprocess", "os.system", "169.254", "sk-"):
        assert token not in text
    assert "eval(" not in text
