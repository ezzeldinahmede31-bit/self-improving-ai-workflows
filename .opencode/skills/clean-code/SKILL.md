---
name: clean-code
description: Applies Robert C. Martin's Clean Code to writing code that is a joy to work on: meaningful names, small functions with one responsibility, comments that explain why not what, formatting, error handling as a first-class concern, and the disciplines that keep a codebase clean as it grows. Use when the user says 'clean code', 'meaningful names', 'small functions', 'single responsibility', 'clean functions', 'Uncle Bob', 'refactor for clarity', 'readable code', 'naming', or when reviewing or improving code quality.
---

# Clean Code (Robert C. Martin)

Clean Code is the standard on how to write code that humans can maintain. This skill applies its rules of names, functions, comments, and error handling to everyday work.

## Meaningful names

- A name says intent: choose names that answer what the thing is and why it exists.
- Use searchable, pronounceable names and avoid encoded or abbreviated ones.
- Classes and objects are named by nouns; functions by verbs or verb phrases.

## Small functions

- A function does one thing, does it well, and does only that; extract until it is small.
- Functions should not mix levels of abstraction or hide side effects.
- Arguments complicate reading; prefer fewer and named ones, or structures.

## Comments and error handling

- Comments explain why, not what; the code should say what it does.
- Error handling is a separate concern with a clear strategy: exceptions or error codes, chosen once.
- Handle the happy path and the failure path with equal care.

## The discipline

- The Boy Scout rule: leave the code cleaner than you found it.
- Clean code is a craft practiced daily, not a one-time cleanup.
- Readability for the next engineer is the top priority; the machine runs anything, people maintain what they understand.

## Pairs with
refactoring-improving-design, code-smell-detector, pragmatic-programmer, code-complete, tdd-sandbox-proof-engine
