---
name: systems-design-review-methodology
description: "Use when the /systems-design-review mode is active. 7-step design review methodology -- understand the design, classify the system, evaluate against codebase, adversarial analysis, tradeoff validation, synthesis, and action items. Governs conversation flow, delegation patterns, and user validation checkpoints."
---

# Design Review Methodology

Companion skill for the `/systems-design-review` mode. The mode gates tools; this skill governs behavior.

**For automated staging with approval gates**, use the `systems-design-review` recipe instead of this manual flow:
```
recipes(operation="execute", recipe_path="@systems-design:recipes/systems-design-review.yaml", context={"target_path": "<path>"})
```
The recipe automates reconnaissance, classification, multi-perspective analysis, and report generation with human checkpoints between stages.

## Core Rule

**You handle the CONVERSATION. Agents handle the ANALYSIS.**

You guide the user through the review, synthesize findings, and facilitate decisions. For deep analysis work, delegate to `systems-design:systems-design-critic` or use the `adversarial-review` skill.

## Step Flow

### Step 1: Understand the Design

Before any critique, reconstruct the designer's reasoning:

1. Read the design document or referenced files thoroughly.
2. Identify the stated goals, constraints, and tradeoffs.
3. If a codebase exists, survey the relevant parts.
4. Note what the design explicitly addresses and what it is silent on.

**Apply the Comprehending Existing lens:**
- Why was this designed this way? What tradeoffs did the original designer make?
- What does the choice of this approach over alternatives tell us about the constraints the designer was working under?
- What is the mental model? Is it human-facing or system-facing?
- What problems does the current design solve that aren't obvious at first glance?

Understanding original intent prevents reviews that recommend "fixing" things the designer already considered and deliberately chose.

Ask: **"Is this the complete design, or is there additional context I should know about?"**

### Step 2: Classify the System

**This step is mandatory. Do not skip it. Do not proceed to analysis without completing it.**

Based on what you learned in Step 1, classify the system under review. Produce a brief taxonomy:

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

Present the classification to the user: **"I've classified this system as [types]. I've loaded domain skills for [list]. Does this classification match your understanding? Anything I should add?"**

**Why this matters:** Domain skills contain failure modes, anti-patterns, and evaluation criteria specific to each system type. Without them, the review produces generic findings. With them, findings are grounded in domain-specific patterns -- "this violates event-driven reliability patterns" rather than "this might have a timeout issue."

### Step 3: Evaluate Against the Codebase

If reviewing an existing system or a design that modifies one:
- Use `read_file`, `grep`, and `LSP` to examine the actual code
- Compare the design's claims against reality
- Identify gaps between the design document and the implementation

**Implementation viability check:** If the design proposes changes to an existing system, trace the impact exhaustively:
- Use LSP `findReferences` and `incomingCalls` to find every usage of components being changed
- For each usage, validate the new design can replace the old seamlessly
- Flag any callsite where the replacement is non-trivial or ambiguous

This is not optional exploration -- it is the mechanism that prevents "it worked in theory but broke 12 callsites" surprises.

### Step 4: Adversarial Analysis

Delegate the deep adversarial review rather than doing it inline:

**Option A -- Delegate to the systems-design-critic agent:**
```
delegate(
  agent="systems-design:systems-design-critic",
  instruction="Review this design: [design content or file path]. System context: [relevant codebase findings from Step 3]. System classification: [types from Step 2]",
  context_depth="recent",
  context_scope="agents"
)
```

**Option B -- Use the adversarial-review skill (spawns 6 parallel agents):**
```
load_skill(skill_name="adversarial-review")
```

Choose Option A when you have accumulated codebase context to pass along. Choose Option B for a quick parallel review when the design is self-contained.

**Pass the system classification to the agent.** The critic should know what type of system it is reviewing so it can apply domain-specific failure modes rather than generic concerns.

### Step 5: Tradeoff Validation

After the adversarial analysis returns, load the tradeoff-analysis skill if the review reveals unclear tradeoffs:
```
load_skill(skill_name="tradeoff-analysis")
```

Verify:
- Are the stated tradeoffs actually what the design achieves?
- Are there unstated tradeoffs the designers may not have recognized?
- Does the design optimize for what the team actually needs?

**Apply the Simplicity and DX lenses:**
- Isn't there a simpler way to accomplish what this design does? What concept have we uncovered that we didn't know before?
- Are we mixing two concerns here? Aren't these actually separate responsibilities?
- How many concepts must a developer hold in their head to use this correctly? Is the naming consistent and clear?
- Does this diverge from ecosystem conventions? If so, is the divergence justified?

### Step 6: Synthesize and Recommend

Present findings to the user.

**Before presenting, categorize each finding:**
- **Architectural** -- boundaries, data flow, failure modes, coupling, scalability, consistency model, state ownership. These belong in a systems-design review.
- **Implementation** -- code quality, specific function issues, API ergonomics, type safety, naming. These are useful but secondary.

If more than 30% of findings are implementation-level, you have drifted from the systems-design scope. Reframe implementation findings in architectural terms or separate them into a distinct section.

**Check design integrity before finalizing:**
- Is this design consistent with previous design decisions in the system? If not, is the inconsistency explicitly reconciled?
- Who owns this component? Does it really belong here, or are we changing the responsibility of something established?
- Does this introduce a second way to do something the system already does?

**Assessment Summary:**
- Overall health: [strong / has concerns / needs significant revision]
- Critical risks: [list]
- Tradeoff alignment: [does the design achieve what it claims?]

**Recommendation:** One of:
- **Proceed** -- risks are acceptable, design is sound
- **Proceed with modifications** -- [specific changes needed]
- **Reconsider** -- [fundamental issue that requires rethinking]

Ask: **"Do these findings match your intuition? Are there aspects of the design I should look at more closely?"**

### Step 7: Capture Action Items

If the user wants to proceed with modifications, produce a clear action list:
1. What to change (specific, not vague)
2. Why (linked to a specific risk or finding)
3. Priority (must-do vs should-do vs nice-to-do)

## Handling Follow-Up Questions After Agent Work

When agents have already completed analysis and the user asks a follow-up question, do NOT re-delegate from scratch. Prior agent work is expensive -- treat it as an asset, not a disposable draft.

**Decision rule:**

1. **Can I answer from prior agent findings?** If the architect or critic already analyzed this system, synthesize their findings into a response. This is conversation work, not analysis work -- it belongs to you.
2. **Does the follow-up require genuinely new analysis?** New scope, new data, or a different analytical frame that prior work didn't cover. Only then re-delegate.
3. **If re-delegating, build on prior work.** Resume the existing agent session (`session_id`) when possible. If spawning fresh, include a summary of prior findings in the instruction so the agent extends rather than repeats.

**The test:** If the new delegation instruction overlaps >50% with a prior one, you are re-doing work. Synthesize instead.

**Anti-pattern:** User asks about higher-level architectural decisions. You feel uncertain about your own synthesis, so you re-spawn the architect and critic from scratch. Both agents produce findings that overlap heavily with their first pass. Hours of computation wasted, and the user watches agents return similar results twice.

**Correct pattern:** User asks about architectural decisions. You check: the architect already assessed boundaries, coupling, and failure modes; the critic already reviewed from 6 perspectives. You synthesize those findings into an answer focused on the user's specific question. If the question touches something genuinely uncovered (e.g., a specific subsystem the prior analysis didn't examine), you delegate only that gap -- and reference prior findings so the agent builds on them.

**The "analysis vs conversation" heuristic:** If answering requires reasoning about tradeoffs, failure modes, or design alternatives using information you don't have, it is ANALYSIS -- delegate it. If answering requires presenting, reframing, or connecting findings that agents already produced, it is CONVERSATION -- do it yourself. When in doubt, check whether prior agent results already contain the answer before delegating.
