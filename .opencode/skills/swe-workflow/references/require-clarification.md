# Require Clarification

## Contract — Read This First

1. In Full mode, check for an active plan before starting a new implementation plan.
2. Read the repository before asking; do not ask for facts the code, docs, config, or tests can answer.
3. Ask only when the answer materially changes scope, behavior, acceptance, design, compatibility, or an irreversible action.
4. Ask the smallest focused question needed and include a recommendation when useful.
5. Analyze each answer for newly introduced requirements or unresolved decision-critical ambiguity.
6. Do not proceed to planning while a decision-critical question remains unanswered.
7. Do not add a routine confirmation handshake after the user has already approved the scope; the completed plan gets the sole routine pre-execution approval.

## When to Use

- Full-mode implementation with unresolved product, architecture, API, schema, security, compatibility, or irreversible choices
- Lightweight discovery that uncovers a decision required before safe edits
- A user answer that introduces materially different scope or acceptance criteria

## Check for Active Plans

```bash
find plans -mindepth 2 -maxdepth 2 -name plan.md 2>/dev/null | sort
rg -n "^> Status:|^\| Step .* \|" plans/*/plan.md plans/*/steps/*.md 2>/dev/null
```

If a nested plan has an `IN_PROGRESS` step: remind the user and ask whether to continue it or switch. Step-file status is authoritative; do not assume abandonment.

## Instructions

1. **Analyze the request:** identify the intended outcome, explicit constraints, acceptance evidence, and any irreversible or contract-sensitive choice.

2. **Explore first:**
   - Read relevant code, docs, config, callers, and tests.
   - Find existing conventions and reusable behavior.
   - Resolve factual uncertainty with repository evidence.

3. **Apply the decision test:**

   | Ask | Do not ask |
   |-----|------------|
   | Multiple plausible outcomes would produce materially different behavior | A nearby established convention answers the question |
   | The user must approve a product, UX, API, schema, security, compatibility, or destructive choice | The detail is implementation-local and reversible |
   | Acceptance cannot be made testable without the answer | The question is speculative or does not change implementation |

4. **Ask efficiently:**
   - Ask one focused decision at a time; include only inseparable subparts.
   - Prefer concrete options and state the recommended option with rationale.
   - Stop when scope and acceptance are sufficient for a safe plan; do not explore hypothetical branches without a trigger.

5. **Analyze the answer:** confirm it resolves the decision and note any new scope, acceptance, or design consequence. Ask a follow-up only when that consequence blocks planning.

6. **Hand off to planning:** summarize material decisions and assumptions once. If the user already approved the implementation scope, proceed to `create-plan`; do not ask a second "ready to plan" question. The resulting plan is presented once for execution approval.

## Handling Partial or Vague Answers

When the answer does not resolve the focused decision:

```
Agent: "Should Task Listener also be removed? Recommended: keep it, because no caller evidence links it to this cleanup."
User:  "Use the same behavior."

Agent: "I cannot map 'same behavior' to remove or keep. Should Task Listener be removed?
        a) Keep (recommended)  b) Remove"
```

Do not proceed while the focused decision remains unresolved. Do not reinterpret a partial or vague answer as approval.

## Mandatory Checklist

- [ ] Repository evidence gathered before questions
- [ ] Material scope and acceptance criteria are clear enough to plan
- [ ] Decision-sensitive choices identified and answered
- [ ] No unanswered question can materially change implementation
- [ ] Answers analyzed for scope or acceptance changes
- [ ] Already-approved scope is not sent through a duplicate confirmation handshake

## Constraints

- **Never invent decision-critical requirements** — ask when evidence cannot resolve them
- **Never plan with decision-critical open questions**
- **Read the repository first** — do not ask what you can discover
- **Analyze every answer** for material scope or acceptance changes
- If the user says "just do it," proceed when the request is safely actionable; otherwise ask only the single blocking decision
- Do not require confirmation of facts or scope the user already explicitly approved

## Next Step

→ **create-plan** — when decision-critical questions are resolved and Full-mode implementation scope is sufficiently clear.
