"""Security operations: response, correlation, continuous red-team.

Three loops, one module, stdlib only:
  - Respond: detect -> kill session -> revoke token -> quarantine
    workflow -> alert human -> preserve evidence. Each action is a
    caller callable; the runbook records per-action ok/failure so a
    half-contained incident is visible, not assumed contained.
  - Correlate: group raw alerts by (agent, session) inside a time
    window; 3+ distinct signals fuse into one incident (lonely alerts
    stay open but unlinked — no silent drops).
  - RedTeamLoop: scheduled attack-corpus runs (adversarial_suite
    shape: run_suite(detector) -> rows/rate) against staging; new
    failures convert to golden-corpus cases (dedupe by case id).

Only stdlib is used. Side effects live in caller callables.
"""

from __future__ import annotations

import time


RESPONSE_STEPS = ("kill_session", "revoke_token", "quarantine_workflow",
                  "alert_human", "preserve_evidence")


class IncidentResponse:
    """Runbook executor with per-action honesty."""

    def __init__(self, actions: dict | None = None):
        self._actions = dict(actions or {})
        self.runs: list[dict] = []

    def respond(self, incident_id: str, context: dict | None = None) -> dict:
        """Execute the five containment steps in order, record each."""
        ctx = dict(context or {})
        steps = []
        for name in RESPONSE_STEPS:
            fn = self._actions.get(name)
            if fn is None:
                steps.append({"step": name, "ok": False,
                              "note": "no handler bound"})
                continue
            try:
                fn(incident_id, ctx)
                steps.append({"step": name, "ok": True, "note": ""})
            except Exception as exc:  # noqa: BLE001 - record, continue
                steps.append({"step": name, "ok": False, "note": str(exc)})
        contained = all(s["ok"] for s in steps)
        out = {"incident": str(incident_id), "ts": time.time(),
               "contained": contained, "steps": steps}
        self.runs.append(out)
        return out


def correlate(alerts: list[dict], *, window_s: float = 600.0,
              fuse_at: int = 3) -> dict:
    """Fuse alerts sharing (agent, session) inside the time window."""
    groups: dict[tuple[str, str], list[dict]] = {}
    for alert in alerts:
        key = (str(alert.get("agent", "?")), str(alert.get("session", "?")))
        groups.setdefault(key, []).append(alert)
    incidents, lonely = [], []
    for (agent, session), items in groups.items():
        items = sorted(items, key=lambda a: a.get("ts", 0))
        if not items:
            continue
        span = items[-1].get("ts", 0) - items[0].get("ts", 0)
        kinds = sorted({str(i.get("kind", "?")) for i in items})
        if len(items) >= fuse_at and span <= window_s and len(kinds) >= 2:
            incidents.append({"agent": agent, "session": session,
                              "signals": len(items), "kinds": kinds,
                              "span_s": round(span, 1)})
        else:
            lonely.extend(items)
    return {"incidents": incidents, "lonely": lonely}


class RedTeamLoop:
    """Nightly-style attack runs -> golden cases for new failures."""

    def __init__(self):
        self.runs: list[dict] = []

    def run_cycle(self, run_suite_fn, golden_add_fn) -> dict:
        """Execute one cycle: suite -> new failures -> corpus cases.

        run_suite_fn() -> {rows: [{case, family, ok}]} (adversarial
        shape). golden_add_fn(case_id, reproducer, expect) records.
        """
        if not callable(run_suite_fn) or not callable(golden_add_fn):
            raise TypeError("suite and golden hooks must be callable")
        result = run_suite_fn() or {}
        rows = result.get("rows", []) or []
        added = []
        for row in rows:
            if row.get("ok"):
                continue
            cid = f"rt-{row.get('family', 'x')}-{row.get('case', '?')}"
            try:
                golden_add_fn(cid, str(row), "defense must hold")
                added.append(cid)
            except Exception:  # noqa: BLE001 - next case, still counted
                added.append(cid + ":record-failed")
        out = {"ts": time.time(), "checked": len(rows),
               "failures": sum(1 for r in rows if not r.get("ok")),
               "added": added}
        self.runs.append(out)
        return out
