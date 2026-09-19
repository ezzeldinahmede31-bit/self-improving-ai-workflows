---
name: systems-design-methodology
description: "Use when the /systems-design mode is active. 9-phase structured design methodology -- problem framing, system classification, constraints, candidate architectures, tradeoff analysis, risk review, refinement, migration planning, and documentation. Governs conversation flow, delegation patterns, and user validation checkpoints."
---

# System Design Methodology

Companion skill for the `/systems-design` mode. The mode gates tools; this skill governs behavior.

**For automated staging with approval gates**, use the `systems-design-cycle` recipe instead of this manual flow:
```
recipes(operation="execute", recipe_path="@systems-design:recipes/systems-design-cycle.yaml", context={"design_problem": "<description>"})
```
The recipe automates all phases with human checkpoints between stages.

## Core Rule

**You handle the CONVERSATION. Agents handle the ANALYSIS.**

You guide the user through design phases, validate understanding at each step, and delegate analytical work to `systems-design:systems-architect`. The architect does the system-level reasoning (it runs on a `reasoning`-role model with design methodology context). You present its output to the user, collect feedback, and feed that feedback into the next delegation.

## Phase Flow

Progress through these phases in order. Each phase ends with explicit user validation before moving on. You may revisit earlier phases if the user's feedback reveals gaps.

### Phase 1: Problem Framing

Gather the user's initial description, then delegate to the architect to build the system map:

```
delegate(
  agent="systems-design:systems-architect",
  instruction="ANALYZE mode. Build a system map for: [user's description].
    Produce: goals, constraints, actors, interfaces, failure modes, time horizons.
    Do NOT propose solutions -- map the problem only.",
  context_depth="recent"
)
```

Present the architect's system map to the user. Ask: **"Does this capture the problem correctly? What am I missing?"**

Do NOT proceed until the user validates the problem framing. If they correct the map, re-delegate with the corrections.

**If this modifies an existing system**, apply the Comprehending Existing lens before generating the map:
- Why was the existing system designed this way? What tradeoffs did the original designer make?
- What does the current design choice tell us about the constraints the designer was working under?
- What problems does the current design solve that aren't obvious at first glance?

Include this context in the architect delegation so candidates respect existing design intent.

### Phase 2: Classify the System

**This phase is mandatory. Do not skip it. Do not proceed to candidate architectures without completing it.**

Based on the validated system map from Phase 1, classify the system being designed. Produce a brief taxonomy:

**System types** -- which of these apply? List ALL that match, not just the primary one:

| Type | Skill | Applies when... |
|------|-------|-----------------| 
| Web service / API | `system-type-web-service` | HTTP endpoints, REST/GraphQL, request-response |
| Event-driven | `system-type-event-driven` | Message queues, event logs, pub/sub, hooks, reactive patterns |
| Data pipeline | `system-type-data-pipeline` | Batch/streaming processing, ETL, DAG scheduling |
| Workflow orchestration | `system-type-workflow-orchestration` | Multi-step processes, sagas, durable execution |
| CLI tool | `system-type-cli-tool` | Command-line interface, subcommands, plugin architecture |
| Real-time | `system-type-real-time` | WebSockets, persistent connections, state sync |
| Multi-tenant SaaS | `system-type-multi-tenant-saas` | Tenant isolation, shared infrastructure, billing |
| ML serving | `system-type-ml-serving` | Model serving, feature stores, inference pipelines |
| Distributed system | `system-type-distributed` | Consensus, replication, partitioning, multi-node coordination |
| Enterprise integration | `system-type-enterprise-integration` | Legacy modernization, API gateways, data integration |
| Edge / offline-first | `system-type-edge-offline` | Offline operation, sync protocols, constrained resources |
| Single-page app | `system-type-spa` | Client-side routing, state management, rendering strategies |
| Peer-to-peer | `system-type-peer-to-peer` | P2P topologies, NAT traversal, decentralized coordination |
| Azure-hosted | `system-type-azure` | Azure compute, identity, networking, managed services |

**Design philosophies** -- which does the system claim or embody?

| Philosophy | Skill | Applies when... |
|------------|-------|-----------------| 
| Linux/Unix | `design-philosophy-linux` | Mechanism vs policy, composability, small sharp tools |
| Domain-driven | `design-philosophy-domain-driven` | Bounded contexts, ubiquitous language, aggregates |
| Object-oriented | `design-philosophy-object-oriented` | SOLID, composition over inheritance, protocols/traits |

**After classifying, immediately load ALL matching skills:**
```
load_skill(skill_name="system-type-event-driven")
load_skill(skill_name="system-type-cli-tool")
load_skill(skill_name="design-philosophy-linux")
# ... every skill that matches
```

Present the classification to the user: **"Based on the system map, I've classified this as [types]. I've loaded domain skills for [list]. Does this match? Anything to add?"**

**Why this matters:** Domain skills contain canonical patterns, failure modes, and anti-patterns for each system type. Loading them before generating candidates ensures the architect has the right evaluative frame -- candidates that violate domain-specific patterns will be caught immediately rather than discovered in risk review.

### Phase 3: Constraints and Assumptions

Surface everything assumed but not stated:

- Scale expectations (users, requests/sec, data volume)
- Team capabilities and size
- Budget and timeline constraints
- Existing systems that must be integrated
- Regulatory or compliance requirements

Present as a numbered list of explicit assumptions. Ask: **"Which of these are wrong? What constraints am I missing?"**

### Phase 4: Candidate Architectures

Delegate to the architect to generate candidates using the validated system map, classification, and constraints:

```
delegate(
  agent="systems-design:systems-architect",
  instruction="DESIGN mode. Using this validated system map and constraints:
    [system map from Phase 1, with user corrections]
    [system classification from Phase 2]
    [constraints and assumptions from Phase 3, with user corrections]
    Generate 3 candidate architectures:
    1. Simplest viable -- minimum design meeting core requirements
    2. Most scalable -- optimized for growth
    3. Most robust -- optimized for reliability and operational simplicity
    For each: components, boundaries, data flows, technology choices, what it optimizes for.
    Apply domain patterns from the system classification -- candidates should respect [system type] conventions.",
  context_depth="recent",
  context_scope="agents"
)
```

Present the architect's candidates to the user. Ask: **"Which direction feels right? Should we explore any of these deeper?"**

Load the `architecture-primitives` skill if pattern selection is unclear.

**Apply these review questions to each candidate before presenting:**
- Isn't there a simpler way to do this? What if we just...?
- Are there existing CS concepts this is an instance of? Are we reinventing something that already has a name?
- Are we mixing two concerns here? Aren't these actually separate responsibilities?
- Does this diverge from ecosystem conventions? Is there an existing library that replaces much of this?
- How many concepts must a developer hold in their head to use this correctly?

### Phase 5: Tradeoff Analysis

Delegate to the architect to evaluate the user's preferred candidates against the 8-dimension tradeoff frame:

```
delegate(
  agent="systems-design:systems-architect",
  instruction="DESIGN mode -- tradeoff analysis only.
    Evaluate these candidates against the 8-dimension tradeoff frame:
    [candidates the user wants compared]
    User's preferred direction: [if stated]
    Produce the filled comparison matrix.",
  context_depth="recent",
  context_scope="agents"
)
```

Present the architect's comparison matrix to the user. Ask: **"Do these ratings match your understanding? Are any dimensions more important than I've weighted?"**

Load the `tradeoff-analysis` skill for deeper methodology if the tradeoffs are contested or unclear.

### Phase 6: Risks and Failure Modes

For the leading candidate, identify:
- Critical failure modes and blast radius
- Single points of failure
- Scaling bottlenecks
- Operational complexity
- Security surface
- Developer experience impact (concept count, naming clarity, onboarding cost)

If the design warrants deep adversarial review, delegate to `systems-design:systems-design-critic` or suggest `/adversarial-review`.

**Pass the system classification to the critic** so it can apply domain-specific failure modes.

Present risks ranked by severity. Ask: **"Which of these risks are acceptable? Which need mitigation in the design?"**

### Phase 7: Design Refinement

Delegate to the architect to incorporate the user's risk feedback:

```
delegate(
  agent="systems-design:systems-architect",
  instruction="DESIGN mode -- refinement pass.
    Current architecture: [leading candidate from Phase 4/5]
    User feedback from risk review:
    - Unacceptable risks requiring mitigation: [list]
    - Accepted limitations: [list]
    - Priority adjustments: [list]
    Produce a refined architecture incorporating these changes.",
  context_depth="recent",
  context_scope="agents"
)
```

Present the architect's refined design to the user. Ask: **"Is this the design you want to proceed with?"**

**Encourage hybrid refinement:** If the user liked aspects of multiple candidates, actively suggest combining them: "Should we take the simplicity of candidate A's data model with the resilience approach from candidate C?" Revision and recombination are expected, not exceptional.

**Check design integrity:** Before finalizing, verify the refined design is consistent with prior decisions:
- Does this proposal contradict any design decisions already validated in earlier phases?
- Are we changing the responsibility of any component established in the system map?
- Does this introduce a second way to do something the system already does?

### Phase 8: Migration and Success Metrics

If this replaces or modifies an existing system:
- Migration strategy (incremental vs big-bang)
- Rollback plan
- Success metrics and monitoring

If greenfield:
- Phased rollout plan
- Success metrics and thresholds
- What signals indicate the design is failing

### Phase 9: Document the Design

When the user approves the design, delegate to `systems-design:systems-design-writer`:

```
delegate(
  agent="systems-design:systems-design-writer",
  instruction="Write the design document for [topic]. Include: [summary of all validated sections]",
  context_depth="all",
  context_scope="agents"
)
```

Pass ALL validated content from the conversation. The writer structures it -- it does not make decisions.

## Skills Available Per Phase

| Skill | When to load |
|-------|-------------|
| `system-type-*` (all matching) | Phase 2 -- mandatory, load all that match the classification |
| `design-philosophy-*` (all matching) | Phase 2 -- mandatory, load all that match |
| `architecture-primitives` | Phase 4 -- selecting patterns for candidates |
| `tradeoff-analysis` | Phase 5 -- detailed tradeoff methodology |
| `adversarial-review` | Phase 6 -- parallel 6-perspective stress test |

## Handling Follow-Up Questions After Agent Work

When agents have already completed analysis and the user asks a follow-up question, do NOT re-delegate from scratch. Prior agent work is expensive -- treat it as an asset, not a disposable draft.

**Decision rule:**

1. **Can I answer from prior agent findings?** If the architect or critic already analyzed this, synthesize their findings into a response. This is conversation work, not analysis work -- it belongs to you.
2. **Does the follow-up require genuinely new analysis?** New scope, new data, or a different analytical frame that prior work didn't cover. Only then re-delegate.
3. **If re-delegating, build on prior work.** Resume the existing agent session (`session_id`) when possible. If spawning fresh, include a summary of prior findings in the instruction so the agent extends rather than repeats.

**The test:** If the new delegation instruction overlaps >50% with a prior one, you are re-doing work. Synthesize instead.

**Anti-pattern:** User asks a high-level question about architectural decisions. You feel uncertain, so you re-spawn the architect from scratch. The architect produces findings that overlap heavily with its first pass. Hours wasted.

**Correct pattern:** User asks about architectural decisions. You check: the architect already analyzed boundaries, coupling, and failure modes. You synthesize those findings into an answer. If the user's question touches something the architect didn't cover (e.g., organizational fit), you delegate only that specific gap.

**The "analysis vs conversation" heuristic:** If answering requires reasoning about tradeoffs, failure modes, or design alternatives using information you don't have, it is ANALYSIS -- delegate it. If answering requires presenting, reframing, or connecting findings that agents already produced, it is CONVERSATION -- do it yourself. When in doubt, check whether prior agent results already contain the answer before delegating.

## The Catalytic Question

At the end of every design, ask:

> **"What would have to be true for this to be the wrong choice?"**

This surfaces hidden assumptions and identifies the monitoring signals that tell you the design is failing.
