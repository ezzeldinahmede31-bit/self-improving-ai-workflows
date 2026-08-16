#!/usr/bin/env python3
"""Mechanical codebase mind-map builder.

Builds a persistent index + compact markdown "mind map" for a repo so a
small-context model behaves AS IF it held the whole repo (symbol index,
module summaries, dependency graph, test map). This is the mechanical tool
backing the `codebase-mind-persistence` skill.

Usage:
  venv/bin/python scripts/build_repo_mind.py [--repo PATH] [--out DIR] [--slug NAME]

Outputs:
  <out>/<slug>.json   full mechanical index (symbols, imports, tests, inventory)
  <out>/<slug>.md     compact mind map (< ~2K tokens) per the skill protocol

Pure stdlib (ast + pathlib). Python parsed with `ast`; JS/TS handled with a
light regex symbol scan so the map still gets an inventory for them.
"""
import argparse
import ast
import json
import os
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

SOURCE_EXTS = {".py", ".js", ".jsx", ".ts", ".tsx"}
TEST_HINTS = ("test", "tests", "spec", "e2e", "conftest")

STOP_DIRS = {".git", "node_modules", "venv", ".venv", "__pycache__",
             ".opencode", ".agents", "memory", "dist", "build", ".next"}


def iter_source_files(repo: Path):
    for root, dirs, files in os.walk(repo):
        dirs[:] = [d for d in dirs if d not in STOP_DIRS]
        for f in files:
            if Path(f).suffix in SOURCE_EXTS:
                yield Path(root) / f


def py_symbols(path: Path):
    """AST pass: classes (methods+inheritance), functions, imports, docstring."""
    classes, funcs, imports = [], [], []
    doc = None
    try:
        tree = ast.parse(path.read_text(encoding="utf-8", errors="replace"))
    except (SyntaxError, UnicodeDecodeError, OSError):
        return classes, funcs, imports, None
    if ast.get_docstring(tree):
        doc = ast.get_docstring(tree).strip().split("\n")[0][:140]
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            bases = [b.id for b in node.bases if isinstance(b, ast.Name)]
            methods = []
            for item in node.body:
                if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    mdoc = ast.get_docstring(item)
                    methods.append(item.name + (f": {mdoc.splitlines()[0][:60]}" if mdoc else ""))
            classes.append({"name": node.name, "line": node.lineno,
                            "bases": bases, "methods": methods})
        elif isinstance(node, ast.FunctionDef):
            if node.lineno == getattr(node, "lineno", None):
                pass
            mdoc = ast.get_docstring(node)
            sig = f"({', '.join(a.arg for a in node.args.args)})" if node.args.args else "()"
            funcs.append({"name": node.name, "line": node.lineno,
                          "signature": node.name + sig,
                          "doc": mdoc.splitlines()[0][:100] if mdoc else "no doc"})
    for node in ast.iter_child_nodes(tree):
        if isinstance(node, ast.Import):
            imports += [a.name for a in node.names]
        elif isinstance(node, ast.ImportFrom):
            mod = node.module or ""
            imports += [f"{mod}.{a.name}" if a.name != "*" else f"{mod}.*" for a in node.names]
    return classes, funcs, imports, doc


def js_ts_symbols(path: Path):
    """Light regex pass for JS/TS: top-level functions, classes, imports."""
    text = path.read_text(encoding="utf-8", errors="replace")
    funcs, classes, imports = [], [], []
    for m in re.finditer(r"(?:export\s+)?(?:async\s+)?function\s+(\w+)\s*\(([^)]*)\)", text):
        funcs.append({"name": m.group(1), "signature": f"{m.group(1)}({m.group(2).strip()})", "doc": "no doc"})
    for m in re.finditer(r"(?:export\s+)?class\s+(\w+)", text):
        classes.append({"name": m.group(1), "bases": [], "methods": []})
    for m in re.finditer(r"from\s+['\"]([^'\"]+)['\"]", text):
        imports.append(m.group(1))
    return classes, funcs, imports, None


def build(repo: Path, slug: str):
    files = sorted(iter_source_files(repo))
    inventory = Counter()
    symbols = {}
    per_file_imports = {}
    docstrings = {}
    tests = []
    langs = Counter()
    for path in files:
        rel = str(path.relative_to(repo))
        langs[path.suffix] += 1
        inventory[str(path.parent.relative_to(repo)) or "."] += 1
        if path.suffix == ".py":
            cls, fn, imp, doc = py_symbols(path)
        else:
            cls, fn, imp, doc = js_ts_symbols(path)
        if doc:
            docstrings[rel] = doc
        per_file_imports[rel] = imp
        syms = []
        for c in cls:
            m = f"class {c['name']}" + (f"({','.join(c['bases'])})" if c["bases"] else "") + f" [{c['line']}]"
            syms.append(m)
            for meth in c["methods"]:
                syms.append(f"  .{meth}")
        for f in fn:
            syms.append(f"{f['signature']} [{f['line']}] — {f['doc']}")
        if syms:
            symbols[rel] = syms
        if TEST_HINTS and any(h in rel for h in ("test", "spec")):
            covered = [i.split(".")[0] for i in imp if not i.startswith(("test", "pytest"))]
            tests.append({"file": rel, "imports": imp, "covers_hint": covered})
    return {
        "slug": slug,
        "repo": str(repo),
        "language_counts": dict(langs),
        "inventory": dict(inventory),
        "total_files": len(files),
        "symbols": symbols,
        "imports": per_file_imports,
        "module_docstrings": docstrings,
        "tests": tests,
        "entry_points": [
            r for r in ("main.py", "app.py", "manage.py", "index.js", "index.ts",
                        "server.js", "server.ts", "cli.py")
            if (repo / r).exists()
        ],
    }


def _bare_name(s: str) -> str:
    s = s.strip()
    head = s.split(" — ")[0] if not s.startswith("class ") else s
    if "[" in head:
        line = head.rsplit("[", 1)[-1].rstrip("]")
    else:
        line = "?"
    if s.startswith("class "):
        name = s[len("class "):].split("(", 1)[0].split("[", 1)[0].strip()
        return f"{name}({line})"
    if s.startswith("."):
        return None  # method detail dropped
    name = head.split("(", 1)[0].strip()
    return f"{name}({line})"


def render_md(index, symbol_cap=5, summary_chars=30, edge_cap=4) -> str:
    slug = index["slug"]
    project = index["repo"]
    lines = [f"# {slug} mind map (mechanical AST pass)"]
    lines.append("")
    lines.append("## Inventory & entry points")
    for d, c in sorted(index["inventory"].items()):
        lines.append(f"- {d}: {c} files")
    lines.append(f"- TOTAL: {index['total_files']} files | {index['language_counts']}")
    for e in index["entry_points"]:
        lines.append(f"- ENTRY: {e}")
    lines.append("")
    lines.append("## Symbols (public top-level name:line)")
    for rel, syms in sorted(index["symbols"].items()):
        bare = [b for b in (_bare_name(s) for s in syms) if b]
        public = [b for b in bare if not b.split("(")[0].startswith("_")]
        if public:
            lines.append("- " + rel + ": " + ", ".join(public[:symbol_cap]))
            if len(public) > symbol_cap:
                lines.append(f"    +{len(public)-symbol_cap} more (see .json)")
    lines.append("")
    lines.append("## Module summaries (truncated)")
    for rel, doc in sorted(index["module_docstrings"].items()):
        one = " ".join(doc.split())[:summary_chars]
        lines.append(f"- {rel}: {one}")
    lines.append("")
    lines.append("## Dependency graph (internal edges)")
    proj_root = project.rstrip("/")
    for rel, imps in sorted(index["imports"].items()):
        internal = [i for i in imps if i.split(".")[0] in index["inventory"] or
                    any(rel.startswith(f"{d}/") for d in ()) ]
        if not internal:
            continue
        lines.append(f"- {rel} -> {', '.join(internal[:edge_cap])}" +
                     (" …" if len(internal) > edge_cap else ""))
    lines.append("")
    lines.append("## Test map")
    if index["tests"]:
        for t in index["tests"]:
            lines.append(f"- {t['file']} (covers: {', '.join(t['covers_hint'][:3]) or 'n/a'})")
    else:
        lines.append("- none found")
    lines.append("")
    lines.append("## Unknowns (honest limits)")
    lines.append("- Raw bodies NOT read; names parsed mechanically. Rehydrate")
    lines.append("  exact regions via the name(line) pointers above.")
    return "\n".join(lines) + "\n"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", default=os.getcwd(), help="repo root to index")
    ap.add_argument("--out", default=None,
                    help="output dir (default <repo>/memory/.codebase-minds)")
    ap.add_argument("--slug", default=None, help="slug name (default repo basename)")
    args = ap.parse_args()
    repo = Path(args.repo).resolve()
    slug = args.slug or repo.name.replace(" ", "-").lower()
    out = Path(args.out) if args.out else (repo / "memory" / ".codebase-minds")
    out.mkdir(parents=True, exist_ok=True)
    index = build(repo, slug)
    (out / f"{slug}.json").write_text(json.dumps(index, indent=2, ensure_ascii=False), encoding="utf-8")
    (out / f"{slug}.md").write_text(render_md(index), encoding="utf-8")
    print(f"wrote {out / slug}.json + {out / slug}.md "
          f"({index['total_files']} files, {len(index['symbols'])} files with symbols)")


if __name__ == "__main__":
    main()