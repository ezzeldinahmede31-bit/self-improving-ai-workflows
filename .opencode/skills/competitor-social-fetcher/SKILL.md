---
name: competitor-social-fetcher
description: Social lane of competitor watch: YouTube winners via yt-dlp, imitable formats digest. Use when the user says "social competitors", "سوشيال المنافسين", "فيديوهات المنافسين", "who wins on YouTube", "add a channel", or before copying any competitor video idea.
---

# Competitor Social Fetcher

## Purpose

Monitor competitors' YouTube (server-side, no API key) and report formats
worth structure-level imitation. Single purpose: SOCIAL WINNERS.

## How it works

- **YouTube lane** — `scripts/comp_social_watch.py` pulls latest videos per
  verified channel via yt-dlp `--flat-playlist` (channel IDs, never guessable
  @handles), ranks by views, Nemotron picks top-5 imitable formats, Telegram
  digest. Cron Wed+Sun 12:00 Cairo.
- **TikTok lane (LIVE)** — `scripts/tiktok_watch.py` drives headed Chromium
  (Xvfb-safe, fresh context per creator) over public creator pages, extracts
  captions + play counts, same analyze→digest flow. Proven: 10.2M-view denture
  repair, 4M-view humor. Cron Wed+Sun 13:00 Cairo. Manual run:
  `xvfb-run -a venv/bin/python scripts/tiktok_watch.py --dry-run`.
- Proven winners so far: Solutionreach "Meet Daryl" character series
  (150k-273k views); labtechlee repair-with-me (10.2M).

## Adding a channel (verification mandatory)

1. Resolve the REAL channel: `yt-dlp --flat-playlist --print "%(channel)s | %(channel_id)s" "ytsearch1:<brand> <topic>"`.
2. Test fetch: 2+ videos with view counts. Handles that 404 or return junk
   (seen live: @LindyAI hijack, @GumloopAI 404) are REJECTED, never added.
3. Append `(Name, ID-or-verified-handle)` to CHANNELS, dry-run, then live.

## TikTok / LinkedIn path (updated)

- TikTok user pages block headless + anonymous scraping (proven: captcha wall,
  impersonation error, zero data) AND defeat TikTokApi parsing (KeyError on
  current responses). What works: headed Chromium + fresh context per creator.
- LinkedIn still needs login: EITHER free Apify token (`APIFY_TOKEN` in `.env`)
  OR one-time visible login into the persistent Chrome profile (user types
  credentials once, session reused). Until then: monthly manual review.

## Verification

- `--dry-run` must show `channels ok: N/N` with view counts before any live send.
- Every digest cites channel + title + views. No citation = don't copy.

## Pairs with

- `clinic-competitor-radar` (news lane + imitation protocol) · `clinic-audience-os` (step 3)
- `media-downloader-extractor` (yt-dlp sibling) · `nvidia-nim-integrator` (LLM)
- AUTO-CONSULT: loaded with the radar on every content-planning task.
