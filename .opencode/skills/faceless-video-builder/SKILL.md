---
name: faceless-video-builder
description: Free faceless video pipeline: 1 AI image per scene + Arabic voiceover + captions + assembly. Use when the user says "video builder", "فيديو ديمو", "assemble video", "مشهد لكل صورة", "render video", "Nano Banana", or before producing any faceless video.
---

# Faceless Video Builder

## Purpose

Turn scenes JSON into a finished vertical MP4 with ZERO cost: one AI image
per scene, Arabic voiceover, burned captions, motion, concat. Single purpose:
RENDER video from scenes.

## Free stack (verified live, Sep 2026)

| Layer | Tool | Cost | Proof |
|---|---|---|---|
| Scene images | Pollinations flux, 720x1280, keyless | $0 | live JPEGs |
| Voice + SRT | edge-tts ar-EG-SalmaNeural | $0 | live MP3 + timed SRT |
| Assembly | imageio-ffmpeg (Ken Burns zoompan, concat, libass) | $0 | 37s 720x1280 MP4 |
| Fonts | Noto Kufi Arabic (system) | $0 | verified rendered Arabic |

Nano Banana honesty: the NAME covers Gemini image models; the Gemini API has
NO free tier for image models (limit 0, Google staff confirm) — the free route
is the Gemini APP (~20/day, manual UI). Our script supports `--provider gemini`
only with a billing-enabled `GEMINI_API_KEY`; default stays pollinations.
Watermark note: pollinations stamps its logo despite nologo → cropped in-chain.

## Usage

- `venv/bin/python scripts/faceless_video_builder.py --demo` (5-scene sales demo)
- `... --scenes scenes.json` where scenes = `[{image, voice}, ...]` (Phase-2
  generator emits exactly this shape, one image prompt per scene).
- `... --demo --no-voice` for fast silent previews. Output: `output/faceless_<ts>.mp4`.

## Hard rules

- ONE image per scene, never a slideshow of one image (user rule: مشهد واحد كل مرة).
- Arabic captions always burned (quoted FontName) + SRT sidecar kept.
- Verify every render: duration>0, 720x1280+h264+aac, one eyeballed frame.

## Pairs with

- `clinic-organic-sales-content` (pillars/scripts in) · `psych-school-attention` (edit rules)
- `video-processing-editing` (FFmpeg deep dives) · `clinic-audience-os` (pipeline owner)
