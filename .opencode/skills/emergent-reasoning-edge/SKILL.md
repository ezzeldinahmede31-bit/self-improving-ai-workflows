---
name: emergent-reasoning-edge
description: "Beats a frontier model's parametric instinct at open-ended creativity and emergent reasoning by adding two things it cannot have: (1) LIVE world evidence — web/deep research injects facts, papers, precedents from TODAY (Claude's 'brilliant instinct' is frozen at its training cutoff; ours re-grounds in the present moment via websearch/firecrawl/apify and cites sources), and (2) MECHANICAL falsification — every creative take is attacked by structured adversarial rounds (red-team, worst-idea, pre-mortem, council vote) and only survivors ship. Protocol: reframe the problem in N diverse framings (lateral pack: inversion/scamper/analogy/random-stimulus) → divergent generation of options → EVOLUTIONARY selection via falsification rounds → cross-domain analogy pulled from live search (not memory) → synthesis with confidence + citations → optional iteration log so ideas measurably improve across sessions. Use when the task is 'a new idea', 'think differently', 'novel approach', 'what would change everything', 'creative direction', 'brainstorm something never done', or when a first-pass answer would be too conventional to be valuable. Trigger phrases: 'فكرة جديدة', 'novel idea', 'think outside the box', 'creative direction', 'something nobody has tried', 'emergent thinking'. Pairs with: lateral-thinking pack, cc-thinking-skills pack, llm-council, multi-agent-consensus-engine, parallel-web-search, adversarial-self-falsifier."
---

# Emergent-Reasoning Edge

The frontier model's edge is a strong PARAMETRIC instinct — a fast,
internally-trained reflex. Our edge is a SLOW SYSTEM with two components a
strong instinct cannot have: **live evidence** and **mechanical
falsification**. Reflexes guess fast; systems prove slow. For open-ended
creativity we deliberately go slow.

## Protocol (6 gates)

### Gate 1 — Reframe the problem N ways
The prompt as given is one frame; creativity starts by breaking it.
Deliberately generate 3+ FRAMES (not answers) using the lateral pack:
- Inversion ("what if the problem is the answer?"),
- Analogy ("what does something completely different do here?"),
- Random stimulus (map a random word/object onto the problem),
- Scamper (substitute/combine/adapt/modify/put-to-another-use/eliminate/reverse).
State each frame in one line. The frame set IS the creative payload.

### Gate 2 — Divergent generation (options, not judgments)
Produce 4–6 DIFFERENT candidate solutions — different mechanisms, not
variants of one idea. Include one intentionally 'worst idea' (worst-idea
spark: bad ideas unlock adjacent good ones) and one extreme (provo).
No evaluation during generation.

### Gate 3 — LIVE evidence injection (the edge Claude cannot have)
For each surviving candidate, search the real world TODAY:
- `websearch` / `parallel-web-search` / `deep-research` — what has been
  tried (2025/2026), what failed publicly, what changed recently.
- `firecrawl`/`apify` MCP for primary sources (papers, docs, posts).
- Cross-domain analog: find a working mechanism in a DIFFERENT field
  (biology/games/logistics/pricing...) and cite it.
Rule: any factual claim about 'the world' (markets, tech, precedents) must
carry a source from THIS search — never memory (evidence-over-memory).

### Gate 4 — Mechanical falsification rounds (evolution)
Each candidate now runs attack rounds — kill the weak before synthesis:
1. **Red-team round** (thinking-red-team / adversarial-self-falsifier):
   list the top ways this fails in reality.
2. **Worst-idea round**: assume it works — what terrible side effects?
3. **Pre-mortem round** (thinking-pre-mortem): 12 months later, why did it
   die? Fix or kill.
4. **Council vote** (llm-council): 5 advisors argue, chairman picks ONE
   candidate + one next step.
Survivors: maximum 2. Killed candidates get one line in the log (why).

### Gate 5 — Synthesis with confidence
Deliver: the winning candidate + its frame + live-evidence citations +
explicit remaining risks (post-falsification). Confidence is calibrated by
how many attack rounds it survived, never by how clever it feels.

### Gate 6 — Iteration log (measurable improvement)
Append to `memory/emergent-idea-log.md`: date, problem, frames, candidates,
winner, what falsification killed, lessons learned. Before the next idea in
the same domain, READ the log and let past kill-reasons shape the new
generation (this is how skill compounds where a reflex cannot).

## Why this beats a frozen instinct

| Situation | Parametric instinct (Claude) | This system |
|---|---|---|
| Novel idea, no precedent | confident guess from cutoff-era data | live search + falsified survivor |
| Domain with changed facts | stale defaults | current evidence, cited |
| Creative spark | one brilliant-ish pass | 6 frames × N candidates × attack rounds |
| Second idea in same domain | starts from scratch | session log compounds kills |

## Cost Optimization (implemented)

The pipeline now includes a mandatory caching layer (`scripts/emergent_cache.py`):

1. **Search caching** — query results cached 24h (SHA256 keyed)
2. **Frame caching** — problem frames cached per session
3. **Candidate caching** — divergent candidates cached per frame set
4. **Analogy caching** — cross-domain analogies cached per candidate/domain
5. **Falsification caching** — attack round results cached per candidate/round
6. **Token budget** — 50k tokens/session hard cap, 8k max per invocation
7. **Early exit** — confidence ≥ 0.85 skips remaining gates
8. **Council vote disabled by default** — major cost saver (enable via flag)
9. **Reduced candidates** — 4 instead of 6
10. **Max 2 sources per candidate** — limits web search cost

Pipeline config: `scripts/emergent_cache.py` → `create_optimized_emergent_pipeline()`

## Honest limits

- Slower and more token-hungry than instinct — use only when conventional
  first-pass quality is NOT enough (the cost is real).
- Falsification reduces error but can also kill weird brilliance; if the
  council kills everything, deliver the strongest loser with its risks
  clearly labeled instead of nothing.
- Live search quality bounds evidence quality — cite, but also state when
  evidence is thin.
- Cache hits reduce cost but may serve stale evidence — TTL 24h mitigates.