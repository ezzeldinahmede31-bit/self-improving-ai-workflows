"""Dashboard: read-only snapshot + text render. Never writes to the store."""
from __future__ import annotations

from .state import StateStore


def snapshot(store: StateStore, project_id: str) -> dict:
    tasks = store.list_tasks(project_id)
    counts: dict[str, int] = {}
    rows = []
    for t in tasks:
        counts[t["status"]] = counts.get(t["status"], 0) + 1
        c = t["contract"]
        rows.append({
            "task_id": t["task_id"], "role": t["role"], "status": t["status"],
            "attempts": t["attempts"],
            "deps": c.get("dependencies", []),
            "changed": (t["summary"] or {}).get("changed", []),
        })
    rows.sort(key=lambda r: r["task_id"])
    return {"project_id": project_id, "counts": counts, "tasks": rows,
            "events": store.recent_events(project_id, 15)}


def render_text(snap: dict) -> str:
    lines = [f"project {snap['project_id']} counts={snap['counts']}"]
    for r in snap["tasks"]:
        lines.append(
            f"  [{r['status']:10s}] {r['task_id']} role={r['role']} "
            f"attempts={r['attempts']} deps={r['deps']}")
    lines.append("recent events:")
    for e in snap["events"]:
        lines.append(f"  {e['kind']} {e['payload']}")
    return "\n".join(lines)
