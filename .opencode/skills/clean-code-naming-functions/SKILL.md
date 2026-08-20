---
name: clean-code-naming-functions
description: Applies the naming and function chapters of Robert C. Martin's Clean Code to write code that reads like prose: intention-revealing names for variables, classes, and methods; small functions with a single responsibility; the rule of one level of abstraction per function; and function arguments kept minimal with side effects banished. Use when the user says 'name this better', 'write a small function', 'function too long', 'too many arguments', 'naming conventions', 'Clean Code naming', 'single responsibility function', 'one level of abstraction', or when reviewing code for readability.
---

# Clean Code: Naming and Functions

Clean Code argues that the name of a thing carries most of its meaning. Naming and functions are the two levers that make a module readable without a comment: a name that reveals intent, and a function small enough to state one thing. This skill encodes both disciplines.

## Intention-Revealing Names
- A name should answer what the variable means and why it exists, not how it was computed.
- Prefer a descriptive name over a short one; a longer name is a bargain if it removes a comment.
- Avoid disinformation: don't name something a lie because it is shorter.
- Make meaningful distinctions — the difference in the name must be the difference in the meaning, not a number or a misspelling.
- Choose names searchable and pronounceable so the codebase stays greppable and speakable in review.

## Small Functions
- A function should do one thing, do it well, and do only that — if you can extract another step with a clear name, the function is too large.
- Keep each function short enough that its purpose is visible in a single screen.
- Prefer functions that read top-down, each call moving to a lower level of abstraction like an essay that descends from the thesis to the details.
- Give functions verb-phrase names that describe what they promise, so call sites read like sentences.

## One Level of Abstraction
- Keep the steps inside a function at a consistent level; do not mix policy with mechanism in the same body.
- Push low-level details into helper functions so the main function reads as a sequence of decisions.
- If a function reads a setting, checks a rule, and formats a string, those three levels belong in three functions.
- Review each function for mixed levels as a signal to extract.

## Arguments, Side Effects, and Command-Query
- Keep argument lists short — three is the practical ceiling, and fewer is better.
- Cluster related arguments into a single object or struct rather than passing a parade of parameters.
- Do not use output arguments to return results; prefer returning the value so the caller reads clearly.
- Separate commands from queries: a function either changes state and returns nothing, or returns a value and changes nothing.
- Ban hidden side effects — a function that mutates global state while returning a value will surprise every caller.

## Pairs with
clean-code, art-of-readable-code, pragmatic-programmer, code-smell-detector, surgical-diff-patch-editor
