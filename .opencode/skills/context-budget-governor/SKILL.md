---
name: context-budget-governor
description: "Protect a small context window so it behaves like a big one. Use at the START of any long session, large refactor, big-file read, or when many files/tool outputs are involved. Trigger phrases: working on a big repo, 'continue', long debugging session, reading huge files, or when you feel the conversation getting heavy. Prevents degraded recall and 'forgot the earlier requirement' failures."
---

# Context Budget Governor

A small-context model loses early instructions as a session grows. Treat context
as a **finite budget** you spend deliberately, not a notebook that fills up.

## Rules

1. **Check the budget before spending**: if a file/tool output will be huge,
   read it in slices (`Read` with `offset/limit`) or `Grep` for the exact symbol
   instead of loading the whole thing. Prefer `glob`/`grep`/`task`(explore
   agent) over full reads.
2. **One live document**: for a long task, maintain a single working note
   (e.g. `PLAN.md` or the todo list) with ONLY: objective, current step,
   decisions, blockers. When the chat grows, *re-read that note* instead of
   re-deriving from memory.
3. **Compress aggressively**: after completing a sub-step, replace its full
   detail with a 1-line summary in the note. Full detail belongs in files,
   not in the conversation.
4. **Never re-paste**: when you need an earlier tool result, re-fetch it
   narrowly (one `Read` with offset) rather than reprinting old output.
5. **Delegate exploration**: for codebase questions use the `task` tool with an
   `explore` agent (medium/very-thorough) so the heavy reading happens in the
   sub-agent's context, not yours.
6. **Checkpoint on state changes**: every time you edit files, record
   `what changed + file:line` in the note in ≤2 lines.

## Budget-limit signal
If the current turn already contains a lot of tool output, PREFER:
- `grep` + short reads over full reads,
- summarizing findings to the user in 3 bullets instead of dumping output,
- splitting the work and confirming scope before continuing.