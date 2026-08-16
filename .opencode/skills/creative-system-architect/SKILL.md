---
name: creative-system-architect
description: "Forces the model to generate 3 distinct architectural options (Tree-of-Thought) and apply cross-domain principles to outperform conventional linear solutions. Use whenever designing a new n8n workflow, automation, or system architecture."
---

# CREATIVE SYSTEM ARCHITECT & UNORTHODOX DESIGNER

## DIRECTIVE
Never jump straight into writing code or basic linear workflows (Trigger ->
Action). You must think like a Principal Systems Architect, synthesizing
concepts from Distributed Systems, Behavioral Psychology, and Async
Event-Driven Topologies.

## 3-STEP BRAINSTORMING PROCESS (Tree-of-Thought)
Before outputting any n8n JSON or script, you MUST outline 3 distinct
architectural approaches:

### Option A: The Streamlined Approach
- The clean, simple, and direct implementation.
- Minimal moving parts; best when requirements are simple and cost is primary.

### Option B: The Asynchronous Event-Driven Powerhouse
- High-throughput topology utilizing decoupled sub-workflows, state persistence,
  queues, and zero-latency response patterns.
- Best when isolated failure domains and independent scaling matter.

### Option C: The Unorthodox / Multi-Agent Hybrid (THE INNOVATION)
- Radical, non-linear architecture integrating dynamic self-healing loops,
  behavioral routing, fallback circuit-breakers, and adaptive agent decision nodes.
- Pursued when the problem rewards non-obvious, intelligence-heavy designs.

After presenting the three options, STATE which one you recommend and why, with
explicit trade-offs vs. the other two (cost, latency, resilience, complexity,
maintainability).

## CROSS-DOMAIN DESIGN RULES

1. **Self-Healing Topologies:** Design workflows that recover from downstream API
   failures using dead-letter sub-workflows and dynamic payload restructuring.
   Never let a single downstream outage take down the whole flow.
2. **Behavioral Logic Injection:** Integrate smart micro-triggers, decay logic,
   and contextual scoring based on user interactions (engagement, recency,
   retry fatigue) rather than static if/else.
3. **Extreme Optimization:** Use Code Nodes to batch inputs (`$input.all()`) and
   perform local transformations before triggering external services, saving up
   to 80% on API costs. Prefer local processing over per-item remote calls.

## ANTI-PATTERNS TO AVOID
- Linear Trigger -> Collect -> Send chains when the task could be event-driven.
- State held in memory only (use Supabase/Redis/file DB for anything long-lived).
- Single point of failure: no retry, no dead-letter, no fallback path.