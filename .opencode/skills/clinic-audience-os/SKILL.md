---
name: clinic-audience-os
description: Master operating system binding all psychology schools, the 2000-book index, and sales skills into one pipeline. Use when the user says "audience OS", "اربط كل حاجة", "understand my client", "what content when", "ازاي ابيع", "نقول ايه", or before ANY audience/content/sales decision.
---

# Clinic Audience OS

## Purpose

One pipeline that binds EVERYTHING built so far — 7 psych schools, the
2000-book index (`memory/psychology-books-index.json`), Machiavelli file,
`clinic-buyer-psychology`, `clinic-organic-sales-content` — into answers for:
who is the client, what content, when to post, how to market, how to sell,
what to say. Single purpose: ORCHESTRATE the binding.

## The 7-step run (never skip order)

1. **LOAD the client** → `clinic-buyer-psychology` (motivations/fears/objections).
2. **CONSULT the books** → `scripts/psych_lookup.py --school <relevant> --top 5`
   (or `--query <objection keyword>`). Cite rank + title in the reasoning.
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

## Pairs with

- All `psych-school-*` (knowledge) · `clinic-buyer-psychology` (profile)
- `clinic-organic-sales-content` (distribution) · `clinic-trend_radar` (angles in)
- AUTO-CONSULT: this skill loads FIRST on any audience/content/sales task.
