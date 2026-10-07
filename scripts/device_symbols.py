#!/usr/bin/env python3
"""device_symbols.py — LSP-lite: code intelligence without a language server.

Uses stdlib `ast` for Python (definitions, docstrings, call references via
name matching) and falls back to regex scanning for other text files.
Honest scope: single-file-accurate, workspace-approximate for references
(a real LSP server resolves imports/types; this does not claim that).

Usage:
  device_symbols.py defs <file.py>              # functions/classes + lines
  device_symbols.py info <file.py> <name>       # docstring + signature-ish
  device_symbols.py refs <dir> <name>           # files+lines mentioning name
  device_symbols.py selftest
"""
import ast
import json
import re
import sys
from pathlib import Path


def py_defs(path):
    tree = ast.parse(Path(path).read_text())
    out = []
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            kind = "class" if isinstance(node, ast.ClassDef) else "func"
            args = [a.arg for a in node.args.args] if kind == "func" else []
            out.append({"kind": kind, "name": node.name, "line": node.lineno,
                        "args": args,
                        "doc": (ast.get_docstring(node) or "")[:200]})
    return sorted(out, key=lambda d: d["line"])


def cmd_defs(path):
    print(json.dumps(py_defs(path), indent=1, ensure_ascii=False))
    return 0


def cmd_info(path, name):
    for d in py_defs(path):
        if d["name"] == name:
            print(json.dumps(d, indent=1, ensure_ascii=False))
            return 0
    print(f"symbol {name!r} not defined in {path}", file=sys.stderr)
    return 1


def cmd_refs(directory, name):
    pat = re.compile(r"\b" + re.escape(name) + r"\b")
    hits = []
    for f in Path(directory).rglob("*.py"):
        try:
            for i, line in enumerate(f.read_text().splitlines(), 1):
                if pat.search(line):
                    hits.append({"file": str(f), "line": i,
                                 "text": line.strip()[:120]})
        except Exception:
            pass
    print(json.dumps(hits, indent=1, ensure_ascii=False))
    return 0


def main(argv):
    if len(argv) == 2 and argv[1] == "selftest":
        me = Path(__file__)
        defs = py_defs(me)
        names = {d["name"] for d in defs}
        ok1 = {"cmd_defs", "cmd_info", "cmd_refs", "main"} <= names
        print(f"defs finds own functions -> {'PASS' if ok1 else 'FAIL'} ({sorted(names)})")
        info = [d for d in defs if d["name"] == "cmd_refs"][0]
        ok2 = info["line"] > 0 and isinstance(info["args"], list)
        print(f"info has line+args -> {'PASS' if ok2 else 'FAIL'}")
        import subprocess
        r = subprocess.run([sys.executable, __file__, "refs", "scripts", "cmd_poll"],
                           capture_output=True, text=True)
        hits = json.loads(r.stdout or "[]")
        ok3 = any("device_monitor" in h["file"] for h in hits)
        print(f"refs finds cross-file use -> {'PASS' if ok3 else 'FAIL'} ({len(hits)} hits)")
        ok = ok1 and ok2 and ok3
        print("SELFTEST " + ("OK" if ok else "FAILED"))
        return 0 if ok else 1
    if len(argv) >= 3 and argv[1] == "defs":
        return cmd_defs(argv[2])
    if len(argv) >= 4 and argv[1] == "info":
        return cmd_info(argv[2], argv[3])
    if len(argv) >= 4 and argv[1] == "refs":
        return cmd_refs(argv[2], argv[3])
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv))
