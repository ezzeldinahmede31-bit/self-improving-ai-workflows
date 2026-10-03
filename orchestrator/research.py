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
import os
import re
import time

from egress_firewall import (fetch_pinned, EgressPolicy, PinnedFetchBlocked)

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


def build_research_goal(topic: str, repos: list[str]) -> str:
    lines = [
        f"Research OSS candidates for topic '{topic}'.",
        "For EACH repo below, call the public GitHub API with curl:",
    ]
    for r in repos:
        lines.append(f"  curl -s https://api.github.com/repos/{r}")
    lines += [
        f"Write findings/{topic}.json as a JSON object with keys:",
        '{"candidates": [{"name":..., "url":..., "arch":... (1 line guess allowed),',
        ' "license": <exact SPDX from API>, "activity": <pushed_at + stars from API>,',
        ' "maintained": true/false, "tests": true/false,',
        ' "sources": ["https://api.github.com/repos/<org>/<repo>", ...]}]}',
        "Rules: license/activity/stars MUST come from the API output you saw.",
        "sources MUST be only URLs you actually called. No invented numbers.",
    ]
    return "\n".join(lines)


def research_task_contracts(topics: list[dict]) -> list[dict]:
    """Build bounded research contracts. topics=[{topic, repos, deps}]."""
    out = []
    for t in topics:
        tid = f"research-{t['topic']}"
        path = f"findings/{t['topic']}.json"
        out.append({
            "task_id": tid, "kind": "opencode", "role": "Research Agent",
            "goal": build_research_goal(t["topic"], t.get("repos", [])),
            "outputs": [], "allowed_files": [path],
            "dependencies": t.get("deps", []),
            "acceptance": [
                {"id": "exists", "kind": "file_exists", "path": path},
                {"id": "sourced", "kind": "file_contains", "path": path,
                 "text": "api.github.com"}],
            "model_policy": "primary-only", "gates": False,
            "timeout_s": 240, "max_attempts": 2, "estimate_s": 60,
        })
    return out


def verify_license_live(github_url: str, timeout_s: int = 20) -> str | None:
    """Deterministic re-check of a repo license via public GitHub API.

    Transport is connection-pinned: api.github.com is validated AND the
    socket opens the authorized IP literally (no DNS-rebind reroute of an
    opt-in live check). The candidate URL shape is allow-listed to
    owner/name — anything else returns None without touching the network.
    """
    m = github_url.startswith("https://github.com/")
    if not m:
        return None
    repo = github_url[len("https://github.com/"):].strip("/")
    if repo.count("/") != 1:
        return None
    try:
        out = fetch_pinned(
            f"https://api.github.com/repos/{repo}",
            EgressPolicy(allow_public_internet=True,
                         allowed_domains=("api.github.com",)),
            method="GET",
            headers={"User-Agent": "orchestrator-verify",
                     "Accept": "application/vnd.github+json"},
            timeout_s=timeout_s)
        if out.get("status") != 200:
            return None
        doc = json.loads(out["body"].decode())
        return ((doc.get("license") or {}).get("spdx_id"))
    except (PinnedFetchBlocked, OSError, ValueError, UnicodeDecodeError):
        return None
    except Exception:  # noqa: BLE001 - unverifiable means unverified
        return None


def run_synthesis(store, project_id: str, work_root: str,
                  verify_licenses: bool = False) -> dict:
    """Deterministic synthesis: validate -> record -> mine -> propose.

    Returns {ok, recorded, decisions, errors}. Invalid evidence fails the
    synthesis task (retry policy applies) — decisions never come from thin air.
    """
    errors: list[str] = []
    recorded = 0
    for t in store.list_tasks(project_id):
        if t["status"] != "DONE" or not t["task_id"].startswith("research-"):
            continue
        fdir = os.path.join(work_root, f"plain-{t['task_id']}", "findings")
        if not os.path.isdir(fdir):
            errors.append(f"{t['task_id']}: no findings dir")
            continue
        for fn in sorted(os.listdir(fdir)):
            if not fn.endswith(".json"):
                continue
            try:
                with open(os.path.join(fdir, fn), encoding="utf-8") as fh:
                    doc = json.load(fh)
            except (OSError, ValueError) as e:
                errors.append(f"{t['task_id']}/{fn}: bad JSON ({e})")
                continue
            for cand in doc.get("candidates", []):
                payload = {"name": cand.get("name"), "url": cand.get("url"),
                           "arch": cand.get("arch", "?"),
                           "license": cand.get("license"),
                           "activity": cand.get("activity", "?"),
                           "maintained": bool(cand.get("maintained")),
                           "tests": bool(cand.get("tests")),
                           "sources": cand.get("sources", [])}
                errs = validate_finding("oss-candidate", payload)
                if errs:
                    errors.append(f"{t['task_id']}/{fn}: {errs}")
                    continue
                if verify_licenses and payload.get("url", "").startswith(
                        "https://github.com/"):
                    live = verify_license_live(payload["url"])
                    if live is not None and live != payload["license"]:
                        errors.append(
                            f"{t['task_id']}/{fn}: license mismatch "
                            f"(claimed {payload['license']}, live {live})")
                        continue
                store.add_finding(project_id, "oss-candidate",
                                  t["task_id"], payload)
                recorded += 1
    if errors:
        return {"ok": False, "recorded": recorded, "decisions": [],
                "errors": errors}
    if recorded == 0:
        return {"ok": False, "recorded": 0, "decisions": [],
                "errors": ["no research evidence recorded"]}
    decisions = []
    for f in store.list_findings(project_id, "oss-candidate"):
        p = f["payload"]
        v, _ = license_verdict(p.get("license"))
        if v != "ALLOW" or not p.get("maintained") or not p.get("tests"):
            continue
        ok, did = propose_decision(
            store, project_id, f"Reuse pattern from {p['name']}",
            f"{p['license']} + maintained + tests per {p['url']}",
            p.get("sources", []), {"reuse": [p["name"]]})
        if ok:
            decisions.append(did)
    return {"ok": True, "recorded": recorded, "decisions": decisions,
            "errors": []}


def make_synthesis_fn(store, project_id: str, work_root: str,
                      verify_licenses: bool = False):
    def fn(ctx, work_dir):
        res = run_synthesis(store, project_id, work_root, verify_licenses)
        if not res["ok"]:
            raise RuntimeError(f"synthesis failed: {res['errors']}")
        with open(os.path.join(work_dir, "synthesis.json"), "w",
                  encoding="utf-8") as fh:
            json.dump(res, fh, ensure_ascii=False)
        return {"notes": f"recorded={res['recorded']} "
                         f"decisions={len(res['decisions'])}",
                "outputs": {"recorded": res["recorded"],
                            "decisions": res["decisions"]}}
    return fn


def approve_proposed(store, project_id: str) -> list[str]:
    """Operator step: approve all proposed decisions (recorded in events)."""
    out = []
    for d in store.list_decisions(project_id, status="proposed"):
        store.set_decision_status(project_id, d["id"], "approved")
        out.append(d["id"])
    return out


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


def _tokens(text: str) -> set[str]:
    toks = {t for t in re.sub(r"[^a-z0-9]+", " ", text.lower()).split()
            if len(t) > 2}
    stems = {t[:-1] for t in toks if len(t) > 4 and t.endswith("s")}
    return toks | stems


def kb_lookup(store, topic: str, max_age_days: float = 90,
              fuzzy_threshold: float = 0.35) -> dict | None:
    """Exact match first, else best token-overlap (Jaccard) match.

    No embeddings, no deps: ranked keyword overlap. Returns None below
    threshold. Result carries match=exact|fuzzy and score for honesty.
    """
    row = store.kb_get(topic.lower().strip())
    if row:
        age_days = (time.time() - row["updated_at"]) / 86400.0
        row["stale"] = age_days > max_age_days
        row["match"] = "exact"
        row["score"] = 1.0
        return row
    want = _tokens(topic)
    if not want:
        return None
    best, best_score = None, 0.0
    with store._lock:
        rows = store._db.execute(
            "SELECT topic,findings,sources,project_id,updated_at "
            "FROM research_kb").fetchall()
    for t, f, s, p, u in rows:
        got = _tokens(t)
        if not got:
            continue
        score = len(want & got) / len(want | got)
        if score > best_score:
            best, best_score = ({"topic": t,
                                 "findings": json.loads(f),
                                 "sources": json.loads(s),
                                 "project_id": p, "updated_at": u}, score)
    if best is None or best_score < fuzzy_threshold:
        return None
    best["stale"] = (time.time() - best["updated_at"]) / 86400.0 > max_age_days
    best["match"] = "fuzzy"
    best["score"] = round(best_score, 3)
    return best


def _json(obj) -> str:
    return json.dumps(obj, ensure_ascii=False)
