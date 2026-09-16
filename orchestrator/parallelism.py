"""Maximum Safe Parallelism: expose real parallelism, never invent it.

- Splits happen ONLY for explicitly declared, file-disjoint tasks whose
  acceptance partitions cleanly. Anything else runs whole (refusal is safe).
- Metrics come from explicit per-task `estimate_s` (labeled ESTIMATE) and
  from store event timestamps (labeled MEASURED).
"""
from __future__ import annotations
import math

from . import dag as dag_mod

DEFAULT_ESTIMATE_S = 60


def _estimate(c: dict) -> float:
    try:
        return max(1.0, float(c.get("estimate_s", DEFAULT_ESTIMATE_S)))
    except (TypeError, ValueError):
        return float(DEFAULT_ESTIMATE_S)


def split_safety(contract: dict) -> tuple[bool, str]:
    """Check whether a declared split is SAFE. Returns (ok, reason)."""
    if not contract.get("splittable"):
        return False, "not-declared-splittable"
    if contract.get("split_by") != "files":
        return False, "only-file-splits-supported"
    groups = contract.get("file_groups") or []
    allowed = contract.get("allowed_files", [])
    if len(groups) < 2:
        return False, "need-2+-file-groups"
    flat = [f for g in groups for g in [g] for f in g]
    if sorted(flat) != sorted(allowed) or len(set(flat)) != len(flat):
        return False, "groups-must-partition-allowed_files-disjointly"
    for i, item in enumerate(contract.get("acceptance", [])):
        if not isinstance(item, dict):
            return False, f"acceptance[{i}]-not-a-dict"
        path = item.get("path")
        if not path:
            return False, f"acceptance[{i}]-has-no-path"
        owners = [gi for gi, g in enumerate(groups) if path in g]
        if len(owners) != 1:
            return False, f"acceptance[{i}]-cross-group-or-unknown-path"
    out_keys = contract.get("outputs", [])
    if out_keys:
        return False, "outputs-must-be-empty-for-split (use files)"
    return True, "safe"


def split_contract(contract: dict) -> list[dict]:
    """Split a SAFE contract into sub-contracts. Raises if unsafe."""
    ok, reason = split_safety(contract)
    if not ok:
        raise ValueError(f"unsafe split for {contract.get('task_id')}: {reason}")
    tid = contract["task_id"]
    groups: list[list[str]] = contract["file_groups"]
    n = len(groups)
    per = math.ceil(float(_estimate(contract)) / n)
    subs = []
    for i, files in enumerate(groups):
        sub = dict(contract)
        sub["task_id"] = f"{tid}#{i + 1}"
        sub["goal"] = f"{contract.get('goal')} [part {i + 1}/{n}: {', '.join(files)}]"
        sub["allowed_files"] = list(files)
        sub["file_groups"] = []
        sub["splittable"] = False
        sub["acceptance"] = [a for a in contract.get("acceptance", [])
                             if a.get("path") in files]
        sub["estimate_s"] = per
        sub["split_from"] = tid
        subs.append(sub)
    return subs


def optimize(contracts: list[dict]) -> tuple[list[dict], dict]:
    """Rewrite safe-splittable tasks; rewire dependents. Returns (new, report)."""
    by_id = {c["task_id"]: c for c in contracts}
    out: list[dict] = []
    report = {"split": [], "refused": []}
    rewrites: dict[str, list[str]] = {}
    for c in contracts:
        if c.get("splittable"):
            ok, reason = split_safety(c)
            if ok:
                subs = split_contract(c)
                rewrites[c["task_id"]] = [s["task_id"] for s in subs]
                out.extend(subs)
                report["split"].append({"task_id": c["task_id"],
                                        "into": rewrites[c["task_id"]]})
                continue
            report["refused"].append({"task_id": c["task_id"],
                                      "reason": reason})
        out.append(c)
    for c in out:
        deps = c.get("dependencies", [])
        new_deps: list[str] = []
        for d in deps:
            new_deps.extend(rewrites.get(d, [d]))
        c["dependencies"] = new_deps
    return out, report


def critical_path(contracts: list[dict]) -> tuple[list[str], float]:
    edges = dag_mod.build_edges(contracts)
    dur = {c["task_id"]: _estimate(c) for c in contracts}
    best: dict[str, tuple[float, list[str]]] = {}

    def longest(n: str, seen: frozenset = frozenset()) -> tuple[float, list[str]]:
        if n in best:
            return best[n]
        if n in seen:
            raise ValueError(f"cycle at {n}")
        preds = sorted(edges.get(n, ()))
        if not preds:
            best[n] = (dur.get(n, 0.0), [n])
        else:
            pl, pp = max((longest(p, seen | {n}) for p in preds),
                         key=lambda t: t[0])
            best[n] = (pl + dur.get(n, 0.0), pp + [n])
        return best[n]

    if not contracts:
        return [], 0.0
    return max((longest(c["task_id"]) for c in contracts), key=lambda t: t[0])


def project_metrics(contracts: list[dict]) -> dict:
    edges = dag_mod.build_edges(contracts)
    levels = dag_mod.levels(edges)
    path, length = critical_path(contracts)
    total = sum(_estimate(c) for c in contracts)
    width = max((len(lv) for lv in levels), default=0)
    return {"total_work_estimate_s": total,
            "critical_path": path, "critical_path_length_s": length,
            "max_safe_parallelism": width,
            "theoretical_min_runtime_s": length,
            "levels": levels, "task_count": len(contracts)}
