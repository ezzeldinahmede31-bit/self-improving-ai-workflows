---
name: surgical-diff-patch-editor
description: "Enforces exact line-level search-and-replace block edits instead of rewriting whole files, preventing accidental code truncation. Use whenever changing a fraction of a file's contents. Trigger phrases: 'edit only this line', 'don't rewrite the file', 'targeted edit', 'patch', 'surgical change'."
---

# SURGICAL DIFF PATCH EDITOR SKILL

## DIRECTIVE
NEVER overwrite an entire file if you are modifying only a fraction of its
contents. Use targeted block replacement (Search & Replace) to preserve
existing code formatting and structure.

## EDITING RULES
1. **Pre-Read Verification:** Always read the target lines immediately before
   writing the patch to guarantee line numbers and exact string matches.
2. **Search Block Rules:** Must include 3-5 lines of surrounding context to
   avoid false matches in duplicate code blocks.
3. **Replacement Integrity:** Produce clean SEARCH/REPLACE blocks formatted as:
   ```python
   <<<<<<< SEARCH
   def old_function():
       return False
   =======
   def updated_function():
       return True
   >>>>>>> REPLACE
   ```
4. **Post-Patch AST Check:** Run a quick syntax check
   (`python -m py_compile <file>`) immediately after applying the patch.

## Local adaptation
The `Edit` tool in this workspace mirrors exactly this protocol (oldString must
be unique + 3-5 lines of context, single change per call, no full rewrites).
Apply it verbatim: pre-read the region with the `Read` tool, then edit with the
dedicated `Edit` tool instead of the `Write` tool. When a section repeats across
the file, extend the oldString until the match is unique — never use brute-force
global replace on ambiguous blocks. After the edit, verify syntax with
`venv/bin/python -m py_compile <file>` and, for logic changes, run the affected
test (`venv/bin/python -m pytest tests/ -k <name>`).