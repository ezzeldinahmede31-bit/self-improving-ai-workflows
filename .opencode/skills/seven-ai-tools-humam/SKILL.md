---
name: seven-ai-tools-humam
description: Track and dispatch the AI tools from Humam Najdat's TikTok video 'اهم سبع ادوات للذكاء الاصطناعي' plus his adjacent Claude/dev tooling videos. Use when the user says 'ادوات الذكاء الاصطناعي السبعة', 'humam najdat tools', 'همام نجدت', 'best AI tools', 'Claude skill web developer', 'Apple-level Claude design', or asks which AI tool from those videos fits a task.
version: 1.0.0
---

# Seven AI Tools (Humam Najdat video intel)

## Purpose

Single tracker/dispatcher for the tool intel in HumamNajdat's TikTok video
7694794433325255958 ("اهم سبع ادوات للذكاء الاصطناعي", 52s) and his adjacent
tooling videos. Holds what is VERIFIED from page evidence, routes each known
tool to its install path in this workspace, and names the unknowns explicitly
so the user can fill the gaps (video bytes are anti-bot protected; yt-dlp
fails even with browser cookies — verified this session).

## When to use

- User references the seven-tools video or asks for its tool list/links.
- User asks which of Humam's tools fits a task (Claude dev, Apple-level
  design, LinkedIn growth, multi-model access, 3D design).
- User supplies one of the missing names/links — record it here, then dispatch.

## Verified entries (page evidence, this session)

1. **Claude-as-professional-web-developer skill** — video 7690296442111511830
   (5.7K views): a skill that makes Claude build high-level websites.
   Dispatch: `impeccable` (installed) + `frontend-design` for the design half.
2. **Apple-level Claude website design** — video 7682434502005689622 ("كيف
   تجعل Claude يصمّم مواقع بمستوى APPLE"). Dispatch: `impeccable`
   (`/impeccable init` then `craft`/`polish`) + `apple-ui-designer`.
3. **Human-looking AI websites** — video 7682710665227734274 ("كيف تجعل موقع
   الـ AI يبدو طبيعياً"). Dispatch: `impeccable` detector pass
   (`npx impeccable detect <dir>`) + `quieter`/`distill`.
4. **Claude + ChatGPT at the same time** — video 7689180003224849686 (multi-
   model access from one place). Dispatch: `litellm-tier-router` (model
   routing + failover) + `nvidia-nim-integrator` where applicable.
5. **Claude for LinkedIn growth** — video 7690663067985693974. Dispatch:
   `linkedin-automation` + `linkedin-content` + `audience-psychology-analyst`.
6. **Microsoft 3D-body design tool** — video 7674625780734889238. Status:
   NAME UNVERIFIED — candidate family only, do not install on this hint.
7. **Smart Claude file-upload method** — video 7677236185172921622 (4.4K
   views). Dispatch: `filesystem-context` (file-backed context discipline).

## Awaiting user fill-in (explicit unknowns)

- [ ] The exact 7 names/links as spoken in video 7694794433325255958.
- [ ] Item 6 (Microsoft 3D tool): exact product name + URL.
- [ ] Any DM-gated links ("علق بVIDEO واضغط الرابط في البايو", video
   7694362189544656151): paste them here; never invent URLs.

## Verification

- Every VERIFIED entry above cites a video ID reachable on TikTok; every
   dispatch target names an installed skill present in
   `memory/skills-library.md`. The unknowns list is non-empty until the user
   supplies the missing names — a delivery claiming all seven resolved
   without that input is REJECTED by this skill's own rule.

## Pairs with

- `impeccable` (design items 1-3) + `find-skills` (install a tool's real
   skill once its identity is confirmed) + `media-downloader-extractor`
   (retry the video bytes if TikTok access changes) +
   `evidence-over-memory` (no invented tool names/links, ever).
