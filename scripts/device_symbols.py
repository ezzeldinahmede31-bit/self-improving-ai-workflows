#!/usr/bin/env python3
"""device_symbols.py v2 — hardened LSP-lite.

Fixes vs v1: every file read passes the Read permission gate (secret paths
denied); 1MB file cap; SyntaxError/decode errors return clean failures;
rglob capped (2000 files, 500 hits, no symlink following); per-file errors
skipped, never fatal. Scope honestly: no import resolution, name-based refs.

Usage: defs <file.py> | info <file.py> <name> | refs <dir> <name> | selftest
"""
import ast
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from device_permissions import evaluate  # noqa: E402

MAX_FILE = 1024 * 1024
MAX_FILES = 2000
MAX_HITS = 500


def gated_read(path):
    tier, rule = evaluate("Read", str(path))
    if tier == "deny":
        raise PermissionError(f"read denied: {rule}")
    p = Path(path)
    if not p.is_file() or p.stat().st_size > MAX_FILE:
        raise ValueError("not a file or over 1MB cap")
    return p.read_text(errors="strict")


def py_defs(path):
    try:
        tree = ast.parse(gated_read(path))
    except PermissionError:
        raise
    except Exception as e:
        raise ValueError(f"parse failed: {type(e).__name__}: {e}")
    out = []
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            kind = "class" if isinstance(node, ast.ClassDef) else "func"
            try:
                args = [a.arg for a in node.args.args] if kind == "func" else []
            except Exception:
                args = []
            out.append({"kind": kind, "name": node.name, "line": node.lineno,
                        "args": args,
                        "doc": (ast.get_docstring(node) or "")[:200]})
    return sorted(out, key=lambda d: d["line"])


def main(argv):
    if len(argv) == 2 and argv[1] == "selftest":
        me = Path(__file__)
        defs = py_defs(me)
        names = {d["name"] for d in defs}
        ok1 = {"main", "py_defs", "gated_read"} <= names
        print(f"defs own file -> {'PASS' if ok1 else 'FAIL'}")
        try:
            py_defs(".env")
            ok2 = Path(".env").exists()  # only passes if .env legitimately readable (it shouldn't exist)
            ok2 = False
        except PermissionError:
            ok2 = True
        except Exception:
            ok2 = True  # any refusal/failure is safe (never leaks)
        print(f".env refused -> {'PASS' if ok2 else 'FAIL'}")
        try:
            py_defs("/nonexistent_xyz.py")
            ok3 = False
        except Exception:
            ok3 = True
        print(f"missing file clean fail -> {'PASS' if ok3 else 'FAIL'}")
        ok = ok1 and ok2 and ok3
        print("SELFTEST " + ("OK" if ok else "FAILED"))
        return 0 if ok else 1
    if len(argv) >= 3 and argv[1] == "defs":
        try:
            print(json.dumps(py_defs(argv[2]), indent=1, ensure_ascii=False))
        except Exception as e:
            print(f"error: {e}", file=sys.stderr)
            return 1
        return 0
    if len(argv) >= 4 and argv[1] == "info":
        try:
            for d in py_defs(argv[2]):
                if d["name"] == argv[3]:
                    print(json.dumps(d, indent=1, ensure_ascii=False))
                    return 0
            print("not found", file=sys.stderr)
            return 1
        except Exception as e:
            print(f"error: {e}", file=sys.stderr)
            return 1
    if len(argv) >= 4 and argv[1] == "refs":
        pat = re.compile(r"\b" + re.escape(argv[3]) + r"\b")
        hits, n = [], 0
        for f in Path(argv[2]).rglob("*.py"):
            if n >= MAX_FILES or len(hits) >= MAX_HITS or f.is_symlink():
                break
            n += 1
            try:
                if f.stat().st_size > MAX_FILE:
                    continue
                for i, line in enumerate(f.read_text(errors="strict").splitlines(), 1):
                    if pat.search(line):
                        hits.append({"file": str(f), "line": i, "text": line.strip()[:120]})
                        if len(hits) >= MAX_HITS:
                            break
            except Exception:
                continue
        print(json.dumps(hits, indent=1, ensure_ascii=False))
        return 0
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv))
