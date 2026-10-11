---
name: multi-model-pipeline
description: "Runs a project through three model families on this device: ChatGPT plans, Claude refines, Kimi refines — quota-aware with token-saving wired in. Use when the user says 'خلي شات جيبيتي يخطط', 'claude و kimi يعدلوا', 'multi-model project', 'plan with gpt refine with claude and kimi', 'وزع الشغل على الموديلات', or asks to split planning/review across GPT/Claude/Kimi."
---

# Multi-Model Pipeline (device-native, quota-aware)

All three families are LIVE on this device via the OpenRouter credential in
opencode `auth.json` (verified 2026-10-11, tiny OK-probe each). No new keys,
no new CLIs, no browser hacks needed. `claude` CLI exists but is NOT logged
in — do not depend on it.

## Roles (defaults; cheapest capable wins)

| Step | Model | Why |
|------|-------|-----|
| 1. PLAN | `openai/gpt-4o-mini` | Cheap, strong planner; short structured plan only |
| 2. REFINE-A | `anthropic/claude-haiku-4.5` | Cheapest Claude; critique + tighten (escalate to Sonnet only on explicit ask) |
| 3. REFINE-B | `moonshotai/kimi-k2-0905` | Long-context reviewer; second pass, conflicts with A flagged |

Call pattern (key from `auth.json openrouter.key`, never print it):
`POST https://openrouter.ai/api/v1/chat/completions`
`{"model": "<id>", "messages": [...], "max_tokens": <cap>}`.

## Quota rules (quotas die fast — obey all six)

1. **Cap outputs**: plan ≤800 tokens, each refine ≤600 tokens (`max_tokens` enforced, not requested).
2. **Compress inputs first**: run the brief through `text-optimizer` (20-40% off) before step 1; deltas only between steps (never resend full plan — send plan + diff instructions).
3. **Cheap-first**: Haiku/mini/K2 defaults; dearer models only with explicit user approval + stated token budget.
4. **One-pass each**: no model repeats a step unless its output failed verification; loops max 2 with shrinking caps.
5. **Cache**: identical briefs reuse prior outputs (check turn history first).
6. **Report spend**: every pipeline answer ends with per-step input/output token counts (from API `usage`) + running total.

## Pipeline steps

1. **Brief** (you): 5-10 line task brief (goal, constraints, done-criteria). Optimize it (`text-optimizer`), record token count.
2. **Plan** (GPT): "Produce a numbered build plan for: <brief>. Max 15 steps. No prose." Save plan.
3. **Refine-A** (Claude): "Critique this plan, list flaws with severity, output corrected plan. <plan>". Save.
4. **Refine-B** (Kimi): "Review plan-A vs plan-B, merge best of both, flag unresolved conflicts. <both>". Save merged plan.
5. **Verify**: conflicts resolved? steps ≤15? caps respected? If no → single targeted re-ask (one model, diff-only). If yes → execute merged plan with normal skills.
6. **Report**: merged plan + per-step usage + total + which model said what (one line each).

## Verification

- [ ] Each step used its assigned model (IDs in turn evidence).
- [ ] Caps enforced (`max_tokens` set, usage quoted).
- [ ] Merged plan executed or handed over; spend table present.
- [ ] No credential printed anywhere (keys stay in `auth.json`).

## Pairs with

- `text-optimizer` — input compression before every step.
- `token-economics-cost-control-v2` — budget ceilings around the pipeline.
- `context-budget-governor` / `litellm-tier-router` — overflow + failover.
- `llm-council` — same-model debate alternative when quota is zero.
