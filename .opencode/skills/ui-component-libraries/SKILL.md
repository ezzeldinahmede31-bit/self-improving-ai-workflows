---
name: ui-component-libraries
version: "1.0.0"
description: "Build web UI from ready-made design resources: 21st.dev sections, ReactBits animations, DESIGN.md brand systems (getdesign.md), and Claude Design systems. Use when the user says صمم واجهة, landing page, design system, animations, or wants Apple/Airbnb-level UI without designing from scratch."
---

# ui-component-libraries

The 5-level design stack from the Hussein R. Atwi reel, as installable resources — stop making Claude design from zero; give it proven systems and components to compose.

## Level 1+2 — Claude Design (official Anthropic)

- **What:** design workspace at `claude.ai/design` + persistent **design systems** (colors, type, components) on Pro/Max/Team plans; in Claude Code run `/design-sync` to read tokens/components from an existing React codebase.
- **Use:** visual exploration + design-system definition first; production code later in Claude Code.
- **Docs:** `support.claude.com — set up your design system in Claude Design`
- **This project:** pairs with `impeccable`, `apple-ui-designer`, `frontend-design` skills for taste + critique.

## Level 3 — DESIGN.md brand systems ("Revero Styles" concept)

- **What:** single-file brand visual languages (tokens + rules + rationale) that design agents act on. Sources:
  - `https://getdesign.md/` — 68 ready DESIGN.md inspirations (from VoltAgent/awesome-claude-design)
  - `VoltAgent/awesome-claude-design` (GitHub) — index of the 68
  - Awesome Design MD — 57 brands as plain markdown (30-second install)
- **Use:** fetch one matching DESIGN.md → attach as reference when asking the agent for UI; or drop into Claude Design to scaffold a full system in one shot.

## Level 4 — 21st.dev (verified live: HTTP 200)

- **What:** library of ready-made website sections/components that Claude assembles instead of designing from scratch.
- **Use:** browse `https://21st.dev`, pick sections, have the agent integrate + restyle to your tokens.

## Level 5 — ReactBits (verified: exists, redirects to current domain)

- **What:** 200+ copy-paste animated React/Tailwind components (no install — paste into your codebase).
- **Use:** `https://reactbits.com` → pick animation → agent wires it into your design with your tokens.

## Workflow (the reel's 5 levels as one pipeline)

1. Define brand tokens in **Claude Design** (Level 1)
2. Scaffold app/site from the system in Claude Code (Level 2)
3. Pull a matching **DESIGN.md** for aesthetic direction (Level 3)
4. Compose pages from **21st.dev** sections (Level 4)
5. Sprinkle **ReactBits** motion (Level 5)

Lock tokens first (colors, type, spacing, radius) — reference screenshots beat text prompts; export/store the system every session (no cross-session memory).

## Pairs with

| Skill | Why |
|-------|-----|
| `impeccable` | Taste gate: is the composed UI actually good or generic AI slop |
| `the-agency-agents` | `ui-designer`, `ux-architect` personas to direct the composition |
| `frontend-design` | Direction + typography decisions |
| `agent-reach` | Research competitor UIs (screenshots, trends) before composing |

## Frontmatter

```json
{
  "name": "ui-component-libraries",
  "version": "1.0.0",
  "description": "Web UI from ready-made resources: 21st.dev, ReactBits, DESIGN.md brand systems, Claude Design",
  "license": "mixed (resource licenses vary)",
  "tags": ["ui", "design-system", "components", "animations", "landing-page", "21st-dev", "reactbits", "design-md"],
  "triggers": ["صمم واجهة", "landing page", "design system", "animations", "21st.dev", "reactbits", "design inspiration", "Apple-level UI"]
}
```

---

*Sources: Hussein R. Atwi FB reel (transcribed via Whisper) → verified live: 21st.dev (200), reactbits.com (exists), getdesign.md/VoltAgent (68 DESIGN.md), Claude Design official docs*
