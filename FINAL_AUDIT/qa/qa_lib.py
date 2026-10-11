"""Shared harness for the permanent QA suite (isolated copies only)."""
import json
import subprocess

ISO = "/home/ezzeldin/Documents/Default Project/FINAL_AUDIT/qa/isolated"
RESULTS = []


def wf_code(wf, node):
    d = json.load(open(f"{ISO}/{wf}.json"))
    for n in d["nodes"]:
        if n.get("name") == node:
            return n["parameters"]["jsCode"]
    raise KeyError(f"{wf}:{node}")


def run(js, stubs):
    pre = ""
    if "$input" in stubs:
        pre += ("const $input = {first: () => ({json: "
                + json.dumps(stubs["$input"]) + "})};\n")
    if "$" in stubs:
        m = ",".join(
            f'"{k}":{{first:()=>({{json:{json.dumps(v)}}}),'
            f'item:{{json:{json.dumps(v)}}}}}' for k, v in stubs["$"].items())
        pre += f"const $ = (n) => ({{{m}}})[n];\n"
    if "$env" in stubs:
        pre += f"const $env = {json.dumps(stubs['$env'])};\n"
    if "$now" in stubs:
        pre += f"const $now = {{toISO: () => '{stubs['$now']}'}};\n"
    prog = ("const __items__ = (function(){\n" + pre + js
            + "\n})();\nconsole.log('__RESULT__:' + "
              "JSON.stringify(__items__));")
    r = subprocess.run(["node", "-e", prog], capture_output=True, text=True,
                       timeout=30)
    if r.returncode != 0:
        return {"__error__": r.stderr.strip()[-250:]}
    for line in r.stdout.splitlines():
        if line.startswith("__RESULT__:"):
            return json.loads(line[11:])
    return {"__error__": "no-result"}


def T(tid, cond, evidence=""):
    RESULTS.append((tid, bool(cond), evidence))
    print(("PASS " if cond else "FAIL ") + tid,
          "" if cond else str(evidence)[:160])


def summary():
    n = sum(1 for _, c, _ in RESULTS if c)
    print(f"\nSUITE: {n}/{len(RESULTS)}")
    return n == len(RESULTS)
