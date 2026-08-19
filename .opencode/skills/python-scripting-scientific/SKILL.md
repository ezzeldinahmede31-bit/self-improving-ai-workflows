---
name: python-scripting-scientific
description: Applies Hans Petter Langtangen's Python Scripting for Computational Science to write scripts that drive scientific computation: use Python as the glue for compiled numerical kernels, read and write data files with standard parsers, generate plots and reports programmatically, wrap Fortran/C/C++ libraries, and structure exploratory work as reusable modules. Covers file I/O patterns, array-oriented numpy idioms, plotting, and the workflow where a short script replaces manual labor. Use when the user says 'write a script for this computation', 'scientific scripting', 'parse this data file', 'automate my simulation runs', or 'generate a report from my results'.
---

# python-scripting-scientific

Python is the glue that turns heavy numerical machinery into something a human can drive: a short, parametrized script reads raw data, calls a compiled kernel, and renders the result as a plot or report. The book shows that scripts beat interactive clicking for any task that must run more than once, and that clean module structure keeps exploratory code from rotting into a tangle.

## Core principles

- Script over GUI: anything run more than once deserves a file you can re-run.
- Plain-text data files with standard formats are the interchange layer.
- Array computing via numpy, never hand-written Python loops over big data.
- Make every run reproducible: fixed seeds, logged inputs, versioned scripts.
- Separate the compute step from the visualization step.
- Wrap compiled code behind a small Python interface instead of reimplementing it.

## Key patterns

- Parse tabular data with csv or regex, then validate every row before use.
- Drive the numeric kernel with numpy arrays and index by shape, not by magic numbers.
- Generate plots and reports from the same results object, so they never drift.
- Accept parameters from the command line so the same script serves many runs.
- Write results to disk atomically (write a temp file, then rename).
- Keep reusable helpers in modules and a thin script that only orchestrates.

## Applying this to scripting/automation/code

- Build n8n Code nodes as small, single-purpose functions that parse and reshape data.
- Turn raw logs or exports into clean tables before any downstream step.
- Generate charts or text reports that ship with the workflow output.
- Replace repeated manual editing with one idempotent transform script.
- Wrap a heavy third-party tool behind a thin, testable Python layer.

## Hard rules

- Never embed absolute paths or machine-specific values in a script.
- Validate parsed data before computation; garbage in must fail loudly.
- Keep numeric hot paths in numpy, not interpreted loops.
- Make every script rerunnable without side effects on re-run.
- Write one report per run and store the inputs that produced it.
- Document every assumption the script silently makes.

## Pairs with

code-linter-python-js, code-execution-guided-swemaster, evidence-over-memory, systems-performance-profiling, computer-systems-programmers-perspective
