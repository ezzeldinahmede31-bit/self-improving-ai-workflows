---
name: video-ad-system
description: Brief-to-MP4 ad system that makes a weak model beat strong models via scaffolding. Use when the user says 'اعمل فيديو اعلاني', 'ad video', 'UGC ad', 'منتج + تعليق صوتي', 'brief to video', 'clinic ad', 'عيد الفيديو ده', or any ad-video build.
---

# Video Ad System

Same philosophy as the AI-automation system: a weak generator + strong
scaffolding beats a strong model alone. Pipeline: BRIEF -> PSYCHOLOGY ->
SCRIPT variants -> MECHANICAL GATES -> RENDER -> FRAME VERIFY -> DELIVER.

## Stack (free local only)

- Script + psychology: any LLM (weak is fine, gates carry quality).
- Images: pollinations flux 720x1280 keyless (default).
- Voice + SRT: edge-tts ar-EG-SalmaNeural (free).
- Assembly: imageio-ffmpeg Ken Burns + burned Arabic captions + concat.
- Builder: `scripts/faceless_video_builder.py --demo | --scenes X.json`.
- Gates: `scripts/video_ad_pipeline.py <brief.json>` (exit 0 = READY).

## Mandatory order (never skip)

1. BRIEF: scenes JSON 3-5 items `{image, voice}` + last scene CTA
   (ديمو/واتساب/احجز). Generic briefs allowed (any product later).
2. PSYCHOLOGY: `audience-psychology-analyst` profile + 2-3 levers +
   edit spec (hook 0-3s, pacing, peak-end, re-hook ~20s, one message/beat).
   Store under `_gates.psychology` in the brief.
3. SCRIPT: 3 parallel hook variants, pick via hook-system rules
   (close-up + curiosity gap + promise text). Cap 45 words/scene.
   Hedge bare stats (ممكن/شبه) or cite source. Never fake scarcity.
4. GATES: `video_ad_pipeline.py` must print READY_FOR_PRODUCTION (RC 0).
   Fix violations, never work around them.
5. RENDER: `faceless_video_builder.py --scenes brief.json` (or `--demo`
   for the clinic ad). Output `output/faceless_<ts>.mp4` + SRT sidecar.
6. VERIFY: duration>0, 720x1280, h264+aac, one eyeballed frame,
   voice audible per scene, captions readable, CTA present.
7. DELIVER: evidence table REQ -> evidence -> PASS/FAIL. Never deliver
   unrendered. Send MP4 + brief + gates log.

## Both ad types

- UGC talking style: close-up hook scene + direct voice (بص/عارف) + CTA.
- Product + voiceover: product close-ups + proof scene + CTA.
- Default export: 15-30s target, 9:16, 720x1280, 30fps.

## Pairs with

- `faceless-video-builder` (render) · `audience-psychology-analyst` (profile)
- `viral-hooks` + `ad-creative` hook-system (hooks) · `clinic-organic-sales-content` (clinic pillar)
- `video-processing-editing` (FFmpeg) · `build-gates-pipeline` (code gates)
