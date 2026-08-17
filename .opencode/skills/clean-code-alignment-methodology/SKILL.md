---
name: clean-code-alignment-methodology
description: "Mandatory methodology for ALL new skills: ensures Clean Code principles are embedded from day 1. Provides the checklist that every skill MUST satisfy before registration. Pairs with: build-gates-pipeline, router_register.py, skills_docs_generator."
---
# Clean Code Alignment Methodology

## Prerequisite: Every new skill MUST satisfy this checklist before it can be registered in the router or delivered to the user.

### 1. Skill Description Must Include "Clean Code Alignment" Section
The skill's `SKILL.md` must have a non-empty "Clean Code alignment" line in the description (line 3, after the dashes block), stating which Clean Code principles the skill enforces or embod.

**Required format**: `Clean Code alignment: This skill enforces "..."` — at minimum, must reference 3 of the 9 Clean Code principles listed below.

### 2. Mandatory Clean Code Principles per Skill
Each skill must enforce at least 3 of the following 9 Clean Code principles:

| # | Principle | What it means for the skill |
|---|-----------|----------------------------|
| 1 | **Meaningful Names** | Names (variables, functions, nodes, parameters) must be intention-revealing, not cryptic or single-letter (except loop counters). |
| 2 | **Small Functions/Nodes** | Each function or node should do one thing and be kept under 20 lines / minimal parameters. |
| 3 | **Single Responsibility** | The skill/unit must perform exactly one responsibility; no piling multiple concerns into. |
| 4 | **No Duplication** | Avoid reinventing the same pattern; use existing schemas, templates, or reference designs. |
| 5 | **Command-Query Separation** | Separate data-access expressions from transformation logic; don't mix `.get()` with `.modify()` in the same node/expression. |
| 6 | **Law of Demeter** | Limit transitive navigation of objects/dependencies; avoid chaining ≥ 3 method/expression calls. |
| 7 | **Error Handling Best** | Use exceptions over return codes; provide context; don't return null or pass null. |
| 8 | **Test-Driven** | Skill design should be verifiable; have a way to prove it works before delivery (gate integration). |
| 9 | **Proper Formatting** | Enforce consistent syntax (e.g., n8n 2.x expression format, no moment.js, luxon preferred). |

### 3. Skill Must Not Violate Any Clean Code Principle
The skill must not embody any of the "Code Smells" listed in Clean Code Chapter 17, specifically:
- No redundant/commented-out code in the skill's own docs
- No "train wreck" method chaining depth ≥ 3 in the skill's examples
- No "needless duplication" of patterns that existing skills already cover
- No "obscured intent" — the skill's purpose must be clear from its description and name
- No "inappropriate static methods" — static state should be minimal or absent

### 4. Integration with Router & Pipeline
When a new skill is registered via `router_register.py`:
- The script must verify the skill's description contains the "Clean Code alignment" line
- If missing, the script must auto-add a minimal alignment line referencing 3 principles before allowing registration
- The build-gates-pipeline must include a Clean Code alignment check stage (pre-flighting the skill's JSON/SKILL.md for principle violations)

### 5. Documentation Footnote
Every skill's SKILL.md must include a footer note:
```
Clean Code Alignment: References principles 1, 3, 7 (example). 
See: https:// Uncle Bob's Clean Code Handbook for full principle list.
```

### 6. Examples of Well-Aligned Skills (already in project)
- `best-practice-first-designer`: enforces 1) meaningful names, 2) single function per node, 3) small nodes
- `incremental-generation`: enforces 1) small functions, 2) single responsibility per node, 4) no duplication (schema check)
- `n8n-syntax-v2-enforcer`: enforces 1) meaningful names (expression variables), 2) small expressions, 9) proper formatting
- `off-by-one-boundary-guard`: enforces 1) meaningful names (interval status), 2) precision over cleverness, 6) Law of Demeter (boundary audit depth)
- `law-of-demeter-guard` (new): enforces 6) Law of Demeter (primary), 2) small functions (reduce depth), 1) meaningful names (root-level methods)

### 7. Examples of Poor Alignment (rejected historically)
- Skills that invent new parameter names without schema reference (violates "no duplication")
- Skills that chain 4+ expressions in a single Code node (violates "Law of Demeter"/"small functions")
- Skills with cryptic single-letter variable names in descriptions (violates "meaningful names")
- Skills that duplicate existing gate logic without referencing the existing pattern (violates "no duplication")

## Enforcement

### Automated Checks (scripts/)
- `scripts/skills_docs_generator.py --check-cc-alignment` — validates every SKILL.md has the Clean Code alignment line referencing 3+ principles
- `scripts/router_register.py --cc-verify <skill-name>` — verifies alignment before router registration

### Manual Review
- Before any skill is committed, the uploader must state which 3 principles the skill enforces in the commit message
- If the uploader cannot state 3 principles, the skill is sent back for alignment enhancement

## Philosophy

This methodology ensures that every skill in the project, even if generated automatically or installed from skills.sh, carries forward the "craftsmanship over crap" philosophy that Clean Code embodies. The 3-principle minimum is intentional: it's enough to create meaningful differentiation from generic, low-effort skills, while remaining achievable for any skill author.

**Goal**: By the next skill addition cycle, 100% of skills in `.opencode/skills/` will have verified Clean Code alignment.