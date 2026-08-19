---
name: linux-command-line
description: Applies The Linux Command Line (William Shotts) to shell scripting and automation: a complete introduction to the bash environment, including commands, pipelines, redirection, permissions, processes, variables, control structures, and text processing with grep, sed, and awk. Covers shell grammar, expansion rules, job control, and writing robust scripts. Use when the user says 'write a bash script', 'why does my pipe fail', 'shell expansion', 'process text with awk', or 'automate the terminal'.
---
# linux-command-line

Shotts teaches the command line as a programming environment, from a first command to dependable scripts.
Use this skill whenever a task is best expressed as a shell pipeline or a bash script that must behave correctly.
It makes the terminal a precise, repeatable tool instead of a set of memorized incantations.

## Core principles
- The shell is a language of tiny programs wired by pipes; composition is the point.
- Expansion happens before execution, and understanding its order prevents classic errors.
- Every command has three streams, stdin, stdout, and stderr, and redirection controls their flow.
- Permissions and ownership govern what a script is allowed to touch.
- Text processing tools (grep, sed, awk) form the core of data wrangling on Linux.
- A script is only trustworthy when failures surface instead of being swallowed.

## Key patterns
- Pipelines that transform data step by step with failures made visible.
- Here-documents and variable expansion for templated configuration.
- Quoting discipline that survives spaces and special characters.
- Job control and background execution for long-running work.
- Exit-status checking after every critical command in a script.
- Regular-expression building blocks for finding and editing text.

## Applying this to scripting/automation/code
- Express data-cleaning steps as grep/sed/awk pipelines inside n8n Code nodes via subprocess.
- Use set -euo pipefail so every script fails loudly on the first real error.
- Write idempotent provisioning scripts with explicit checks before each action.
- Convert ad-hoc terminal work into versioned scripts with the same logic.
- Escape and quote user-supplied values so injection stays impossible.
- Test pipelines against sample data before pointing them at production files.

## Hard rules
- Never parse output without handling missing input and empty results.
- Never run rm, chmod, or dd without a dry run and an explicit target.
- Never trust a variable unquoted in a script.
- Never rely on the default shell when bash semantics are required.
- Never build a command string from unvalidated user input.
- Never let a pipeline continue after a stage that failed.

## Pairs with
pragmatic-programmer, devops-automation, infrastructure-as-code, n8n-code-nodes-official, code-linter-python-js
