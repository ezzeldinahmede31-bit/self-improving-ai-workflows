"""DAG construction: explicit dependencies + automatic file-overlap edges.

Two tasks writing the same file NEVER run in parallel: an edge is added
deterministically (sorted task-id order) so the merge stays safe.
"""
from __future__ import annotations


def build_edges(contracts: list[dict]) -> dict[str, set[str]]:
    edges: dict[str, set[str]] = {}
    for c in contracts:
        edges[c["task_id"]] = set(c.get("dependencies", []))
    writers: dict[str, str] = {}
    for c in sorted(contracts, key=lambda x: x["task_id"]):
        tid = c["task_id"]
        for f in c.get("allowed_files", []):
            if f in writers and writers[f] != tid:
                edges[tid].add(writers[f])
            writers[f] = tid
    return edges


def detect_cycle(edges: dict[str, set[str]]) -> list[str] | None:
    WHITE, GRAY, BLACK = 0, 1, 2
    color = {n: WHITE for n in edges}
    stack: list[str] = []

    def visit(n: str) -> list[str] | None:
        color[n] = GRAY
        stack.append(n)
        for m in sorted(edges.get(n, ())):
            if m not in color:
                continue
            if color[m] == GRAY:
                return stack[stack.index(m):] + [m]
            if color[m] == WHITE:
                hit = visit(m)
                if hit:
                    return hit
        stack.pop()
        color[n] = BLACK
        return None

    for n in sorted(edges):
        if color[n] == WHITE:
            hit = visit(n)
            if hit:
                return hit
    return None


def levels(edges: dict[str, set[str]]) -> list[list[str]]:
    """Kahn layering: each level runs fully in parallel. Raises on cycle."""
    deps = {n: set(v) for n, v in edges.items()}
    done: set[str] = set()
    out: list[list[str]] = []
    while deps:
        ready = sorted(n for n, v in deps.items() if v <= done)
        if not ready:
            raise ValueError(f"dependency cycle or missing dep: {sorted(deps)}")
        out.append(ready)
        for n in ready:
            del deps[n]
        done.update(ready)
    return out
