---
name: ast-codebase-graph-navigator
description: "Navigates multi-file codebases using Abstract Syntax Trees (AST), import graphs, and caller-callee traces instead of brute-force full-file loading. Use for any large project, unknown codebase, or multi-module change. Trigger phrases: 'understand this code', 'where is X used', large repo, 'how do these files connect'."
---

# AST CODEBASE GRAPH NAVIGATOR SKILL

## DIRECTIVE
Never read massive codebases linearly. Parse import statements, class
hierarchies, and function caller-callee graphs to isolate ONLY the exact
relevant code slices.

## GRAPH NAVIGATION PROTOCOL
1. **Map Entry Point:** Parse entry-file imports to map dependency flow
   (start from the entrypoint the task names).
2. **Trace AST Tree:** Extract method signatures, class definitions, and type
   definitions WITHOUT loading full function bodies — use `grep`/`glob` for
   `def ` / `class ` / `import` lines first.
3. **Isolate Scope:** Load only target functions and their immediate
   callers/callees (two `Read` slices, not the whole file).
4. **Maintain Dependency Map:** Keep a dynamic structural map of changed files
   (imports that must still resolve, callers that must still work) to prevent
   breaking downstream dependencies.

## Tool recipes
- Find where a symbol is defined/used: `grep "def foo" / "foo(" across the repo`.
- Find imports of a module: `grep "from X import"` / `"import X"`.
- Class hierarchy: `grep "class Y("`, then read only the base class slice.
- Callers of a function: `grep "y.method("` / `"method("`.

## Anti-pattern
Do not `Read` a 2000-line module top-to-bottom "to be safe". Navigate: signature
→ caller/callee → only then the specific body you must change.