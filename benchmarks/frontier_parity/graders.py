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
                  "enumerate": enumerate, "Exception": Exception}


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
