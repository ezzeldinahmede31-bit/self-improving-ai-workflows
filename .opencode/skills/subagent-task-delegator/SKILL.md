---
name: subagent-task-delegator
description: "Decomposes large multi-part jobs into isolated sub-tasks executed by sub-agents, preserving the main conversation context budget. Use on heavy refactors, multi-file features, research-and-implement tasks, or parallelizable work (e.g., schema + API + tests split). Trigger phrases: 'delegate', 'parallel work', 'split the work', 'heavy refactor', 'multi-file change'."
---

# SUBAGENT TASK DELEGATOR SKILL

## DIRECTIVE
When facing a multi-part or heavy refactoring task, do NOT process everything
in a single linear thread. Decompose the job into self-contained sub-tasks and
execute them as isolated sub-routines.

## DELEGATION PROTOCOL
1. **Deconstruct & Isolate:** Split the main goal into 2-4 independent
   sub-tasks (e.g., Task A: DB Schema Update, Task B: API Route Update,
   Task C: Unit Test Creation).
2. **Sub-Agent Context Budget:** For each sub-task, define ONLY the essential
   context (relevant file paths, function signatures) to keep memory footprint
   minimal.
3. **Execution & Handoff:**
   - Execute sub-task A -> Validate output -> Capture concise summary.
   - Execute sub-task B -> Validate output -> Capture concise summary.
4. **Synthesis:** Merge all sub-agent deliverables into the main workspace and
   run integration checks.

## Local adaptation
This workspace ships the tools for real delegation: `task` tool with
`subagent_type: "general" | "explore"`. Delegate file-discovery to `explore`
(reads a bounded slice), and code-writing to `general`. Hand off ONLY: file
paths, function signatures, and the exact acceptance check per sub-task. Do not
dump whole files into a sub-agent prompt — that defeats the context budget this
skill exists to protect. After synthesis, re-run the full suite
(`venv/bin/python -m pytest`, 269 passing) since sub-agent outputs may touch
interdependent modules.