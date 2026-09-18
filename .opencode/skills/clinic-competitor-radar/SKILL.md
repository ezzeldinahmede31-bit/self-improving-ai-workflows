---
name: clinic-competitor-radar
description: Competitor intelligence for the clinic system: leaders watchlist, structure-level imitation, trend memory. Use when the user says "competitors", "المنافسين", "who leads", "نقلد مين", "trend history", "الترندات القديمة", or before copying any idea.
---

# Competitor Radar

## Purpose

Watch ONLY the leaders, imitate structure (never content), and keep a memory
of old trends so patterns compound. Single purpose: COMPETITIVE INTELLIGENCE.

## Leaders watchlist (verified sources, 2025-2026)

| Leader | Why they lead | Steal the structure |
|---|---|---|
| Adit (adit.com, 10k+ professionals) | AI Call Intelligence + missed-call recovery math + case studies | Missed-call loss calculator posts; "we answer what you miss" framing |
| Practice by Numbers (5k+ providers) | Marketing IQ/ROI dashboards, 600+ KPIs | Numbers-first content: one metric per video, dashboard on screen |
| Solutionreach (solutionreach.com) | Benchmark reports (DSO 2026), missed-call case studies, AI Receptionist | Annual benchmark post; "when calls go unanswered" story spine |
| Clinit Egypt (clinit.app) | AI recall priority, SEO clinic profiles, WhatsApp-first, reseller program | WhatsApp > SMS proof; Arabic-first demos; partner angle |
| Top dental creators (Modash Aug 2026: jerry_rdh 129k/4% ER; dentalchick 250k) | Humor+education mix, team videos, trending sounds | Office-team formats; myth-busting spine; sound-first editing |
| Dr. Lam pattern (Houstonia, Mar 2025, 420k followers) | Fun office team, trends participation, approachability | "Clinic is family" series; staff faces (ours: hands/screens, faceless) |

## Leaders-only imitation protocol

1. Pick a leader asset with PROVEN numbers (views, ER, or revenue claim).
2. Deconstruct structure ONLY: hook (first line), format (talking/screen/skit),
   pacing, CTA, posting cadence. Never copy words, footage, or claims.
3. Map to OUR pillar + OUR proof (our screen recordings, our numbers).
4. Originality gate: if >30% textual overlap with source → rewrite.
5. Log: source URL + structure + our adaptation in the trend memory.

## Trend memory (old trends) + live watch

- Every radar digest is archived: Redis `trend-radar:digest:<YYYY-MM-DD>`
  (30-day TTL) by the `Archive Daily Digest` node in `clinic_trend_radar`.
- `clinic_competitor_watch` runs weekly (Sunday 18:00 Cairo + headerAuth
  webhook): Google News multi-OR feed (Adit, PbN, Solutionreach, Clinit,
  NexHealth, AY Automate, NextAutomation, Flowlyn, Goodspeed, Lindy) →
  top moves + imitable formats → Telegram digest. YouTube/LinkedIn/TikTok
  surfaces have no free server API — covered by monthly manual review below.
- Weekly review (Sunday): which angles repeated? Which pillars converted to
  WhatsApp starts? Promote repeat winners to evergreen; retire losers.
- Rule: a format that worked twice becomes a template; a topic that failed
  twice is banned for 60 days.

## Verification

Every imitation must cite: leader + asset + numbers + our adaptation. No
citation = plagiarism risk = rejected. Trend memory checked weekly.

## Pairs with

- `clinic-audience-os` (step 3-4: choose + time) · `clinic-organic-sales-content` (pillars)
- `psych-school-power` (frame the battlefield) · `biz-school-strategy` (category)
- AUTO-CONSULT: loaded on every content-planning task alongside the OS.
