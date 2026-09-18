---
name: competitor-social-fetcher
description: Social lane of competitor watch: YouTube winners via yt-dlp, imitable formats digest. Use when the user says "social competitors", "سوشيال المنافسين", "فيديوهات المنافسين", "who wins on YouTube", "add a channel", or before copying any competitor video idea.
---

# Competitor Social Fetcher

## Purpose

Monitor competitors' YouTube (server-side, no API key) and report formats
worth structure-level imitation. Single purpose: SOCIAL WINNERS.

## How it works

- `scripts/comp_social_watch.py` pulls latest videos per verified channel via
  yt-dlp `--flat-playlist` (channel IDs, never guessable @handles), ranks by
  views, Nemotron picks top-5 imitable formats, Telegram digest to the owner.
- Schedule: cron Wed + Sun 12:00 Cairo (see Install). Manual run anytime:
  `venv/bin/python scripts/comp_social_watch.py --dry-run` first.
- Proven winners so far: Solutionreach "Meet Daryl" character series
  (150k-273k views) — character-led AI-receptionist stories.

## Adding a channel (verification mandatory)

1. Resolve the REAL channel: `yt-dlp --flat-playlist --print "%(channel)s | %(channel_id)s" "ytsearch1:<brand> <topic>"`.
2. Test fetch: 2+ videos with view counts. Handles that 404 or return junk
   (seen live: @LindyAI hijack, @GumloopAI 404) are REJECTED, never added.
3. Append `(Name, ID-or-verified-handle)` to CHANNELS, dry-run, then live.

## TikTok / LinkedIn path (needs free Apify token)

- yt-dlp TikTok user pages fail anonymously (proven: impersonation error);
  LinkedIn needs login. Both unlock with a free Apify token ($5/mo free):
  user creates it once at console.apify.com, saves as `APIFY_TOKEN` in `.env`,
  then this skill gains tiktok-scrape + linkedin scrapers. Until then: monthly
  manual review (3 accounts, structure notes only).

## Verification

- `--dry-run` must show `channels ok: N/N` with view counts before any live send.
- Every digest cites channel + title + views. No citation = don't copy.

## Pairs with

- `clinic-competitor-radar` (news lane + imitation protocol) · `clinic-audience-os` (step 3)
- `media-downloader-extractor` (yt-dlp sibling) · `nvidia-nim-integrator` (LLM)
- AUTO-CONSULT: loaded with the radar on every content-planning task.
