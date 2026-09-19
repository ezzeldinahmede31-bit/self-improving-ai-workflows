---
name: missing-semester-cs-tools
description: "Masters the tooling CS degrees skip: shell, editors, data wrangling, and debugging. Use when the user says 'bash scripting', 'vim', 'data wrangling', 'sed awk', 'dotfiles', 'version control', 'debugging tools', 'profiling', 'Missing Semester', or when fluency with the machine itself is the bottleneck."
---

# Missing Semester CS Tools

Distilled from MIT's *The Missing Semester of Your CS Education*: expertise
with your tools multiplies every other skill. Each unit is one evening of
practice, not one semester of theory.

## Purpose

Reach professional fluency with the shell, editor, and debugging/profiling
toolchain so the machine never slows the thinking.

## The units (each: learn by doing, keep a cheat-sheet)

1. **Shell that works for you.** Job control, redirection/pipes, quoting
   (single vs double vs none), globbing, history expansion, dotfiles under
   version control. Script defensively: `set -euo pipefail`, quote every
   expansion, prefer `[[ ]]`.
2. **Editors at speed.** Modal editing (vim motions/operators/text-objects),
   macros for repetition, buffers/windows/tabs. Goal: editing at the speed
   of thought for the 20 motions you use daily — relearn the rest on demand.
3. **Data wrangling.** `grep`/`sed`/`awk`/`sort`/`uniq`/`cut`/`paste`/`join`,
   `jq` for JSON, regex fluency (greedy vs lazy, groups, lookarounds).
   Pipeline discipline: inspect each stage's output before adding the next.
4. **CLI environment.** SSH + keys + agent forwarding (never copy private
   keys), tmux/screen for persistence, dotfile sync, package managers, cron
   for scheduling. Know your PATH, man pages, and `--help` first.
5. **Version control fluency.** Daily loop (status/diff/add/commit/push/pull),
   branching hygiene, stash, bisect for regressions. (Deep model: `pro-git`.)
6. **Debugging and profiling.** Reproduce, then bisect; debugger over prints
   for state (breakpoints, watchpoints, backtraces); profilers over guesses
   for speed (sampling first, instrumentation second). Strace/ltrace when the
   OS is the suspect.
7. **Metaprogramming and security hygiene.** Build systems (make targets as
   dependency graphs), CI basics, secrets never in shell history or repos,
   permissions (chmod/ssh 0600/0700), checksums for downloads.

## Verification

Fluency test per unit: perform the core task cold (no googling) in under two
minutes — edit a file with macros, wrangle a CSV to an answer, bisect a
regression, profile a hotspot. Slow = drill again.

## Pairs with

- `pro-git` (deep Git model), `bash-cookbook` (shell recipes),
  `linux-command-line` (deeper shell), `zeller-why-programs-fail`
  (debugging science), `systems-performance-profiling` (measurement).
