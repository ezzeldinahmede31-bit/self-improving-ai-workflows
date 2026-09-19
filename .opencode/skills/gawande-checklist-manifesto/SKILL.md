---
name: gawande-checklist-manifesto
description: "Makes complex work reliable with checklists: design, discipline, and culture. Use when the user says 'checklist', 'pilot checklist', 'surgical safety', 'Gawande', 'reduce errors', 'pre-flight', or when skilled people keep failing at basics under pressure."
---

# Gawande Checklist Manifesto

Distilled from Atul Gawande's *The Checklist Manifesto*: expertise fails
predictably under complexity + pressure + fallibility — well-designed
checklists (not more training, not more heroism) are the proven fix, from
cockpits to operating rooms to data centers.

## Purpose

Eliminate avoidable failures in complex, high-stakes work with checklists
people actually use — short, tested, and culturally enforced.

## Design rules (checklists that work vs wallpaper)

1. **Two types, two moments.** READ-DO (read then perform: unfamiliar/
   critical sequences like startup configs) vs DO-CONFIRM (perform from
   memory, then verify: routine expert work like pre-deploy). Pick per task
   — wrong type breeds resentment and skipping.
2. **Killer items only (5-9).** Checklists capture what experience shows
   gets missed under pressure, NOT every step (procedures live in manuals).
   Each item earns its place with a past failure or a near-miss; annual
   culling of items that never catch anything.
3. **Precise language, one page.** Exact terms from the work (no synonyms —
   ambiguity kills), fit on one screen/page, typography that scans (bold
   critical values). Test with real users doing real work, revise from
   observed skips.
4. **Pause points, owned.** Checklist runs at DEFINED pauses (before
   takeoff, before incision, before deploy) with a NAMED reader and verbal
   confirmation from the team. Unowned checklists are unread checklists.
5. **Culture carries it.** Leadership uses them first and visibly; skipping
   is a reportable event, not a time-saver; near-miss reports feed checklist
   evolution. A checklist people mock is a design failure — redesign with
   the mockers, don't mandate harder.

## Where they pay most (deploy first)

Deployments/releases, incident response (war-time checklists beat memory),
onboarding/offboarding access, data migrations, surgical business
operations (payroll, compliance filings), any procedure where one missed
step cascades.

## Verification

Per checklist: usage rate measured, near-miss log reviewed monthly, annual
cull performed, pause-point ownership named. A checklist with 100% design
quality and 20% usage is a failed implementation — fix adoption, not format.

## Pairs with

- `human-approval-gates` (checkpoints in automation),
  `n8n-delivery-verification-gate` (delivery proof),
  `incident-response-ai-failures-hallucinations` (war checklists),
  `carpenter-work-the-system` (systems that host checklists).
