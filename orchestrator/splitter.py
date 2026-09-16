"""Safe-Split Optimizer: cohesion-aware task partitioning.

Answers deterministically: can this task be split into smaller tasks that
run safely in parallel? Verdicts: SAFE_SPLIT / UNSAFE_SPLIT / DEFERRED_REVIEW,
each with evidence. Never splits on file-count alone.

Signals used (all observable, no LLM judgment):
  - declared file_groups + partitioned acceptance (strongest evidence)
  - import graph parsed from existing repo files (ast, stdlib only)
  - test<->source name pairing (test boundaries)
  - hub files (high fan-in within the set -> serialization risk)
  - shared-state signals (config/schema/migration/env names, outputs,
    path-less acceptance items)
Cost model: split only when estimated makespan gain clearly exceeds
coordination cost; otherwise UNSAFE_SPLIT (economics). Missing files or
unresolvable structure -> DEFERRED_REVIEW, never a guess.
"""
from __future__ import annotations
import ast
import math
import os
import re

from . import dag as dag_mod

SHARED_PATTERNS = [r"^config", r"\.env$", r"schema", r"migration",
                   r"__init__\.py$", r"settings", r"conftest"]
_SHARED_RE = re.compile("|".join(f"(?:{p})" for p in SHARED_PATTERNS),
                        re.IGNORECASE)
MIN_GAIN_S = 10.0
CROSS_EDGE_COST_S = 5.0
SUBTASK_OVERHEAD_S = 5.0


def _test_pair(a: str, b: str) -> bool:
    base = lambda p: os.path.splitext(os.path.basename(p))[0]
    x, y = base(a), base(b)
    return x == "test_" + y or y == "test_" + x or \
        x.removeprefix("test_") == y.removeprefix("test_")


def parse_imports(path: str) -> set[str]:
    """Module basenames imported by a Python file (stdlib ast)."""
    try:
        with open(path, encoding="utf-8", errors="ignore") as fh:
            tree = ast.parse(fh.read())
    except (OSError, SyntaxError, ValueError):
        return set()
    out: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            out.update(a.name.split(".")[0] for a in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            out.add(node.module.split(".")[0])
    return out


def analyze_contract(contract: dict, repo_root: str | None = None) -> dict:
    files = list(contract.get("allowed_files", []))
    imports: dict[str, set[str]] = {}
    if repo_root:
        for f in files:
            p = os.path.join(repo_root, f)
            imports[f] = parse_imports(p) if os.path.isfile(p) else set()
    else:
        imports = {f: set() for f in files}
    basenames = {f: os.path.splitext(os.path.basename(f))[0] for f in files}
    coupling: dict[tuple[str, str], int] = {}
    for i, a in enumerate(files):
        for b in files[i + 1:]:
            score = 0
            if basenames[b] in imports.get(a, set()) or \
               basenames[a] in imports.get(b, set()):
                score += 3
            if os.path.dirname(a) == os.path.dirname(b):
                score += 1
            if _test_pair(a, b):
                score += 2
            if score:
                coupling[(a, b)] = score
    fan_in = {f: 0 for f in files}
    for (a, b), s in coupling.items():
        if s >= 3:
            fan_in[a] += 1
            fan_in[b] += 1
    hubs = sorted(f for f, n in fan_in.items() if n >= 2)
    shared = sorted(f for f in files if _SHARED_RE.search(os.path.basename(f)))
    missing = [] if not repo_root else sorted(
        f for f in files if not os.path.isfile(os.path.join(repo_root, f)))
    return {"task_id": contract.get("task_id"), "files": files,
            "coupling": coupling, "hubs": hubs, "shared_state_files": shared,
            "missing_files": missing,
            "estimate_s": float(contract.get("estimate_s", 60))}


def _partition_greedy(files: list[str],
                      coupling: dict[tuple[str, str], int]) -> list[list[str]]:
    """Greedy cut: keep coupled files together, isolate the rest."""
    parent = {f: f for f in files}

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    def union(a, b):
        ra, rb = find(a), find(b)
        if ra != rb:
            parent[rb] = ra

    for (a, b), s in sorted(coupling.items(), key=lambda kv: -kv[1]):
        if s >= 3:
            union(a, b)
    groups: dict[str, list[str]] = {}
    for f in files:
        groups.setdefault(find(f), []).append(f)
    parts = [sorted(g) for g in groups.values()]
    parts.sort(key=lambda g: g[0])
    return parts


def _acceptance_by_path(contract: dict) -> tuple[dict[str, list[dict]], list[str]]:
    by_path: dict[str, list[dict]] = {}
    bad: list[str] = []
    for i, item in enumerate(contract.get("acceptance", [])):
        if not isinstance(item, dict) or not item.get("path"):
            bad.append(f"acceptance[{i}]-no-path")
            continue
        by_path.setdefault(item["path"], []).append(item)
    return by_path, bad


def decide(contract: dict, repo_root: str | None = None) -> dict:
    """Return a split decision with evidence. Never guesses."""
    tid = contract.get("task_id")
    files = list(contract.get("allowed_files", []))
    base_ev = {"original_task": tid, "files": files,
               "estimate_s": float(contract.get("estimate_s", 60))}
    if len(files) < 2:
        return {"verdict": "UNSAFE_SPLIT", "reason": "single-file-task",
                "evidence": base_ev}
    if contract.get("outputs"):
        return {"verdict": "UNSAFE_SPLIT",
                "reason": "task-produces-shared-outputs",
                "evidence": {**base_ev, "outputs": contract["outputs"]}}
    by_path, bad = _acceptance_by_path(contract)
    if bad:
        return {"verdict": "UNSAFE_SPLIT",
                "reason": "acceptance-not-partitionable",
                "evidence": {**base_ev, "problems": bad}}
    declared = contract.get("file_groups") or []
    analysis = analyze_contract(contract, repo_root)
    if analysis["shared_state_files"]:
        return {"verdict": "UNSAFE_SPLIT", "reason": "shared-state-files",
                "evidence": {**base_ev,
                             "shared": analysis["shared_state_files"]}}
    for path in by_path:
        owners = [g for g in (declared or [files]) if path in g]
        if len(owners) != 1 and not declared:
            pass  # greedy path below re-checks per partition
    if declared:
        flat = [f for g in declared for f in g]
        if sorted(flat) != sorted(files) or len(set(flat)) != len(flat):
            return {"verdict": "UNSAFE_SPLIT",
                    "reason": "declared-groups-dont-partition-files",
                    "evidence": base_ev}
        parts = [sorted(g) for g in declared]
    elif analysis["missing_files"]:
        return {"verdict": "DEFERRED_REVIEW",
                "reason": "files-not-in-repo-cannot-analyze-coupling",
                "evidence": {**base_ev,
                             "missing": analysis["missing_files"]}}
    else:
        parts = _partition_greedy(files, analysis["coupling"])
    if len(parts) < 2:
        return {"verdict": "UNSAFE_SPLIT", "reason": "no-clean-cut-coupling",
                "evidence": {**base_ev, "coupling": len(analysis["coupling"])}}
    # acceptance must sit inside exactly one partition
    for path in by_path:
        if sum(1 for p in parts if path in p) != 1:
            return {"verdict": "UNSAFE_SPLIT",
                    "reason": "acceptance-crosses-partitions",
                    "evidence": {**base_ev, "path": path}}
    cross = sum(1 for (a, b) in analysis["coupling"]
                if not any(a in p and b in p for p in parts))
    n = len(parts)
    part_est = [base_ev["estimate_s"] * len(p) / len(files) for p in parts]
    gain = base_ev["estimate_s"] - max(part_est)
    cost = cross * CROSS_EDGE_COST_S + n * SUBTASK_OVERHEAD_S
    if gain < MIN_GAIN_S or gain <= cost:
        return {"verdict": "UNSAFE_SPLIT", "reason": "coordination-exceeds-gain",
                "evidence": {**base_ev, "gain_s": round(gain, 1),
                             "cost_s": round(cost, 1)}}
    subs = []
    for i, part in enumerate(parts):
        acc = [a for p in part for a in by_path.get(p, [])]
        subs.append({"task_id": f"{tid}#{i + 1}", "files": part,
                     "acceptance_ids": [a.get("id") for a in acc],
                     "estimate_s": round(part_est[i], 1)})
    return {"verdict": "SAFE_SPLIT",
            "evidence": {**base_ev, "generated_subtasks": subs,
                         "cross_edges": cross,
                         "gain_s": round(gain, 1), "cost_s": round(cost, 1),
                         "hubs": analysis["hubs"],
                         "qa_requirements": "each subtask keeps its path-scoped "
                         "acceptance; parent acceptance fully partitioned",
                         "rollback": "re-run original contract whole"}} | {
            "generated_subtasks": subs, "partitions": parts,
            "gain_s": round(gain, 1), "cost_s": round(cost, 1),
            "reason": "clean-file-cut-gain-exceeds-cost"}


def apply_split(contract: dict, decision: dict) -> list[dict]:
    if decision.get("verdict") != "SAFE_SPLIT":
        raise ValueError("only SAFE_SPLIT decisions apply")
    tid = contract.get("task_id")
    by_path, _ = _acceptance_by_path(contract)
    out = []
    for i, sub in enumerate(decision["generated_subtasks"]):
        part = sub["files"]
        c = dict(contract)
        c["task_id"] = sub["task_id"]
        c["goal"] = (f"{contract.get('goal')} "
                     f"[split part {i + 1}: {', '.join(part)}]")
        c["allowed_files"] = list(part)
        c["file_groups"] = []
        c["splittable"] = False
        c["acceptance"] = [a for p in part for a in by_path.get(p, [])]
        c["estimate_s"] = max(1, int(round(sub["estimate_s"])))
        c["split_from"] = tid
        out.append(c)
    return out


def optimize_project(contracts: list[dict],
                     repo_root: str | None = None) -> tuple[list[dict], dict]:
    """Split SAFE tasks, rewire dependents, rebuild + verify the DAG."""
    before = _metrics(contracts)
    out: list[dict] = []
    decisions = []
    rewrites: dict[str, list[str]] = {}
    for c in contracts:
        if c.get("splittable"):
            d = decide(c, repo_root)
            decisions.append({"task_id": c["task_id"],
                              "verdict": d["verdict"],
                              "reason": d.get("reason"),
                              "gain_s": d.get("gain_s", 0.0),
                              "cost_s": d.get("cost_s", 0.0)})
            if d["verdict"] == "SAFE_SPLIT":
                subs = apply_split(c, d)
                rewrites[c["task_id"]] = [s["task_id"] for s in subs]
                out.extend(subs)
                continue
        out.append(c)
    for c in out:
        c["dependencies"] = [x for d in c.get("dependencies", [])
                             for x in rewrites.get(d, [d])]
    edges = dag_mod.build_edges(out)
    cycle = dag_mod.detect_cycle(edges)
    after = _metrics(out)
    report = {"decisions": decisions,
              "rewrites": rewrites,
              "cycle": cycle,
              "metrics_before": before,
              "metrics_after": after,
              "makespan_gain_s": round(before["critical_path_s"] -
                                       after["critical_path_s"], 1)}
    if cycle:
        raise ValueError(f"split produced a cycle: {cycle}")
    return out, report


def _metrics(contracts: list[dict]) -> dict:
    edges = dag_mod.build_edges(contracts)
    levels = dag_mod.levels(edges)
    dur = {c["task_id"]: float(c.get("estimate_s", 60)) for c in contracts}
    longest: dict[str, float] = {}
    for lv in levels:
        for node in lv:
            preds = edges.get(node, set())
            longest[node] = dur.get(node, 60.0) + max(
                [longest.get(p, 0.0) for p in preds] or [0.0])
    return {"tasks": len(contracts),
            "total_work_s": round(sum(dur.values()), 1),
            "critical_path_s": round(max(longest.values()) if longest else 0.0, 1),
            "max_width": max((len(lv) for lv in levels), default=0),
            "levels": len(levels)}
