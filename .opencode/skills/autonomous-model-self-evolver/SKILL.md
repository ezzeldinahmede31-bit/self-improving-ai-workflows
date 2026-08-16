---
name: autonomous-model-self-evolver
description: "Autonomous meta-skill that MEASURES the current model against a live leader with real model calls on deterministic probes, pulls real weaknesses from the audit trail (FeedbackLoop rejections, HITL quirks), and promotes ONLY verified guard rules into machine-readable rules.json that the SecurityGate enforces at runtime. Honest loop: [measure gap -> extract real weaknesses -> trial current model against the exact regression probe -> promote only on pass]. No fabricated scores, no static weakness lists, no placebo verification, no inert docs. Use whenever the system is about to execute a task a weak model is known to fail, when a new/free model replaces the current one and its gaps must be measured, when recurring HITL rejections should become enforced rules, or when a fix must be verified with a real model before being trusted. Trigger phrases: 'self evolve', 'benchmark my model', 'compare with Claude/Kimi/Qwen', 'turn this bug into a rule', 'auto-improve', 'gap analysis', 'promote this rule'."
---

# AUTONOMOUS SELF-EVOLUTION ENGINE (honest, no theater)

## DIRECTIVE

Never claim an improvement that was not measured, and never promote a fix that
was not verified by a real model against the exact failure mode. The engine
learns only from the system's own evidence trail; when there is no live model
or no real rejection data, it says so and changes nothing.

## THE HONEST 4-STEP LOOP

```
1. MEASURE the gap  -> run current + leader on the SAME deterministic probes.
                      No leader connected => measured=False, NO gap claim.
2. EXTRACT real weaknesses -> read FeedbackLoop.rejection_summary(), HITL
                      quirks, audit DB. No evidence => empty list, not prose.
3. TRIAL the current model -> it must now pass the regression probe for the
                      exact failure mode. No live model => nothing can pass.
4. PROMOTE only on pass -> write rules.json (gate-enforced) + SKILL.md (docs).
```

## CONTRACT (each line maps to a v1 critique it fixes)

| v1 problem | v2 behavior |
|---|---|
| `competitor_matrix` fabricated | `benchmark_vs()` uses live model calls; missing leader => `measured=False` |
| static `known_weaknesses` | `WeaknessSource` reads the real audit trail; empty when nothing happened |
| sandbox test unrelated to the bug | every candidate maps to a canonical probe that rejects that exact failure mode |
| `.md` was inert | rules.json is loaded by `SecurityGate._load_promoted_rules()` and enforced at runtime |
| "never repeat mistake" unsupported | loop starts from real rejection data; no production error => no claim |

## PROTOCOL EXECUTION RULES

1. **Measurement**
   - Only live model callbacks produce scores. `gap_pct = (leader - current) * 100`
     over the SAME probe set.
   - `needs_evolution` is `False` whenever `measured=False`. Unknown gap => no escalation.

2. **Weakness extraction**
   - Sources: `FeedbackLoop.rejection_summary()` (rule/count/last_reason),
     quirks with service `hitl_feedback`, HITL audit rows.
   - `min_rejections` filters weak signals; recurring rejections rank first.

3. **Trial & verification**
   - Each candidate rule must map to a `CANONICAL_PROBES` entry
     (`guard` deny-pattern scan or `ast` parse — pure Python, deterministic).
   - The current model runs the task; the probe is applied to its output.
   - NO live model => verification impossible => **NOTHING is promoted** (reported).

4. **Promotion & enforcement**
   - `SkillRegistry.promote()` writes `auto-fix-<rule>/rules.json` with the rule,
     its probe, evidence, and timestamp.
   - `SecurityGate(rules_dir=...)` loads promoted rules; a matched `guard` adds
     a violation and risk. Probes flagged `fatal` (e.g. SSRF egress) force
     `risk >= 45` => `REJECTED_SECURITY_RISK`.
   - `SKILL.md` is generated as documentation alongside — it is never the
     mechanism of enforcement.

## HARD RULES

- `measured=False` => never escalate or promote on the basis of that benchmark.
- No live model => nothing is promoted; the round reports it.
- No canonical probe => the rule is skipped with an explicit failure reason.
- Promotion writes only `rules.json` + `SKILL.md`; it never mutates the
  orchestrator, tests, or live workflows.

## INTEGRATION

Engine: `auto_self_evolver.py`. Enforcement: `security_gate.py`
(`_load_promoted_rules` / `_apply_promoted_rules`). Wired at orchestrator
STEP 0.1 with the real `FeedbackLoop` as the weakness source; without connected
model callbacks it honestly reports an unmeasured, no-op round.

## RESEARCH ANCHORS (how this engine maps to the literature)

| Paradigm | What it contributes | Where it lives here |
|---|---|---|
| **Voyager** (NVIDIA/Stanford) — skill library with name+description retrieved for new tasks | write skill, verify in sandbox, store, auto-retrieve on same task type | `SkillRegistry.find_rules_for_task(task_text)` — deterministic token-overlap retrieval over rule name + probe description; no fake vectors |
| **DSPy** (Stanford) — compare vs SOTA, regenerate prompts + few-shot on gap | verified outputs become in-context examples, loop until parity | `demonstration` captured on every promote; `demonstrations_for_task()` feeds the next round's prompt (real regeneration, honest) |
| **Cline / Roo Code / Cursor** — developer writes a rule into project files on error | human-authored rule with immediate effect | `SkillRegistry.promote_direct_rule()` records `source: "developer"`; still HMAC-signed + permission-checked like every rule |
| **EvoAgent / Self-Evolve** — small vs strong model gap → System Directives | measured gap becomes prompt-language compensation for the weaker model | `build_system_directive(rule, probe)` derived from the canonical probe; injected into the weak model's next trial prompt |

All four are honest implementations: retrieval is keyword scoring (not
embeddings), few-shots are real prior passing outputs (not invented), directives
are deterministic prose from the probe (not free-form).
