---
name: context-enrichment
description: "Explicit-rule lexicon for implicit intents (weak-model hardening). A frontier model catches implicit intents from broad training data; a small model cannot. Compensate with a domain-specific RAG: every time HITL corrects a misread intent, store it as (implicit_pattern -> explicit_rule) and inject the matching explicit rules into the generator prompt BEFORE it starts. Use when the user's phrasing is vague ('make it safe', 'خليه آمن', 'make it reliable') and the system must translate it into concrete requirements (auth + rate limiting + input validation) rather than guess."
---

# CONTEXT ENRICHMENT PROTOCOL

## DIRECTIVE

A small model doesn't miss implicit intent because it's careless — it misses it
because it lacks the broad training context that makes the implicit obvious. The
compensation is a RAG built on YOUR domain (n8n + security) instead of general
knowledge. Each human intent-correction becomes a translation rule.

## LEXICON SHAPE

```
implicit_pattern (user's vague phrasing)
  → context (category the rule applies in, e.g. webhook)
  → explicit_rule (the executable requirements)
```

Seed examples:

| implicit | context | explicit_rule |
|---|---|---|
| آمن / secure / make it safe / خليه آمن | webhook | add auth + rate limiting + input validation |
| لا تخسر / don't lose / make it reliable | webhook | retry w/ backoff + dead-letter queue |
| بسرعة / fast / realtime | webhook | synchronous chain, no polling |
| مجانا / free / رخيص | model | free/local tier, never paid frontier for routine |

## WRITE PATH (fed from HITL)

Every time a human corrects a misread intent:

1. `record_hitl_correction(task_text, what_user_meant, context)` — stores the
   exact user phrasing → what the user actually wanted.
2. The lexicon GROWS from real corrections. Re-curated by usage count (evidence
   strength), so repeated corrections out-rank one-off seeds.

## READ PATH (fed INTO the generator)

Before generation:

1. `resolve(text, context)` — match the user's phrasing (token overlap) OR the
   context category.
2. Inject every matching explicit rule as a HARD constraint into the generator
   system-prompt, formatted as:

```
## Explicit intent rules for this task (must implement):
- (webhook) add auth (token/secret check), rate limiting and input validation.
```

## RELATION TO QUIRKS MEMORY

- `quirks_memory.py` = durable facts about REMOTE SERVICES (Telegram 4096 cap).
- This lexicon = translations of USER INTENT into executable requirements.
Complements, never replaces, quirks memory.

## INTEGRATION

Second in the pipeline (after ambiguity-resolver stops unclear tasks):

```
ambiguity-resolver (stops if unclear)
  → context-enrichment (inject known implicit context)
  → chain-integrity-checker (verify each step)
  → confidence-calibrator (decide real escalation)
```