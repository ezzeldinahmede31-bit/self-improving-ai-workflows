---
name: art-of-readable-code
description: Applies The Art of Readable Code by Dustin Boswell and Trevor Foucher to write code that is easy to understand: pack meaning into names, reduce what a reader must remember, explain the why in comments, keep functions small, and prefer clarity over cleverness. Encodes the measurable goal that code is good when the next reader understands it quickly and correctly. Use when the user says 'make this code readable', 'better variable names', 'refactor for clarity', 'write maintainable code', 'review my code for readability', or 'simplify this function'.
---

# art-of-readable-code

Readable code is the cheapest code to maintain, because the reader is the one who must change it later. The book's measurable goal is simple: minimize the time it takes the next person to understand your code, and this skill turns that goal into concrete habits.

## Core principles

- Code is written once and read many times; optimize for the reader.
- Names carry meaning; choose them for the reader, not the writer.
- Comments should explain why, not restate what.
- Reduce what a reader must remember in any one place.
- Smaller units of work are easier to understand and reuse.
- Clarity beats cleverness every time.

## Key patterns

- Descriptive names that match the domain, with no cryptic abbreviations.
- Short functions with one job and an obvious name.
- Consistent formatting that groups related logic visually.
- Comments that capture intent and non-obvious constraints.
- Conditionals written so the happy path is the easy path.
- Extracting named helpers instead of nesting deeply.

## Applying this to scripting/automation/code

- Write n8n Code nodes a reviewer can follow in one pass.
- Keep workflow expression names aligned with the business meaning.
- Refactor long functions into named steps before delivery.

## Hard rules

- Name for the reader; expand abbreviations fully.
- Comment the why, never restate the what.
- Split functions that do more than one thing.
- Avoid clever one-liners that cost comprehension.
- Keep nesting shallow and branches readable.
- Make the happy path the most visible path.

## Pairs with

clean-craftsmanship, pragmatic-programmer, code-smell-detector, code-execution-guided-swemaster, evidence-over-memory
