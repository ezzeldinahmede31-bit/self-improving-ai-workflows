"""Static auditor for clinic n8n project files. No secrets printed (counts only).
Usage: venv/bin/python scripts/clinic_audit.py  (run from project root)
Writes: FINAL_AUDIT/inventory.json, FINAL_AUDIT/static-findings.json
"""
import json
import re
from pathlib import Path
from collections import defaultdict

ROOT = Path("memory/workflows")
FILES = sorted(ROOT.glob("clinic_*.json"))
DEMOPAT = re.compile(
    r"DEMO|Dr\.?\s*Samir|دكتور\s*سمير|300\s*(EGP|جنيه|LE)|"
    r"Test Clinic|عيادة\s*تجريبية|example\.com|\+2010{7}|\+2012345678",
    re.IGNORECASE)
SECRETPAT = re.compile(
    r"sk-[A-Za-z0-9]{10,}|xox[bap]-[A-Za-z0-9-]+|"
    r"BEGIN [A-Z ]*PRIVATE KEY", re.IGNORECASE)
NODEREF = re.compile(r"\$\(['\"]([^'\"]+)['\"]\)")
REDISKEY = re.compile(r"['\"]([a-zA-Z0-9_-]*(?::[a-zA-Z0-9_*{}$.-]+)+)['\"]")


def main():
    inv, findings = {}, defaultdict(list)
    name_by_file = {}
    for f in FILES:
        d = json.loads(f.read_text(encoding="utf-8"))
        name_by_file[f.stem] = d.get("name", f.stem)
    for f in FILES:
        d = json.loads(f.read_text(encoding="utf-8"))
        nodes = d.get("nodes", [])
        conns = d.get("connections", {})
        names = {n.get("name") for n in nodes}
        entry = {"file": f.name, "n8n_name": d.get("name"),
                 "nodes": len(nodes), "triggers": [],
                 "creds": set(), "exec_refs": [], "err_wf": None,
                 "orphans": [], "dangling": [], "demo_hits": [],
                 "secret_hits": 0, "redis_keys": set(),
                 "no_retry": [], "no_timeout": []}
        # targets referenced by connections
        targets = set()
        for src, outs in conns.items():
            if src not in names:
                entry["dangling"].append(f"conn-from-unknown:{src}")
            for br in (outs.get("main") or []):
                for e in br:
                    targets.add(e.get("node"))
        for n in nodes:
            nm = n.get("name")
            t = n.get("type", "")
            if "rigger" in t or "webhook" in t.lower():
                entry["triggers"].append(f"{nm}:{t.split('.')[-1]}")
            for cn, cv in (n.get("credentials") or {}).items():
                entry["creds"].add(f"{cn}:{cv.get('name')}")
            if t == "n8n-nodes-base.executeWorkflow":
                wf = (n.get("parameters") or {}).get("workflowId")
                entry["exec_refs"].append(f"{nm}->{wf}")
            if t == "n8n-nodes-base.code":
                js = (n.get("parameters") or {}).get("jsCode", "")
                if "Tool Workflow" in js or "toolWorkflow" in js:
                    entry["exec_refs"].append(f"{nm}->toolWorkflow?")
            for p in ("retryOnFail", "onError"):
                pass
            if t in ("n8n-nodes-base.httpRequest",):
                p = n.get("parameters", {})
                if not n.get("retryOnFail"):
                    entry["no_retry"].append(nm)
                if not (p.get("options") or {}).get("timeout"):
                    entry["no_timeout"].append(nm)
            s = json.dumps(n)
            for m in DEMOPAT.findall(s):
                entry["demo_hits"].append(f"{nm}:{m[:40]}")
            entry["secret_hits"] += len(SECRETPAT.findall(s))
            for m in REDISKEY.findall(s):
                if ":" in m and "http" not in m:
                    entry["redis_keys"].add(m[:80])
            for m in NODEREF.findall(s):
                if m not in names:
                    entry["dangling"].append(f"{nm}->missing-node:{m}")
        # orphans: non-trigger nodes with no incoming edge
        incoming = set()
        for src, outs in conns.items():
            for br in (outs.get("main") or []):
                for e in br:
                    incoming.add(e.get("node"))
        trig_names = {n.get("name") for n in nodes
                      if "rigger" in n.get("type", "")
                      or "webhook" in n.get("type", "").lower()}
        for n in names:
            if n not in incoming and n not in trig_names and n not in targets:
                entry["orphans"].append(n)
        entry["creds"] = sorted(entry["creds"])
        entry["redis_keys"] = sorted(entry["redis_keys"])
        inv[f.stem] = entry
    Path("FINAL_AUDIT").mkdir(exist_ok=True)
    json.dump(inv, open("FINAL_AUDIT/inventory.json", "w"), indent=1,
              ensure_ascii=False)
    print("workflows:", len(inv), "| nodes:",
          sum(e["nodes"] for e in inv.values()))
    # cross-file exec refs resolution
    live_names = set(name_by_file.values())
    for stem, e in inv.items():
        for r in e["exec_refs"]:
            tgt = r.split("->", 1)[1]
            if tgt not in live_names and tgt != "toolWorkflow?":
                findings["exec-unresolved"].append(f"{stem}: {r}")
    json.dump(dict(findings), open("FINAL_AUDIT/static-findings.json", "w"),
              indent=1, ensure_ascii=False)
    for k, v in findings.items():
        print(k, len(v))
    noretry = sum(len(e["no_retry"]) for e in inv.values())
    notime = sum(len(e["no_timeout"]) for e in inv.values())
    print("http-no-retry:", noretry, "| http-no-timeout:", notime)
    print("demo-hits:", sum(len(e["demo_hits"]) for e in inv.values()),
          "| secret-hits:",
          sum(e["secret_hits"] for e in inv.values()))


if __name__ == "__main__":
    main()
