---
name: omni-request-orchestrator
description: "MANDATORY skill-synthesis orchestrator for EVERY user request, no exceptions. Any task the user asks (understand a video edit, write copy, fix code, build a workflow, analyze a brand, edit a montage...) MUST run the full pipeline: (1) extract the underlying PURPOSE and TARGET AUDIENCE (ask if not given), (2) analyze that audience's psychology using the LATEST online reports/research (live web search, never memory), (3) choose a marketing strategy that matches that psychology, (4) hand all of it to the production skill (video-edit, copywriting, social, n8n...), (5) verify the output against the psychology. Psychology skills are NEVER optional — even skills that look unrelated (code, n8n) still get the audience/psychology pass because the user demands omnipresent orchestration. Trigger phrases: ANY request, especially 'افهم فيديو مونتاج', 'افهم الفيديو ده', 'اعمل مونتاج', 'اكتب اعلان', 'حلل الجمهور', 'مثال على', and any task where the user says nothing about audience — that MISSING info triggers the extraction step."
---

# Omni Request Orchestrator

This skill sits ABOVE all other skills. It never does the work itself — it
forces the work into a fixed 5-stage pipeline and hands each stage to the
right skill. It runs on EVERY request, whether the task looks related to
marketing or not (the user's rule: "لو قفلت شغل كل المهارات مع بعض حتي لو
انت شايف ان ملهمش علاقة").

## The 5 mandatory stages (never skip, never reorder)

### Stage 1 — Extract purpose + target audience
Before any production work:
- **Purpose**: what is this thing FOR? (sell / educate / entertain / convert /
  retain / inform). Ask one clarifying question ONLY if truly ambiguous.
- **Target audience**: who consumes this? If the user did not say → state your
  best inference, mark it as an assumption, and proceed (never block on it).
- Output a 3-line contract: `PURPOSE: ... | AUDIENCE: ... | CONSTRAINT: ...`

### Stage 2 — Audience psychology (LIVE research, not memory)
This stage is MANDATORY for every request, including code/n8n ones.
1. Load `audience-psychology-analyst` for the analysis framework (needs/
   motivations/fears/values/decision style/trust barriers).
2. Search the web for the LATEST psychological/behavioral reports about this
   audience: `web-search` + `deep-research` with queries like
   "audience X psychology 2026 report", "consumer behavior [niche] 2025 2026",
   "attention span video statistics 2026", "Gen Z / target group buying
   psychology report". ALWAYS 2025/2026 sources — dated data is a failure.
3. Distill: top 3-5 psychological drivers of THIS audience WITH citation to
   the found reports.

### Stage 3 — Marketing strategy matching that psychology
Load the persuasion stack and pick ONLY the levers that match Stage 2's
profile: `influence-psychology` (Cialdini 7) / `conversion-psychology` /
`persuasion-principles` / `marketing-psychology`. Output:
- 3-5 levers with the mechanism named (e.g. "loss aversion because report X
  shows this buyer fears missing out more than gaining").
- The offer/message framing derived from them.

### Stage 4 — Production handoff
Pass EVERYTHING from stages 1-3 to the execution skill:
- Video/montage → `video-edit` / `video-processing-editing` + `viral-hooks`
  (hooks per Stage-2 attention stats) + `video-inpainting` if needed.
- Copy/ads → `copywriting` / `conversion-psychology` framing.
- Social → `social-media` / `social-publisher` per-platform.
- Code/n8n → build per spec but STILL apply stages 1-3 first (audience =
  the end user of the automation; psychology = their trust/UX drivers).
The deliverable must contain an explicit "Psychological brief" section that
the production skill worked FROM, so the output is traceable.

### Stage 5 — Verify output against psychology
Read the final artifact and check: does it match the Stage-2 drivers? Does
the framing use the Stage-3 levers? Fix mismatches. Deliver a short
`verification note` (1-3 lines) stating what was checked.

## Rules (hard)
0. **Unknown-task fallback (the user's core rule):** if you are NOT sure
   which skills apply to a request (or the task is unusual/novel), do NOT
   pick a subset — fire the WHOLE relevant pack together and synthesize.
   "شغل كل المهارات مع بعض حتى لو انت شايف إن بعضهم ملهمش لزمة." Never
   leave a skill idle out of a sense that it looks unrelated: run the
   psychology pass, the research pass, the quality/security pass, the
   production pass — and let each contribute what it actually can. Cost of
   running one extra skill ≈ 0; cost of missing its input = wrong output.
1. Stage 2 runs on EVERY request — psychology is never "unrelated".
2. All sources in Stage 2 must be dated 2025+; if search fails, say so
   honestly instead of inventing reports.
3. One clarifying question max; otherwise proceed on stated assumptions.
4. The final answer to the user always includes the `PURPOSE/AUDIENCE`
   contract + the psychological brief (even if brief), so the pipeline is
   visible, not hidden.
5. Keep the whole pipeline fast: research = 2-4 searches max, extracts only.

## Activation
Say the pipeline line: `[omni] purpose=..., audience=..., stages=1-5 running`
then execute. This SKILL is the top of the stack — it routes to the router
(`compensatory-router`) skills per stage, it does not replace them.