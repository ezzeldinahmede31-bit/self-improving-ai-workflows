#!/usr/bin/env python3
"""whop_campaign_monitor.py — offline-first Whop Content Rewards helper.

Baseline (best-practice-first, cited):
  - Campaign feed schema mirrors Apify actor
    `tactful_anvil/whop-content-rewards-scraper` (top adoption in Store
    search, HTTP-only, filterable feed with reward per 1K views, budget
    left, runway, payout velocity, composite opportunity score).
  - Clip pipeline shape follows n8n template 9867 (long video -> viral
    moments -> titles/captions -> scheduled shorts). This script covers
    the planning half in pure stdlib Python: rank campaigns, emit a
    posting brief per winner (hooks + caption + tags + single CTA +
    disclosure checklist). Cutting/posting stay human-side (platform
    logins + phone verification cannot run headless).

Usage:
    venv/bin/python scripts/whop_campaign_monitor.py --sample --top 3
    venv/bin/python scripts/whop_campaign_monitor.py --input campaigns.json --top 5 --out picks.json
    venv/bin/python scripts/whop_campaign_monitor.py --sample --state memory/whop_seen.json --top 3

Live fetch (optional, off by default):
    --live --actor tactful_anvil/whop-content-rewards-scraper
    reads APIFY_API_TOKEN from the environment. Never pass tokens as argv.
    Without a token the script runs fully offline on --sample/--input.

Outputs JSON: ranked picks with scores + briefs. Exit 0 on success.
"""

import argparse
import json
import os
import sys
import time
import urllib.request
import urllib.error

ACTOR_DEFAULT = "tactful_anvil/whop-content-rewards-scraper"
APIFY_API = "https://api.apify.com"

# Sample rows shaped like public 2026 listings. Marked sample:true.
# Figures echo published examples (Roobet-style, Yomi-style) for offline runs.
SAMPLE_CAMPAIGNS = [
    {
        "title": "Sample: sportsbook clipping",
        "brand": "SampleBrand A",
        "reward_per_thousand": 1.5,
        "total_budget": 250000.0,
        "budget_left": 190000.0,
        "total_creators": 420,
        "progress_pct": 24.0,
        "platforms": ["tiktok", "youtube", "instagram"],
        "campaign_url": "https://whop.com/sample/a",
        "campaign_type": "clipping",
        "runway_days": 21.0,
        "sample": True,
    },
    {
        "title": "Sample: creator clipping FR",
        "brand": "SampleBrand B",
        "reward_per_thousand": 1.0,
        "total_budget": 238000.0,
        "budget_left": 190500.0,
        "total_creators": 192,
        "progress_pct": 20.0,
        "platforms": ["instagram", "tiktok", "youtube"],
        "campaign_url": "https://whop.com/sample/b",
        "campaign_type": "clipping",
        "runway_days": 30.0,
        "sample": True,
    },
    {
        "title": "Sample: podcast clipping",
        "brand": "SampleBrand C",
        "reward_per_thousand": 2.0,
        "total_budget": 10000.0,
        "budget_left": 8200.0,
        "total_creators": 60,
        "progress_pct": 18.0,
        "platforms": ["tiktok", "instagram", "youtube"],
        "campaign_url": "https://whop.com/sample/c",
        "campaign_type": "clipping",
        "runway_days": 12.0,
        "sample": True,
    },
    {
        "title": "Sample: UGC on-camera",
        "brand": "SampleBrand D",
        "reward_per_thousand": 3.5,
        "total_budget": 4000.0,
        "budget_left": 3100.0,
        "total_creators": 25,
        "progress_pct": 22.5,
        "platforms": ["youtube", "instagram", "tiktok"],
        "campaign_url": "https://whop.com/sample/d",
        "campaign_type": "ugc",
        "runway_days": 9.0,
        "sample": True,
    },
    {
        "title": "Sample: drained pool (skip)",
        "brand": "SampleBrand E",
        "reward_per_thousand": 0.3,
        "total_budget": 1000.0,
        "budget_left": 40.0,
        "total_creators": 900,
        "progress_pct": 96.0,
        "platforms": ["tiktok"],
        "campaign_url": "https://whop.com/sample/e",
        "campaign_type": "clipping",
        "runway_days": 0.5,
        "sample": True,
    },
]


def _num(value, default=0.0):
    try:
        result = float(value)
    except (TypeError, ValueError):
        return default
    if result != result:  # NaN guard
        return default
    return result


def opportunity_score(item):
    """Composite 0-100: reward 35 / headroom 25 / low rivalry 25 / runway 15.

    Mirrors the actor baseline weighting so offline ranks match the feed.
    """
    reward = _num(item.get("reward_per_thousand"))
    total_budget = _num(item.get("total_budget"))
    budget_left = _num(item.get("budget_left"))
    total_creators = _num(item.get("total_creators"))
    runway = _num(item.get("runway_days"), default=7.0)

    reward_part = min(reward / 6.0, 1.0)
    headroom = (budget_left / total_budget) if total_budget > 0 else 0.0
    headroom = max(0.0, min(headroom, 1.0))
    rivalry = 1.0 / (1.0 + total_creators / 100.0)
    runway_part = min(runway / 30.0, 1.0)
    score = 35.0 * reward_part + 25.0 * headroom + 25.0 * rivalry + 15.0 * runway_part
    return round(max(0.0, min(score, 100.0)), 1)


def normalize(item):
    """Accept actor-shaped or short keys; return canonical dict."""
    get = item.get
    platforms = get("platforms") or get("socialPlatforms") or []
    platforms = [str(p).lower() for p in platforms]
    return {
        "title": str(get("title") or get("brand") or "untitled"),
        "brand": str(get("brand") or "unknown"),
        "reward_per_thousand": _num(get("reward_per_thousand", get("rewardPerThousandUsd"))),
        "total_budget": _num(get("total_budget", get("totalBudgetUsd"))),
        "budget_left": _num(get("budget_left", get("budgetLeftUsd"))),
        "total_creators": int(_num(get("total_creators", get("creatorsCount")))),
        "progress_pct": _num(get("progress_pct", get("progressPercentage"))),
        "platforms": platforms,
        "campaign_url": str(get("campaign_url", get("campaignUrl") or "")),
        "campaign_type": str(get("campaign_type", get("payoutType") or "clipping")).lower(),
        "runway_days": _num(get("runway_days", get("minEstimatedDaysLeft") or 7.0), default=7.0),
        "sample": bool(get("sample", False)),
    }


def filter_campaigns(rows, min_reward=0.0, min_budget_left=0.0,
                     max_progress=100.0, max_creators=None,
                     platforms=None, sort_by="opportunity", limit=10):
    """Filter + score + sort. Pure function; no I/O."""
    wanted = {p.lower() for p in (platforms or [])}
    scored = []
    for raw in rows:
        item = normalize(raw)
        if item["reward_per_thousand"] < min_reward:
            continue
        if item["budget_left"] < min_budget_left:
            continue
        if item["progress_pct"] > max_progress:
            continue
        if max_creators is not None and item["total_creators"] > max_creators:
            continue
        if wanted and not (set(item["platforms"]) & wanted):
            continue
        item["opportunity"] = opportunity_score(item)
        scored.append(item)
    keys = {
        "opportunity": lambda r: r["opportunity"],
        "reward": lambda r: r["reward_per_thousand"],
        "budgetLeft": lambda r: r["budget_left"],
        "fewestCreators": lambda r: -r["total_creators"],
        "runway": lambda r: r["runway_days"],
    }
    key = keys.get(sort_by, keys["opportunity"])
    scored.sort(key=key, reverse=(sort_by != "fewestCreators"))
    if sort_by == "fewestCreators":
        scored.sort(key=lambda r: r["total_creators"])
    return scored[: max(1, limit)]


def detect_new(previous_urls, current_rows):
    """Return rows whose URL was absent in the prior run."""
    seen = set(previous_urls or [])
    return [r for r in current_rows if r.get("campaign_url") not in seen]


def make_brief(item):
    """Posting brief: hooks + caption + tags + single CTA + checklist."""
    brand = item.get("brand", "the brand")
    title = item.get("title", "this campaign")
    hooks = [
        "First 3 seconds: show the result before the setup — %s payoff first." % brand,
        "Hold to the end: the clip hides one detail that changes the story.",
        "POV: you found the %s clip everyone will repost tomorrow." % brand,
    ]
    caption = (
        "%s — full clip via %s. Follow for part 2. "
        "Ad: paid clipping via Whop Content Rewards." % (title, brand)
    )
    tags = ["#clipping", "#whop", "#viralclip", "#shorts", "#fyp"]
    checklist = [
        "Use only the campaign source material named in the rules page.",
        "Link social accounts in Whop BEFORE posting (views prior to linking may not verify).",
        "Keep mandatory tags/credit exactly as written in the rules.",
        "Submit the post URL promptly with an analytics screenshot.",
        "Mark the post as a paid partnership where the platform offers it.",
        "Stop posting a pool whose remaining budget reads near zero.",
    ]
    return {
        "hooks": hooks,
        "caption": caption,
        "tags": tags,
        "cta": "Follow for part 2.",
        "checklist": checklist,
        "posting_windows": ["18:00", "21:00"],
        "disclosure": "Disclose paid clipping on every post.",
    }


def load_state(path):
    try:
        with open(path, "r", encoding="utf-8") as handle:
            data = json.load(handle)
        if isinstance(data, dict):
            return data
    except (OSError, ValueError):
        pass
    return {}


def save_state(path, payload):
    with open(path, "w", encoding="utf-8") as handle:
        json.dump(payload, handle, ensure_ascii=False, indent=2)


def apify_run_sync(token, actor_id, actor_input, timeout=120):
    """Run an Apify actor and return dataset items. Live path only."""
    base = APIFY_API.rstrip("/")
    start_url = "%s/v2/acts/%s/runs?token=%s" % (base, actor_id, token)
    payload = json.dumps(actor_input or {}).encode("utf-8")
    request = urllib.request.Request(
        start_url, data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            run = json.load(response).get("data", {})
    except urllib.error.URLError as exc:
        raise RuntimeError("apify start failed: %s" % exc)
    run_id = run.get("id")
    dataset_id = (run.get("defaultDatasetId") or "")
    deadline = time.time() + timeout
    status = run.get("status")
    while status not in ("SUCCEEDED", "FAILED", "ABORTED", "TIMED-OUT"):
        if time.time() > deadline:
            raise RuntimeError("apify run timed out waiting for terminal state")
        time.sleep(5)
        poll_url = "%s/v2/actor-runs/%s?token=%s" % (base, run_id, token)
        try:
            with urllib.request.urlopen(poll_url, timeout=30) as response:
                run = json.load(response).get("data", {})
        except urllib.error.URLError as exc:
            raise RuntimeError("apify poll failed: %s" % exc)
        status = run.get("status")
        dataset_id = run.get("defaultDatasetId") or dataset_id
    if status != "SUCCEEDED":
        raise RuntimeError("apify run ended with state %s" % status)
    items_url = "%s/v2/datasets/%s/items?token=%s&clean=true" % (base, dataset_id, token)
    try:
        with urllib.request.urlopen(items_url, timeout=60) as response:
            items = json.load(response)
    except urllib.error.URLError as exc:
        raise RuntimeError("apify dataset fetch failed: %s" % exc)
    return items if isinstance(items, list) else []


def build_parser():
    parser = argparse.ArgumentParser(description="Rank Whop Content Rewards pools offline-first.")
    parser.add_argument("--sample", action="store_true")
    parser.add_argument("--input", default="")
    parser.add_argument("--top", type=int, default=3)
    parser.add_argument("--min-reward", type=float, default=1.0)
    parser.add_argument("--min-budget", type=float, default=1000.0)
    parser.add_argument("--max-progress", type=float, default=90.0)
    parser.add_argument("--max-creators", type=int, default=0)
    parser.add_argument("--platform", action="append", default=[])
    parser.add_argument("--sort", default="opportunity",
                        choices=["opportunity", "reward", "budgetLeft", "fewestCreators", "runway"])
    parser.add_argument("--state", default="")
    parser.add_argument("--out", default="")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--live", action="store_true")
    parser.add_argument("--actor", default=ACTOR_DEFAULT)
    return parser


def main(argv=None):
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.sample and args.input:
        print("use only one of --sample or --input.", file=sys.stderr)
        return 2

    if args.live:
        token = os.environ.get("APIFY_API_TOKEN", "")
        if not token:
            print("APIFY_API_TOKEN is not set; rerun offline with --sample.", file=sys.stderr)
            return 2
        actor_input = {
            "status": "active",
            "platforms": args.platform or [],
            "minRewardPerThousand": int(args.min_reward),
            "minBudgetLeftUsd": int(args.min_budget),
            "sortBy": "budgetLeft" if args.sort == "budgetLeft" else "opportunity",
            "maxItems": 200,
        }
        try:
            rows = apify_run_sync(token, args.actor, actor_input)
        except RuntimeError as exc:
            print(str(exc), file=sys.stderr)
            return 3
    elif args.input:
        with open(args.input, "r", encoding="utf-8") as handle:
            loaded = json.load(handle)
        rows = loaded if isinstance(loaded, list) else loaded.get("items", [])
    else:
        rows = SAMPLE_CAMPAIGNS

    picks = filter_campaigns(
        rows,
        min_reward=args.min_reward,
        min_budget_left=args.min_budget,
        max_progress=args.max_progress,
        max_creators=(args.max_creators or None),
        platforms=args.platform,
        sort_by=args.sort,
        limit=args.top,
    )
    fresh = []
    if args.state:
        prior = load_state(args.state)
        fresh = detect_new(prior.get("seen_urls", []), picks)
        seen = set(prior.get("seen_urls", []))
        for row in picks:
            if row.get("campaign_url"):
                seen.add(row["campaign_url"])
        save_state(args.state, {"seen_urls": sorted(seen)})

    report = {
        "picks": [{**p, "brief": make_brief(p)} for p in picks],
        "fresh_urls": [r.get("campaign_url") for r in fresh],
        "source": "live" if args.live else ("input" if args.input else "sample"),
    }
    text = json.dumps(report, ensure_ascii=False, indent=2)
    if args.out:
        with open(args.out, "w", encoding="utf-8") as handle:
            handle.write(text)
    if args.json or not args.out:
        print(text)
    else:
        print("wrote %d picks to %s" % (len(picks), args.out))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
