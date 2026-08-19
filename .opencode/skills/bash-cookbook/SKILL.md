---
name: bash-cookbook
description: Applies Bash Cookbook (Carl Albing & JP Vossen) to everyday shell automation: battle-tested recipes for variables, arithmetic, functions, text processing, redirection, and safe system administration in bash. Covers configuration files, quoting pitfalls, command substitution, arrays, and security-conscious script writing. Use when the user says 'bash recipe', 'make my script safer', 'bash arrays', 'redirection tricks', or 'debug my shell script'.
---
# bash-cookbook

Albing and Vossen collect proven, practical bash recipes that solve real automation problems without reinventing shell idioms.
Use this skill for any bash scripting task that needs a reliable, reviewed pattern rather than an improvisation.
It turns bash from a set of tricks into a language you can build systems with.

## Core principles
- Bash has real language features, including variables, functions, arrays, and arithmetic, not just command chaining.
- Quoting rules decide whether words, globs, or commands are interpreted; getting them right removes whole bug classes.
- Every script inherits an environment; knowing what is inherited and what is local prevents leakage.
- Text tools and command substitution let one script transform and compose data cleanly.
- Safety in scripts comes from discipline: set options, error checks, and deliberate side effects.
- A recipe is only useful when it documents the assumptions it makes.

## Key patterns
- Array loops for robust word lists that survive spaces.
- Arithmetic evaluation for numeric logic without external tools.
- Functions for reusable script components with explicit return values.
- Case statement dispatch for menu and argument handling.
- Redirection groups that capture output and errors separately.
- Command substitution and process substitution for composing results.

## Applying this to scripting/automation/code
- Reuse the book's quoting and array patterns when generating shell commands from n8n Code nodes.
- Add set -euo pipefail and explicit traps as the default script skeleton.
- Validate inputs and fail fast before any destructive command runs.
- Implement retry loops for flaky network calls inside wrapper scripts.
- Keep credentials out of scripts by sourcing them from restricted files or the environment.
- Document each recipe's version assumptions so it survives host upgrades.

## Hard rules
- Never embed secrets in scripts or command lines.
- Never run a destructive command without an explicit guard and confirmation.
- Never use eval on untrusted input.
- Never assume the same bash version or feature set across hosts.
- Never background a job without handling its exit status.
- Never write a recipe you cannot explain line by line.

## Pairs with
pragmatic-programmer, devops-automation, infrastructure-as-code, n8n-code-nodes-official, code-linter-python-js
