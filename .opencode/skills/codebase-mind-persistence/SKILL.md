---
name: codebase-mind-persistence
description: "Persistent on-disk codebase mind map (approximate 1M-token context emulation) built ONCE per codebase — symbol index, module-level summaries, dependency graph, API surface, test map — so a small-context model behaves AS IF it held the whole repo in context on later tasks, without re-reading files. Use when asked to 'read/understand this whole repo', 'work confidently across this codebase', 'remember the architecture between sessions', on a large multi-module repo, or when an ast graph was built and you want it persisted for later sessions. Trigger phrases: 'understand this repo once and remember it', 'codebase mind map', 'keep the whole codebase in mind', 'I keep re-reading the same files', 'large repo, load everything'. Pair with ast-codebase-graph-navigator (graph construction) and context-budget-governor (eviction while working)."
---

# Codebase Mind Persistence

## The gap it closes
A 1M-context model reads the entire repo once and keeps it in working memory for the
whole session. A small-context model re-reads files every turn and forgets cross-file
structure. This skill closes that gap by turning a one-time AST pass into a PERSISTENT
mind map on disk: everything the agent learned about the repo lives in
`memory/.codebase-minds/<repo-slug>.md`, reloadable in <2K tokens, so every later task
starts "as if" the whole repo were in context.

## Build protocol (ONCE per repo; cheapest when a repo is first touched)

1. **Inventory**: `find`/`glob` all source files; record counts per directory; note
   language(s), build system, entry points (main, CLI, server), test locations.
2. **Symbol index** (AST-based, mechanical — no reading needed file-by-file):
   - classes (name → file:line, public methods, inheritance)
   - functions (name → file:line, signature, one-line docstring or "no doc")
   - constants/config keys, env vars read, exported API surface
   Automate with tree-sitter/ast via scripts; if unavailable, `grep -n "def \\|class \\|func \\|export"`.

   ```
   scripts/build_repo_mind.py  (venv) → writes JSON index
   ```

3. **Module summaries** (cheap pass): for each module, one paragraph distilled from its
   docstring + top symbols + imports (imports reveal dependencies without reading body).
4. **Dependency graph**: modules → what they import → who calls whom (from step 2 index).
5. **Test map**: test files → which module each covers (from test names/imports).
6. **Persist** to `memory/.codebase-minds/<repo-slug>.md`:
   ```
   # <repo> mind map (built <date>)
   ## Inventory & entry points
   ## Symbols (per file, compact)
   ## Module summaries
   ## Dependency graph (text edges)
   ## Test map
   ## Open questions / unknowns (honest: what was NOT read)
   ```
   Keep the file < ~2K tokens: symbols one line each, summaries one paragraph, edges one
   line each. This is a COMPRESSION, not a dump; raw detail stays in the files — the map
   tells you WHERE to rehydrate from.

## Usage protocol (every later session on the same repo)

1. Load `memory/.codebase-minds/<repo-slug>.md` ONCE into context (the 2K-token "mind").
2. For a task touching module X: read ONLY the lines/region of X that the mind marks
   relevant (targeted `read` with offset/limit, or `grep` for the exact symbol) —
   rehydration is exact, via the map, not a full-file re-read.
3. Keep a running in-context delta: files read THIS session, decisions made THIS session
   (append to the mind file's "session deltas" section, or to a scratch note — do NOT
   bloat the mind map itself).
4. **Update the mind** when the repo changes: on any new file/renamed symbol, patch the
   corresponding lines (surgical diff, not rebuild) — the map must never lie about
   WHERE something is (freshness rule).

## Rules (do not do)
- Do NOT paste the whole mind map into every prompt — load once, reference afterwards
  with explicit "per mind map: X" citations.
- Do NOT store raw code in the mind map. It is an INDEX + STRUCTURE, and MUST stay < 2K
  tokens; raw recovery always comes from files via the map's pointers.
- Do NOT build the mind map by LLM-reading every file (costs a full corpus pass every
  time). Build it ONCE mechanically, then maintain it surgically.
- NEVER let the map silently go stale after large refactors — mark "STALE — rebuild"
  and rebuild via the script, don't patch-drift.

## Handoff / pairing
- Construction partner: `ast-codebase-graph-navigator` (graphs + caller-callee while
  the map is being built) and `long-context-sharding-engine` when per-file bodies must
  be read in bulk.
- This is the memory substrate for `single-pass-frontier-emulator`: with the mind in
  context, a single-pass delivery over a big repo is coherent because the map IS the
  whole-repo working memory at 2K tokens.