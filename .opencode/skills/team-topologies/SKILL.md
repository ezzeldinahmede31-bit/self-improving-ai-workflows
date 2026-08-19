---
name: team-topologies
description: Applies Skelton and Pais' Team Topologies to shape teams and the software around them: Conway's Law makes organization the primary architecture constraint, so choose four team types (stream-aligned, enabling, complicated-subsystem, platform) and three interaction modes (collaboration, X-as-a-Service, facilitation). Manages cognitive load so teams can own what they run. Use when the user says 'design our team structure', 'what team structure fits us', or 'why does our org mirror bad software'.
---
# team-topologies

Skelton and Pais argue that fast software delivery follows from deliberate team design. The team is the fundamental unit of delivery, and the interfaces the teams use become the interfaces the software exposes. Use this skill to shape teams, their boundaries, and the interactions that let them move quickly.

## Core principles
- Conway's Law is real: software mirrors the communication structure of the teams that build it, so design the teams to get the architecture you want.
- The stream-aligned team is the default: one team owns a slice of value end to end.
- Cognitive load is the budget: a team can only own a system it can hold in its head, so add support teams instead of overloading.
- Team APIs are contracts: how teams interact (collaborate, serve, or enable) determines how their software interacts.
- Small, long-lived teams with stable membership outperform big or frequently reorganized teams.
- The platform team exists to reduce the cognitive load of the stream-aligned teams.

## Key patterns
- Four team types: stream-aligned (owns the value stream), enabling (helps others adopt practices), complicated-subsystem (owns deep specialist work), platform (provides self-service foundations).
- Three interaction modes: collaboration (work closely for a time), X-as-a-Service (consume a product), facilitation (enable others to do it themselves).
- The inverse Conway maneuver: restructure teams to match the target architecture before building it.
- A self-service platform with paved roads so stream teams pick the supported path instead of inventing their own.
- Interface ownership made explicit: every boundary has a named owner and a documented contract.
- Awareness of team boundaries when designing software boundaries, so the two stay aligned.

## Applying this to n8n/automation/code
- Group workflows into stream-aligned domains (marketing, support, data) with clear ownership per domain.
- Build a platform layer of shared subworkflows and helpers that domain teams consume as a service.
- Make the interface of shared subworkflows explicit and versioned, exactly like a team API.
- Use enabling interactions to spread automation skills across teams instead of centralizing all expertise.
- Match workflow architecture to team ownership so nobody maintains a system their team does not understand.

## Hard rules
- Never give a team more systems than its members can hold in their heads; reduce scope or add support.
- Never let one team own a boundary another team depends on without a documented contract.
- Never force collaboration on teams that should consume a product instead; choose the mode deliberately.
- Never reorganize frequently; stable teams and stable boundaries beat constant reshuffling.

## Pairs with
microservices-boundary-design, monolith-to-microservices, agent-arch-system-design, high-output-management, value-stream-mapping
