"""Deterministic graders for the frontier-parity pilot battery (v1.0.0).

Every grader is a pure function: grade(task_id, output, context) -> (ok, note).
No model calls, no network, stdlib only. Code-execution graders run untrusted
model code under a restricted-builtins exec (parse-only safety: no imports,
no I/O builtins available).
"""

from __future__ import annotations

import base64
import binascii
import json

_SAFE_BUILTINS = {"sorted": sorted, "len": len, "range": range,
                  "abs": abs, "min": min, "max": max, "sum": sum,
                  "enumerate": enumerate, "Exception": Exception,
                  "set": set, "dict": dict, "list": list, "tuple": tuple,
                  "str": str, "int": int, "float": float, "bool": bool,
                  "zip": zip, "reversed": reversed, "all": all, "any": any,
                  "isinstance": isinstance, "type": type, "iter": iter,
                  "next": next, "StopIteration": StopIteration,
                  "ValueError": ValueError, "KeyError": KeyError,
                  "TypeError": TypeError, "IndexError": IndexError,
                  "AttributeError": AttributeError}


def _exec_fn(code: str, name: str):
    ns: dict = {}
    exec(code, {"__builtins__": _SAFE_BUILTINS}, ns)
    fn = ns.get(name)
    if not callable(fn):
        return None, f"no callable {name} defined"
    return fn, ""


def grade_r01(output: str, ctx: dict) -> tuple[bool, str]:
    return (True, "") if output.strip() == "15" else (False, f"got {output.strip()!r} want '15'")


def grade_m01(output: str, ctx: dict) -> tuple[bool, str]:
    return (True, "") if output.strip() == "333833500" else (False, f"got {output.strip()!r}")


def grade_c01(output: str, ctx: dict) -> tuple[bool, str]:
    cases = [([3, 1, 2], 2), ([1, 2, 3, 4], 2.5), ([-5, -1, -3], -3),
             ([7], 7), ([5, 5, 5, 5], 5)]
    try:
        fn, err = _exec_fn(output, "median")
        if fn is None:
            return False, err
        for args, want in cases:
            if abs(fn(list(args)) - want) > 1e-9:
                return False, f"median({args}) want {want}"
        return True, ""
    except Exception as exc:  # noqa: BLE001 - grader must not crash the matrix
        return False, f"exec/grade raised: {exc}"


def grade_d01(output: str, ctx: dict) -> tuple[bool, str]:
    cases = [([1, 3, 5, 7], 5, 2), ([1, 3, 5, 7], 1, 0),
             ([1, 3, 5, 7], 7, 3), ([1, 3, 5, 7], 4, -1),
             ([], 9, -1), ([2], 2, 0), ([2], 5, -1)]
    try:
        fn, err = _exec_fn(output, "find")
        if fn is None:
            return False, err
        for a, x, want in cases:
            if fn(list(a), x) != want:
                return False, f"find({a},{x}) want {want}"
        return True, ""
    except Exception as exc:  # noqa: BLE001
        return False, f"exec/grade raised: {exc}"


_TOPO_EDGES = [("b", "a"), ("c", "a"), ("a", "d"), ("d", "e"), ("d", "f")]


def grade_p01(output: str, ctx: dict) -> tuple[bool, str]:
    try:
        order = json.loads(output.strip())
        pos = {n: i for i, n in enumerate(order)}
        if set(pos) != {"a", "b", "c", "d", "e", "f"}:
            return False, "node set wrong"
        for u, v in _TOPO_EDGES:
            if pos[u] >= pos[v]:
                return False, f"edge {u}->{v} violated"
        return True, ""
    except Exception as exc:  # noqa: BLE001
        return False, f"bad order: {exc}"


def grade_t01(output: str, ctx: dict) -> tuple[bool, str]:
    want = str(ctx.get("fixture_total", ""))
    return (True, "") if output.strip() == want else (False, f"got {output.strip()!r} want {want!r}")


def grade_n01(output: str, ctx: dict) -> tuple[bool, str]:
    return (True, "") if output.strip() == "2026-10-09" else (False, "decode wrong")


def grade_x01(output: str, ctx: dict) -> tuple[bool, str]:
    try:
        d = json.loads(output.strip())
    except Exception as exc:  # noqa: BLE001
        return False, f"not json: {exc}"
    if not all(k in d for k in ("title", "owner", "eta")):
        return False, "keys missing"
    low = json.dumps(d).lower()
    for fact in ("paris", "berlin", "madrid"):
        if fact not in low:
            return False, f"missing {fact}"
    return True, ""


GRADERS = {
    "FP-R01": grade_r01,
    "FP-M01": grade_m01,
    "FP-C01": grade_c01,
    "FP-D01": grade_d01,
    "FP-P01": grade_p01,
    "FP-T01": grade_t01,
    "FP-N01": grade_n01,
    "FP-X01": grade_x01,
}


def grade(task_id: str, output: str, ctx: dict | None = None) -> tuple[bool, str]:
    fn = GRADERS.get(task_id)
    if fn is None:
        return False, f"no grader registered for {task_id} (sealed or unknown)"
    return fn(output or "", ctx or {})


# ---------------------------------------------------------------------------
# v1.1 dual scoring: value_ok (capability) vs format_ok (instruction compliance).
# Strict ok = value_ok AND format_ok (unchanged bar for verdicts). Repair notes
# now distinguish VALUE_WRONG from VALUE_OK_FORMAT_BAD so repair loops stop
# wasting calls on correctly-computed answers wrapped in chatter.
# ---------------------------------------------------------------------------

def _format_ok(raw: str, normalized: str, ctx: dict, changed: bool | None = None) -> bool:
    """Channel-aware format rule. Chat channel: reply must BE the artifact.
    result_json channel: the file content must need no extraction (narration
    may say anything — that is the separation working as designed)."""
    if (ctx or {}).get("channel") == "result_json":
        if changed is None:
            changed = (normalized or "").strip() != (normalized or "").strip()
        return not changed
    return (raw or "").strip() == (normalized or "").strip()


def _split_value(task_id: str, norm_s: str, ctx: dict) -> tuple[bool, str]:
    """Value-only check for v1 tasks. Returns (value_ok, want_description)."""
    if task_id == "FP-R01":
        return ("15" in norm_s, "'15'")
    if task_id == "FP-M01":
        return ("333833500" in norm_s, "'333833500'")
    if task_id == "FP-T01":
        want = str(ctx.get("fixture_total", ""))
        return (bool(want) and want in norm_s, repr(want))
    if task_id == "FP-N01":
        return ("2026-10-09" in norm_s, "'2026-10-09'")
    ok, note = grade(task_id, norm_s, ctx)
    return (ok, f"grader:{note}" if not ok else "grader-pass")


def grade2(task_id: str, raw: str, normalized: str,
           ctx: dict | None = None, changed: bool = False) -> tuple[bool, bool, str]:
    """Returns (value_ok, format_ok, note). Pure function, no model, no network.

    `changed` = whether mechanical normalization altered the graded candidate
    (caller-computed). Format is channel-aware via _format_ok.
    """
    ctx = ctx or {}
    raw_s, norm_s = (raw or "").strip(), (normalized or "").strip()
    v_ok, _want = _split_value(task_id, norm_s, ctx)
    if not v_ok:
        return False, False, f"VALUE_WRONG: want {_want}"
    f_ok = _format_ok(raw_s, norm_s, ctx, changed)
    if f_ok:
        return True, True, ""
    if ctx.get("channel") == "result_json":
        return True, False, ("VALUE_OK_FORMAT_BAD: RESULT.json content needed "
                             "extraction; write the bare artifact")
    return True, False, "VALUE_OK_FORMAT_BAD: correct artifact wrapped in extra text"


def repair_note_for(task_id: str, raw: str, normalized: str,
                    ctx: dict | None = None) -> str:
    v_ok, f_ok, note = grade2(task_id, raw, normalized, ctx)
    if v_ok and not f_ok:
        return ("grader: VALUE_OK_FORMAT_BAD — the computed value/artifact is correct, "
                "but the reply wraps it in extra prose. Reply with ONLY the requested artifact.")
    return f"grader: {note}"


# ---------------------------------------------------------------------------
# v2 generic graders (full battery): driven by task params, no hardcoded answers.
# Expected values travel in ctx (computed by fixtures.py at run time), never in
# prompts. kinds: exact | exec | order | jsonfacts | filemodule | fileset
# ---------------------------------------------------------------------------

def _want_of(ctx: dict) -> str:
    # expected_key takes PRECEDENCE: fixtures always carry an `expected`
    # (their own contract), which must not shadow the task's pinned key.
    key = ctx.get("expected_key")
    if isinstance(key, str) and key and key in ctx:
        return str(ctx[key])
    return str(ctx.get("expected", ""))


def grade_exact_ctx(output: str, ctx: dict) -> tuple[bool, str]:
    want = _want_of(ctx)
    return (True, "") if output.strip() == want else (False, f"got {output.strip()[:80]!r}")


def _value_present(want: str, norm: str) -> bool:
    """Numeric expectations match whole tokens only ('15' not found in '150');
    non-numeric expectations match as substrings."""
    import re as _re
    if not want:
        return False
    if _re.fullmatch(r"-?\d+(?:\.\d+)?", want):
        return _re.search(r"(?<!\d)" + _re.escape(want) + r"(?!\d)", norm) is not None
    return want in norm


def grade_exact_dual(raw: str, output: str, ctx: dict) -> tuple[bool, bool, bool, str]:
    """Value/format split for exact tasks: value = expected present in the
    normalized candidate (token-aware for numbers); format = channel-aware.
    Returns (strict_ok, value_ok, format_ok, note)."""
    ctx = ctx or {}
    want = _want_of(ctx)
    norm = (output or "").strip()
    changed = ctx.get("candidate_changed")
    if changed is None:
        changed = (raw or "").strip() != norm
    v_ok = _value_present(want, norm)
    # Format for exact tasks = the graded candidate IS EXACTLY the artifact.
    # (No extraction is defined for exact tasks, so `changed` is irrelevant;
    # the result_json channel wins by selecting the file as the candidate.)
    if norm == want:
        return True, True, True, ""
    if v_ok:
        if ctx.get("channel") == "result_json":
            return False, True, False, ("VALUE_OK_FORMAT_BAD: RESULT.json content "
                                        "is not exactly the artifact; write only it")
        return False, True, False, "VALUE_OK_FORMAT_BAD: correct value wrapped in extra text"
    return False, False, False, f"VALUE_WRONG: got {norm[:80]!r}"


def grade_exec_ctx(output: str, ctx: dict) -> tuple[bool, str]:
    """ctx: {func: name, cases: [[args_list, want], ...], float_tol}."""
    name = ctx.get("func", "solve")
    tol = float(ctx.get("float_tol", 1e-9))
    try:
        fn, err = _exec_fn(output, name)
        if fn is None:
            return False, err
        for args, want in ctx.get("cases", []):
            got = fn(*[list(a) if isinstance(a, list) else a for a in args])
            if isinstance(want, float) or isinstance(got, float):
                if abs(float(got) - float(want)) > tol:
                    return False, f"{name}({args}) want {want}"
            elif got != want:
                return False, f"{name}({args}) want {want}"
        return True, ""
    except Exception as exc:  # noqa: BLE001
        return False, f"exec/grade raised: {exc}"


def grade_order_ctx(output: str, ctx: dict) -> tuple[bool, str]:
    """ctx: {nodes: [...], edges: [[u,v],...]} — any valid topological order."""
    try:
        order = json.loads(output.strip())
        pos = {n: i for i, n in enumerate(order)}
        if set(pos) != set(ctx.get("nodes", [])):
            return False, "node set wrong"
        for u, v in ctx.get("edges", []):
            if pos[u] >= pos[v]:
                return False, f"edge {u}->{v} violated"
        return True, ""
    except Exception as exc:  # noqa: BLE001
        return False, f"bad order: {exc}"


def grade_jsonfacts_ctx(output: str, ctx: dict) -> tuple[bool, str]:
    """ctx: {keys: [...], facts: [...lowercase substrings required in values...]}."""
    try:
        d = json.loads(output.strip())
    except Exception as exc:  # noqa: BLE001
        return False, f"not json: {exc}"
    for k in ctx.get("keys", []):
        if k not in d:
            return False, f"key missing: {k}"
    low = json.dumps(d, ensure_ascii=False).lower()
    for fact in ctx.get("facts", []):
        if str(fact).lower() not in low:
            return False, f"missing {fact}"
    return True, ""


def grade_filemodule_ctx(files: dict, ctx: dict) -> tuple[bool, str]:
    """Grade a module the agent wrote into the workdir. files: {name: content}."""
    name = ctx.get("file", "")
    content = (files or {}).get(name, "")
    if not content:
        return False, f"file {name} missing/empty"
    return grade_exec_ctx(content, ctx)


def _resolve_refs(items: list, ctx: dict) -> list:
    """'$key' entries resolve against ctx (runtime-computed expectations);
    list values expand to their items."""
    out = []
    for s in items or []:
        if isinstance(s, str) and s.startswith("$"):
            v = ctx.get(s[1:], "")
            if isinstance(v, list):
                out.extend(str(x) for x in v)
            else:
                out.append(str(v))
        else:
            out.append(s)
    return out


def grade_fileset_ctx(files: dict, ctx: dict) -> tuple[bool, str]:
    """ctx: {required: [...], contains: {name: [...]}, contains_ctx: {name: ['$key', ...]}}."""
    for name in ctx.get("required", []):
        if name not in (files or {}):
            return False, f"file missing: {name}"
    for name, subs in (ctx.get("contains", {}) or {}).items():
        body = (files or {}).get(name, "")
        for s in subs:
            if s.lower() not in body.lower():
                return False, f"{name} lacks {s!r}"
    for name, refs in (ctx.get("contains_ctx", {}) or {}).items():
        body = (files or {}).get(name, "")
        for s in _resolve_refs(refs, ctx):
            if not s or s.lower() not in body.lower():
                return False, f"{name} lacks ctx value {s!r}"
    return True, ""


def grade_filejson_ctx(files: dict, ctx: dict) -> tuple[bool, str]:
    """Grade a JSON document the agent wrote into the workdir.
    ctx: {file, keys: [...], facts: [...], facts_ctx: [...], pairs: {k: '$ref'|literal}}."""
    name = ctx.get("file", "")
    content = (files or {}).get(name, "")
    if not content:
        return False, f"file {name} missing/empty"
    try:
        d = json.loads(content.strip())
    except Exception as exc:  # noqa: BLE001
        return False, f"{name} not json: {exc}"
    for k in ctx.get("keys", []):
        if k not in d:
            return False, f"key missing: {k}"
    low = json.dumps(d, ensure_ascii=False).lower()
    for fact in list(ctx.get("facts", [])) + _resolve_refs(ctx.get("facts_ctx", []), ctx):
        if str(fact).lower() not in low:
            return False, f"missing {fact}"
    for k, ref in (ctx.get("pairs", {}) or {}).items():
        want = ctx.get(ref[1:], ref) if isinstance(ref, str) and ref.startswith("$") else ref
        if d.get(k) != want:
            return False, f"pair {k} want {want!r}"
    return True, ""


GENERIC = {"exact": grade_exact_ctx, "exec": grade_exec_ctx,
           "order": grade_order_ctx, "jsonfacts": grade_jsonfacts_ctx}


FILE_GRADERS = {"filemodule": grade_filemodule_ctx, "fileset": grade_fileset_ctx,
                "filejson": grade_filejson_ctx}


def grade_generic(kind: str, output: str, ctx: dict) -> tuple[bool, str]:
    fn = GENERIC.get(kind)
    if fn is None:
        return False, f"unknown generic grader kind {kind}"
    return fn(output or "", ctx or {})
