---
name: clinic-audience-os
description: Master operating system binding all psychology schools, the 2000-book index, and sales skills into one pipeline. Use when the user says "audience OS", "اربط كل حاجة", "understand my client", "what content when", "ازاي ابيع", "نقول ايه", or before ANY audience/content/sales decision.
---

# Clinic Audience OS

## Purpose

One pipeline that binds EVERYTHING built so far — 9 psych/business schools,
three book indexes (`memory/psychology-books-index.json` 6000 +
`memory/marketing-books-index.json` 3000 + `memory/business-books-index.json`
2200+, queried via `scripts/psych_lookup.py --lib psych|marketing|business|all`),
Machiavelli file, `clinic-buyer-psychology`, `clinic-organic-sales-content`,
`clinic-competitor-radar` (leaders watchlist + leaders-only imitation),
live `clinic_trend_radar` (daily angles, archived 30d) and `clinic_audience_pulse`
(daily 07:00 Cairo owner pains) + platform map `memory/audience-platforms-eg.md`
(platform × age × country with 2026 sources + watchlist) — into answers for:
who is the client, what content, when to post, how to market, how to sell,
what to say. Single purpose: ORCHESTRATE the binding.

## The 7-step run (never skip order)

1. **LOAD the client** → `clinic-buyer-psychology` (motivations/fears/objections)
   + weekly `clinic_audience_pulse` digest (live Egypt owner pains).
2. **CONSULT the books** → `scripts/psych_lookup.py --lib all --school <relevant> --top 5`
   (or `--query <objection keyword>`). Cite lib + rank + title in the reasoning.
3. **CHECK leaders** → `clinic-competitor-radar` (imitate structure of proven
   winners only) + trend memory (repeat winners become templates).
3. **CHOOSE content** → pillar from `clinic-organic-sales-content`
   (pain/proof/objection/authority) matched to the objection.
4. **TIME it** → Cairo slots 1pm (break) / 9-11pm (after clinic); LinkedIn
   repost Sunday 9pm. Test 2 weeks, keep winners.
5. **MARKET it** → levers from the loaded schools (loss frame + peer proof
   by default; add scarcity/commitment only if honest).
6. **SELL it** → offer path: free demo → paid pilot → monthly; objections
   answered from `psych-school-decision` + `psych-school-power` (daylight test).
7. **SAY it** → script in Egyptian Arabic using the 45-60s template; every
   claim carries its school/book source. No source = cut the line.

## School router (which schools per job)

| Job | Schools to load |
|---|---|
| Understand hesitation | decision + emotion |
| Pick video angle | attention + persuasion |
| Write proof piece | social + persuasion |
| Price/package | decision + power |
| Beat competitor | power + social |
| Retention/recall | emotion + decision |
| LinkedIn authority | foundations + persuasion |

## Verification

Every output must contain: client profile line, ≥2 cited books (rank+title),
pillar name, slot time, lever names, offer step, script. Missing item = rerun
the step. No invented stats, no fake scarcity, no anonymous proof.
Citation format per claim: Mechanism → strength (strong/moderate/inspired-by)
→ exact source. Audience facts need our data or hedging (ممكن/أغلب); never
present a copywriting illustration as a research finding.
7. **CLAIMS GATE before publishing**: every sales copy MUST pass
   `venv/bin/python scripts/claims_review.py --text <file>` with VERDICT PASS
   (exit 0). FAIL = rewrite, never publish. WARN = human decides.

## Pairs with

- All `psych-school-*` (knowledge) · `clinic-buyer-psychology` (profile)
- `clinic-organic-sales-content` (distribution) · `clinic-trend_radar` (angles in)
- AUTO-CONSULT: this skill loads FIRST on any audience/content/sales task.
