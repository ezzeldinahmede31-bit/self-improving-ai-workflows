---
name: esr-unix-philosophy
description: "Designs software the Unix way: small composable tools, text interfaces, and transparency. Use when the user says 'Unix philosophy', 'do one thing well', 'composition', 'pipes', 'text interface', 'KISS', 'worse is better', 'ESR', 'Art of Unix Programming', or when a design is getting monolithic and needs splitting."
---

# ESR Unix Philosophy

Distilled from Eric S. Raymond's *The Art of Unix Programming*: seventeen
rules compressed into one instinct — build simple parts connected by clean
interfaces, and let the USER program the combinations.

## Purpose

Keep systems small, transparent, and composable: every feature must justify
itself against simplicity, and every interface must be scriptable.

## The load-bearing rules (the ones that decide designs)

1. **Modularity:** write simple parts connected by clean interfaces. If a
   component cannot be described in one sentence, split it.
2. **Composition:** design programs to be connected to other programs (pipes,
   filters, file formats) — the user will invent uses you never imagined.
3. **Separation:** separate policy from mechanism (what vs how), and
   interfaces from engines (UI is replaceable skin over a scriptable core).
4. **Simplicity & Parsimony:** simplest sufficient solution; big systems only
   from small systems that work independently. Never add a feature "for
   completeness".
5. **Transparency:** design for visibility — observable state, debuggable
   behavior, no hidden magic. If you must be clever, encapsulate the
   cleverness behind a dumb interface.
6. **Textuality:** human-readable formats and protocols (logs, configs, wire
   formats you can read). Binary is earned by measurement, not assumed.
7. **Economy & Generation:** programmer time beats machine time; don't hand-
   hack what you can generate (code generators, DSLs, declarative specs).
8. **Repair:** fail noisily and early; design errors to be recoverable and
   diagnosable ("rule of repair": when in doubt, fail out loud).
9. **Least surprise:** interfaces should do the obvious thing; match the
   ecosystem's conventions before inventing your own.

## Application test (run on any design)

- Can each piece run standalone and be tested standalone? (If no: merge or split.)
- Can a user script it without your GUI? (If no: add the CLI/API first.)
- Is every persistent format human-readable? (If no: justify with numbers.)
- Where does it fail, and does the failure say what happened? (If silent: fix.)

## Verification

A design review ends with: the one-sentence description of each part, the
composition story (how parts connect), and which rule each contentious choice
cites. Unjustified complexity gets removed, not documented.

## Pairs with

- `zero-trust-modular-decomposer` (enforced splitting),
  `philosophy-software-design-ousterhout` (deep modules),
  `practice-of-programming-kernighan` (craft), `bash-cookbook` (composition).
