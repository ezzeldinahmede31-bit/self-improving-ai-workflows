---
name: clarify-before-execute
description: "The user's mandatory discovery loop: when they give a request, DO NOT start building. First SEARCH (web / skills.sh / codebase) to ground the request in real context, then COME BACK and ask them the load-bearing clarifying questions (goal, exact output, audience, constraints, preferences, examples, what 'done' means), then restate a one-contract confirmation, and ONLY after they confirm, execute precisely that contract. Never build on assumptions when a question is affordable; never stall the user with more than one compact round (max ~7 numbered questions, each with a stated default if unanswered). Use at the START of ANY user request that is not already fully specified — especially: 'افهم فيديو مونتاج', 'اعمل لي', 'ابني', 'write me', 'create a', 'fix my', 'تحسين', any task where the user expects us to know their exact intention. Trigger phrases: 'اسألني الأول', 'أنا عايزك تسألني', 'اعرف التفاصيل مني', 'clarify first', 'ask me questions', 'don't assume'. Pairs with thinking-socratic (which questions are load-bearing), ambiguity-resolver (block on high ambiguity), omni-request-orchestrator (psychology pass AFTER contract is fixed), proactive-spec-expander (turn confirmed answers into a PRD)."
---

# Clarify Before Execute

The loop the user demands, verbatim: after they say what they want —
**search first, then come back and ask, then do exactly what they want.**

## The 5-Phase Loop

### Phase 0 — SEARCH FIRST (before asking anything)
The moment the request lands, do a quick informed pass so the questions are
intelligent, not generic:
- If the request references a domain/tool/topic → `websearch` / firecrawl /
  apify / skills.sh `npx skills find` for current facts, options, pitfalls
  (evidence-over-memory: do not ask from ignorance, do not answer from memory).
- If the request references THIS workspace (repo, skills, n8n, memory) →
  check the codebase / skill stack / `memory/conversation-memory.md` for
  what already exists (do not re-ask what memory answers).
- If the request references a site/brand/media → quick live look.
Keep this pass bounded: enough to ask good questions, not a research report.

### Phase 1 — COME BACK AND ASK (one compact round, max ~7 questions)
Present the questions as a numbered list. Every question is:
- **Load-bearing** (the answer changes what we build) — use thinking-socratic
  to pick only these; cut anything we can safely default.
- **Prefer concrete choices** over open fields ("A/B/C + 'your own' + 'you
  choose'" style from the interactive-gathering pattern — exclusive vs
  multi-select classification).
- **Given a stated default** for silence: "لو ما جاوبتش على ده، هفترض X".
Ask in the user's language. Start the reply with one line saying what we
searched and learned (Phase 0), so the user sees why the questions are asked.

Canonical dimensions (pick the relevant subset — never all 7 blindly):
1. **Goal/outcome** — what is the success state? ("done" means what?)
2. **Exact deliverable** — format, platform, where it lands (file? n8n? post?).
3. **Audience** — who uses/receives it (feeds omni psychology pass).
4. **Constraints** — budget/cost cap, time, tools allowed/forbidden, free-only?
5. **Preferences** — style/tone/look, existing examples to imitate.
6. **Scope edges** — explicitly out-of-scope, must-not-break things.
7. **Definition of done / verification** — how do we both know it worked?

### Phase 2 — CONFIRMATION CONTRACT
Restate in 3-5 lines: **Goal / Deliverable / Audience / Constraints / Done-when**.
Ask one yes/no: "صح؟ لو صح هبدأ". If the user says 'امشي' / 'just do it',
note the defaults taken and proceed — do not re-ask.

### Phase 3 — EXECUTE the confirmed contract
Now and only now run the real work, passing the contract into the task
pipeline (omni-request-orchestrator for audience/psychology, production
skills for the artifact). Never let later steps silently drift from the
contract — if something discovered mid-work contradicts it, stop and
re-confirm one targeted question.

### Phase 4 — VERIFY against the contract
Before delivery, check the output against the Phase-2 'done-when' line.
Report explicitly: delivered vs contract, deviations (if any) and why.

## Hard rules
- No building before Phase 2 confirmation (unless user pre-authorizes
  'just do it' — then still state the assumptions we took).
- One question round max by default; a second round only for blocking
  contradictions found mid-execution.
- Every question must carry its default → the user can answer with silence.
- Never ask about something the search/memory already answered.
- Ask in the user's language; keep the list short enough to read in seconds.

## Anti-patterns (from the interactive-gathering reference)
- Batching 20 questions; asking one-at-a-time dragging over many turns.
- Assuming answers without asking (the exact failure this skill kills).
- Using jargon the user didn't use.
- Skipping the confirmation step before generation.
- Generating content from unselected options.

## Honest limits
- Some users answer faster with freedom than with A/B/C — if the user
  writes a full free-form answer, honor it over the option list.
- If the user explicitly says 'بدون أسئلة، نفذ' — obey: default everything,
  state the assumptions, execute.