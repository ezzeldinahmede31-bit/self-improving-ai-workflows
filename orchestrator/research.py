"""Pre-Build Research & Competitive Intelligence — permanent capability.

Position in flow: Requirement Understanding -> RESEARCH (this module) ->
Task Decomposition. Research findings live in the StateStore as structured
records; synthesis is DETERMINISTIC code (aggregation + license gate +
complaint mining). Research *workers* (opencode tasks) only collect facts
into strict schemas; they never decide architecture.

Rules enforced here (not by LLM):
  - decisions need >=1 source (evidence rule)
  - reuse needs license ALLOW + maintained + tests + approval
  - closed-source records carry NO code (learn-don't-copy)
  - replacing our component needs a comparison showing theirs-better
  - popularity (stars) is a signal, never proof
"""
from __future__ import annotations
import json
import time

LICENSE_ALLOW = {"MIT", "Apache-2.0", "BSD-2-Clause", "BSD-3-Clause", "ISC"}
LICENSE_REVIEW = {"GPL-2.0", "GPL-3.0", "AGPL-3.0", "LGPL-2.1", "LGPL-3.0",
                  "MPL-2.0", "EPL-2.0", "CDDL-1.0"}

DEPTH_TOPICS = {
    "light": ["oss-candidates", "closed-candidates", "community-feedback"],
    "deep": ["oss-candidates", "closed-candidates", "community-feedback",
             "architecture-comparison", "reuse-analysis"],
    "deep-security": ["oss-candidates", "closed-candidates",
                      "community-feedback", "architecture-comparison",
                      "reuse-analysis", "security-review"],
}


def decide_depth(attrs: dict) -> str:
    """Adaptive depth from project attributes. Small/safe -> light."""
    score = 0
    score += {"small": 0, "medium": 1, "large": 2}.get(
        attrs.get("complexity", "small"), 0)
    score += {"low": 0, "medium": 1, "high": 2}.get(
        attrs.get("importance", "low"), 0)
    score += {"low": 0, "medium": 1, "high": 2}.get(
        attrs.get("security_sensitivity", "low"), 0)
    try:
        score += min(2, int(attrs.get("dependencies", 0)) // 3)
    except (TypeError, ValueError):
        pass
    score += {"low": 0, "medium": 1, "high": 2}.get(
        attrs.get("failure_cost", "low"), 0)
    if attrs.get("security_sensitivity") == "high":
        return "deep-security"
    if score >= 4:
        return "deep"
    return "light"


def plan_research(project_goal: str, depth: str) -> list[dict]:
    topics = DEPTH_TOPICS.get(depth, DEPTH_TOPICS["light"])
    return [{"topic": t, "depth": depth, "goal": project_goal} for t in topics]


def license_verdict(spdx: str | None) -> tuple[str, str]:
    """Return (verdict, reason). verdict in ALLOW/REVIEW/DENY."""
    if not spdx or spdx == "NOASSERTION":
        return "DENY", "unknown or unasserted license"
    if spdx in LICENSE_ALLOW:
        return "ALLOW", f"permissive license {spdx}"
    if spdx in LICENSE_REVIEW:
        return "REVIEW", f"copyleft/conditional license {spdx} needs human review"
    return "REVIEW", f"unrecognized license {spdx} needs human review"


OSS_REQUIRED = ("name", "url", "arch", "license", "activity", "tests",
                "sources")
CLOSED_REQUIRED = ("name", "sources", "strengths_observed")
FEEDBACK_REQUIRED = ("claim", "source", "source_kind")


def validate_finding(kind: str, payload: dict) -> list[str]:
    errs: list[str] = []
    if kind == "oss-candidate":
        for f in OSS_REQUIRED:
            if f not in payload:
                errs.append(f"missing {f}")
        if "code" in payload and payload.get("license") not in LICENSE_ALLOW:
            pass  # code snippets still allowed inside analysis; reuse gated
    elif kind == "closed-candidate":
        for f in CLOSED_REQUIRED:
            if f not in payload:
                errs.append(f"missing {f}")
        if payload.get("code"):
            errs.append("closed-source records must not contain code")
    elif kind == "community-feedback":
        for f in FEEDBACK_REQUIRED:
            if f not in payload:
                errs.append(f"missing {f}")
        if payload.get("source_kind") not in (
                "fact", "documented-issue", "individual-opinion",
                "repeated-pattern"):
            errs.append("source_kind must be classified")
    else:
        errs.append(f"unknown finding kind {kind}")
    srcs = payload.get("sources") if isinstance(payload, dict) else None
    if kind in ("oss-candidate", "closed-candidate") and not srcs:
        errs.append("at least one source required")
    return errs


def repeated_complaints(feedback: list[dict], min_sources: int = 2) -> list[dict]:
    """Mine complaints appearing across >=min_sources distinct sources."""
    groups: dict[str, dict] = {}
    for fb in feedback:
        if fb.get("source_kind") == "individual-opinion":
            continue  # one opinion is not a pattern
        key = str(fb.get("claim", "")).strip().lower()
        g = groups.setdefault(key, {"claim": fb.get("claim"),
                                    "sources": set(), "kinds": set()})
        g["sources"].add(str(fb.get("source")))
        g["kinds"].add(str(fb.get("source_kind")))
    out = []
    for g in groups.values():
        if len(g["sources"]) >= min_sources:
            out.append({"claim": g["claim"],
                        "sources": sorted(g["sources"]),
                        "evidence_kinds": sorted(g["kinds"])})
    return sorted(out, key=lambda x: (-len(x["sources"]), x["claim"]))


def propose_decision(store, project_id: str, decision: str, reason: str,
                     evidence: list[str], effects: dict | None = None,
                     comparison: dict | None = None) -> tuple[bool, str]:
    """Record an architecture decision. Enforces the evidence rule."""
    if not evidence:
        return False, "decision needs at least one source"
    if effects and effects.get("replace_ours"):
        if not comparison or comparison.get("verdict") != "theirs-better":
            return False, "replacing our component needs theirs-better comparison"
    did = store.add_decision(project_id, decision, reason, evidence,
                             effects or {}, comparison or {})
    return True, did


def reuse_verdict(store, project_id: str, component: str) -> tuple[bool, str]:
    """Deterministic reuse gate for an OSS component finding."""
    items = store.list_findings(project_id, "oss-candidate")
    cand = next((i for i in items if i["payload"].get("name") == component),
                None)
    if cand is None:
        return False, "no analyzed candidate with that name"
    p = cand["payload"]
    verdict, why = license_verdict(p.get("license"))
    if verdict != "ALLOW":
        return False, f"license gate: {verdict} ({why})"
    if not p.get("maintained"):
        return False, "not maintained"
    if not p.get("tests"):
        return False, "no tests evidence"
    return True, f"reusable ({why})"


def apply_decisions(store, project_id: str) -> dict:
    """Turn APPROVED decisions into decomposition inputs.

    Returns {new_tasks, constraints, reuses, avoided}. Only approved
    decisions apply; reuse effects re-checked through reuse_verdict.
    """
    new_tasks, constraints, reuses, avoided = [], [], [], []
    for d in store.list_decisions(project_id, status="approved"):
        eff = d.get("effects", {})
        for t in eff.get("add_tasks", []):
            new_tasks.append(t)
        for c in eff.get("add_constraints", []):
            constraints.append(c)
        for r in eff.get("reuse", []):
            ok, why = reuse_verdict(store, project_id, r)
            (reuses if ok else avoided).append({"component": r, "why": why})
        for a in eff.get("avoid", []):
            avoided.append({"pattern": a, "why": d["reason"]})
    return {"new_tasks": new_tasks, "constraints": constraints,
            "reuses": reuses, "avoided": avoided}


def build_research_prompt(topic: str, project_goal: str, depth: str) -> str:
    return "\n".join([
        f"You are a Research worker. Project goal: {project_goal}",
        f"Topic: {topic} (depth: {depth}).",
        "Collect FACTS with sources (URLs). Classify every community claim as",
        "fact | documented-issue | individual-opinion | repeated-pattern.",
        "For closed-source systems: behavior and patterns ONLY, never code.",
        "Write findings/<topic>.json with fields matching the finding schema",
        "and reply DONE. Small focused output only; no secrets.",
    ])


REPORT_SECTIONS = ["Project Goal", "Open Source Candidates",
                   "Closed Source Candidates", "Architecture Comparison",
                   "Feature Comparison", "Community Feedback",
                   "Repeated Complaints", "Strengths Worth Adopting",
                   "Weaknesses To Avoid", "Reusable Components",
                   "License Analysis", "Security Considerations",
                   "Performance Considerations", "Recommended Architecture Changes",
                   "Final Design Decisions", "Sources"]


def generate_report(store, project_id: str, project_goal: str,
                    path: str) -> str:
    oss = store.list_findings(project_id, "oss-candidate")
    closed = store.list_findings(project_id, "closed-candidate")
    fb = store.list_findings(project_id, "community-feedback")
    complaints = repeated_complaints([f["payload"] for f in fb])
    decisions = store.list_decisions(project_id)
    applied = apply_decisions(store, project_id)
    srcs: list[str] = []
    for items in (oss, closed, fb):
        for it in items:
            for s in it["payload"].get("sources", []):
                if s not in srcs:
                    srcs.append(s)
    lines = [f"# Research Report — {project_goal}", ""]
    lines += ["## Project Goal", project_goal, ""]
    lines += ["## Open Source Candidates"] + [
        f"- {p['payload'].get('name')}: {p['payload'].get('url')} "
        f"(license {p['payload'].get('license')}, "
        f"tests: {p['payload'].get('tests')})" for p in oss] + [""]
    lines += ["## Closed Source Candidates"] + [
        f"- {p['payload'].get('name')}: "
        f"{'; '.join(p['payload'].get('strengths_observed', []))}"
        for p in closed] + [""]
    lines += ["## Architecture Comparison",
              "(see candidate arch fields + decisions below)", ""]
    lines += ["## Feature Comparison", "(see candidate payloads in store)", ""]
    lines += ["## Community Feedback"] + [
        f"- [{p['payload'].get('source_kind')}] {p['payload'].get('claim')} "
        f"({p['payload'].get('source')})" for p in fb] + [""]
    lines += ["## Repeated Complaints"] + [
        f"- {c['claim']} ({len(c['sources'])} sources)" for c in complaints] + [""]
    lines += ["## Strengths Worth Adopting"] + [
        f"- {d['decision']}: {d['reason']}" for d in decisions
        if "adopt" in d["decision"].lower() or "reuse" in d["decision"].lower()] + [""]
    lines += ["## Weaknesses To Avoid"] + [
        f"- {a.get('pattern', a.get('component', a))}: {a.get('why', '')}"
        for a in applied["avoided"]] + [""]
    lines += ["## Reusable Components"] + [
        f"- {r['component']}: {r['why']}" for r in applied["reuses"]] + [""]
    lines += ["## License Analysis"] + [
        f"- {p['payload'].get('name')}: "
        f"{license_verdict(p['payload'].get('license'))}" for p in oss] + [""]
    lines += ["## Security Considerations",
              "Closed-source: behavior only. Reuse: permissive licenses only.", ""]
    lines += ["## Performance Considerations",
              f"Repeated complaints: {len(complaints)} patterns.", ""]
    lines += ["## Recommended Architecture Changes"] + [
        f"- {d['decision']} (status: {d['status']})" for d in decisions] + [""]
    lines += ["## Final Design Decisions"] + [
        f"- [{d['status']}] {d['decision']}: {d['reason']} "
        f"evidence={len(d['evidence'])}" for d in decisions] + [""]
    lines += ["## Sources"] + [f"- {s}" for s in srcs] + [""]
    import os as _os
    _os.makedirs(_os.path.dirname(path) or ".", exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines))
    return path


def kb_save(store, topic: str, findings: dict, sources: list[str],
            project_id: str) -> None:
    store.kb_put(topic.lower().strip(), findings, sources, project_id)


def kb_lookup(store, topic: str, max_age_days: float = 90) -> dict | None:
    row = store.kb_get(topic.lower().strip())
    if not row:
        return None
    age_days = (time.time() - row["updated_at"]) / 86400.0
    row["stale"] = age_days > max_age_days
    return row


def _json(obj) -> str:
    return json.dumps(obj, ensure_ascii=False)
