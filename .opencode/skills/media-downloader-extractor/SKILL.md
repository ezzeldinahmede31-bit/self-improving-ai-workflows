---
name: media-downloader-extractor
description: "Downloads and extracts video/audio streams from social-media links (Facebook Reels, YouTube, TikTok, Instagram) using yt-dlp — bypassing browser scrapers, Cloudflare JS challenges, and paywalls. Use whenever the task is a video/social link the regular page fetcher cannot read. Trigger phrases: 'watch this', 'get the video', 'fb reel', 'yt reel', 'download the reel', 'transcribe the reel'."
---

# MEDIA DOWNLOADER EXTRACTOR

## DIRECTIVE
A social video (Facebook Reel/YouTube Shorts/TikTok) is NOT a normal webpage:
the player + JS bundle defeats static fetchers. Pull the media bytes directly
with `yt-dlp` instead of pretending the HTML is content.

## EXECUTION STEPS
1. **Tooling:** `yt-dlp --version` (system `/usr/bin/yt-dlp` is available).
   `ffmpeg` is provided by `imageio-ffmpeg` in the venv when system ffmpeg
   is missing (`/home/.../venv/bin/ffmpeg` or `python -c
   "import imageio_ffmpeg;print(imageio_ffmpeg.get_ffmpeg_exe())"`).
2. **Download audio FIRST** (smallest payload, all transcription needs is the
   audio track):
   ```bash
   yt-dlp -x --audio-format mp3 -o "/tmp/reel_%(id)s.%(ext)s" "<URL>"
   ```
   `-x` = extract audio; `%(id)s` keeps filenames unique per video.
3. **If blocked by auth/restriction:** drop a real browser's cookies:
   ```bash
   yt-dlp --cookies-from-browser chrome -x --audio-format mp3 -o "/tmp/reel_%(id)s.%(ext)s" "<URL>"
   ```
4. **Fallback formats:** if mp3 fails, try `m4a`/`wav`. If the platform
   refuses audio-only, take the lowest video (`-f w`) and let ffmpeg strip
   audio.
5. **Handoff** the `.mp3`/`.wav` path to `audio-whisper-transcriber`.

## RULES
- Never write raw video to long-term storage; keep temp files under `/tmp`.
- If the first attempt errors (403/geoblock), do NOT loop blindly — escalate,
   report the exact error, then try cookies.
- Evidence over memory: capture and show `yt-dlp`'s stdout/exit before moving
   to transcription.

## Local adaptation
This machine: `/usr/bin/yt-dlp` present, `faster-whisper` installed in venv, and a
system Chrome at `/usr/bin/google-chrome` (usable for `--cookies-from-browser
chrome`). Output is piped to `audio-whisper-transcriber` in the same session. On
Facebook Reels, anonymous download usually works for public content; if it
returns a login wall, re-run with the chrome cookie fallback (cookies are only
read, never echoed).