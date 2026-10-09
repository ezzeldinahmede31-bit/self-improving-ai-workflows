"""Deterministic fixture builders for the v2 full battery (fixtures v1.0.0).

Every builder is seeded: same seed -> identical files AND identical expected
values. Expected values travel in the run row ctx for graders; they NEVER go
into prompts. Stdlib only.
"""

from __future__ import annotations

import base64
import json
import random


def csv_quarters(seed: int, nfiles: int = 3, prefix: str = "sales_q") -> tuple[dict, dict]:
    rng = random.Random(seed)
    files, total, nrows = {}, 0, 0
    for q in range(1, nfiles + 1):
        lines = ["id,amount"]
        for i in range(rng.randint(8, 15)):
            v = rng.randint(5, 500)
            total += v
            nrows += 1
            lines.append(f"{i + 1},{v}")
        files[f"{prefix}{q}.csv"] = "\n".join(lines) + "\n"
    return files, {"fixture_total": total, "expected": str(total),
                   "nrows": nrows}


def csv_malformed(seed: int) -> tuple[dict, dict]:
    rng = random.Random(seed)
    lines = ["order_id,qty,price"]
    valid_total, skipped = 0, 0
    for i in range(1, 21):
        r = rng.random()
        if r < 0.2:  # malformed row
            lines.append(rng.choice([f"{i},NaN", f"{i}", f"{i},2,XX", ""]))
            skipped += 1
        else:
            qty, price = rng.randint(1, 9), rng.randint(10, 200)
            valid_total += qty * price
            lines.append(f"{i},{qty},{price}")
    return ({"orders.csv": "\n".join(lines) + "\n"},
            {"expected": f"total={valid_total} skipped={skipped}"})


_FIRST = ["Lena", "Omar", "Priya", "Tomas", "Aisha", "Kofi", "Mira", "Jonas"]
_CITIES = ["Porto", "Lyon", "Oslo", "Gdańsk", "Izmir", "Haifa", "Cusco", "Nagano"]
_ROLES = ["owner", "reviewer", "scheduler", "auditor", "curator", "liaison"]


def synthetic_report(seed: int) -> tuple[dict, dict]:
    rng = random.Random(seed)
    people = rng.sample(_FIRST, 4)
    cities = rng.sample(_CITIES, 4)
    roles = rng.sample(_ROLES, 4)
    months = rng.sample(["March", "April", "May", "June"], 4)
    paras = [f"{p} ({r}) visited {c} in {m}."
             for p, r, c, m in zip(people, roles, cities, months)]
    doc = "Field report. " + " ".join(paras)
    return ({"report.txt": doc},
            {"keys": ["title", "owner", "eta"], "facts": [c.lower() for c in cities]})


def cipher_blob(seed: int) -> tuple[dict, dict]:
    rng = random.Random(seed)
    key = bytes(rng.sample(range(65, 91), 2)).decode()
    due = f"2026-{rng.randint(10, 12):02d}-{rng.randint(10, 28):02d}"
    raw = json.dumps({"job": rng.choice(["recall", "audit", "sync"]),
                      "due": due}).encode()
    x = bytes(c ^ ord(key[i % 2]) for i, c in enumerate(raw))
    blob = base64.b64encode(x).decode()
    return ({"BLOB.txt": blob, "KEY.txt": key},
            {"expected": due, "blob": blob, "key": key})


BUGGY_TEMPLATES = {
    "median": ("def median(a):\n    s = sorted(a)\n    return s[len(s) // 2]\n",
               {"func": "median", "cases": [([[3, 1, 2]], 2), ([[1, 2, 3, 4]], 2.5),
                                            ([[9]], 9), ([[4, 4]], 4.0)]}),
    "dedupe": ("def dedupe(items):\n    return sorted(set(items))\n",
               {"func": "dedupe", "cases": [([[1, 2, 2, 3]], [1, 2, 3]),
                                            ([["b", "a", "b"]], ["b", "a"]),
                                            (([],), [])]}),
    "running_max": ("def running_max(a):\n    best = 0\n    out = []\n    for x in a:\n        best = max(best, x)\n        out.append(best)\n    return out\n",
                    {"func": "running_max",
                     "cases": [([[3, 1, 4]], [3, 3, 4]), ([[-2, -5]], [-2, -2]),
                               (([],), [])]}),
}


def buggy_file(which: str) -> tuple[dict, dict]:
    src, spec = BUGGY_TEMPLATES[which]
    return ({"target.py": src}, dict(spec, file="target.py"))


FAKE_MAN = """ZXTOOL(1)                    Fictional Manual                    ZXTOOL(1)

NAME
    zxtool - manage widget queues (fictional; only this page documents it)

SYNOPSIS
    zxtool push --queue NAME --item TEXT [--priority N]
    zxtool drain --queue NAME [--limit N] [--dry-run]
    zxtool inspect --queue NAME --format short|full

OPTIONS
    --priority N   1..9, default 5. Higher runs first.
    --limit N      max items per drain, default 25, max 200.
    --dry-run      list what would drain without removing.
    --format       short prints ids only; full prints id+item+priority.

EXIT CODES
    0 ok · 2 bad arguments · 3 queue missing · 5 limit exceeded
"""


def man_page() -> tuple[dict, dict]:
    return ({"zxtool.1": FAKE_MAN},
            {"expected": "priority-max=9 limit-max=200 missing=3"})


def arch_choice(seed: int) -> tuple[dict, dict]:
    """Three topology options; exactly one meets budget+latency. Answer: its id."""
    rng = random.Random(seed)
    profiles = [
        {"cost": rng.randint(40, 60), "p95": rng.randint(100, 160)},
        {"cost": rng.randint(20, 35), "p95": rng.randint(200, 260)},
        {"cost": rng.randint(20, 35), "p95": rng.randint(100, 160)},
    ]
    ids = ["A", "B", "C"]
    rng.shuffle(ids)  # valid option varies by seed: no position bias
    opts = [dict(p, id=i) for p, i in zip(profiles, ids)]
    opts.sort(key=lambda o: o["id"])
    budget, sla = 36, 180
    valid = [o["id"] for o in opts if o["cost"] <= budget and o["p95"] <= sla]
    answer = sorted(valid)[0] if len(valid) == 1 else "NONE-OR-AMBIGUOUS"
    desc = (f"Budget ${budget}/mo. p95 must be <= {sla}ms. Options: "
            + "; ".join(f"{o['id']}: cost ${o['cost']}, p95 {o['p95']}ms" for o in opts)
            + ". Reply with ONLY the valid option id, or NONE-OR-AMBIGUOUS if not exactly one qualifies.")
    return ({"SCENARIO.txt": desc}, {"expected": answer, "scenario": desc})


def schedule_job(seed: int) -> tuple[dict, dict]:
    """Single-machine jobs with durations+deadlines; unique feasible order exists."""
    rng = random.Random(seed)
    names = ["a", "b", "c", "d"]
    durs = {n: rng.randint(1, 3) for n in names}
    # construct a feasible order, then set deadlines just above completion times
    order = names[:]
    rng.shuffle(order)
    t, deadlines = 0, {}
    for n in order:
        t += durs[n]
        deadlines[n] = t + rng.randint(0, 1)
    # withhold the order; agent must find A feasible one (any valid order passes)
    desc = ("Jobs (duration, deadline): "
            + ", ".join(f"{n}({durs[n]},{deadlines[n]})" for n in names)
            + ". Output ONE feasible execution order as a JSON list of exactly "
              "[a,b,c,d] (single machine, sequential). Reply with ONLY the JSON list.")
    return ({"JOBS.txt": desc},
            {"schedule": {"durs": durs, "deadlines": deadlines}, "jobs_desc": desc})


def grade_schedule_ctx(output: str, ctx: dict) -> tuple[bool, str]:
    try:
        order = json.loads(output.strip())
    except Exception as exc:  # noqa: BLE001
        return False, f"not json: {exc}"
    sched = ctx.get("schedule", {})
    durs, deadlines = sched.get("durs", {}), sched.get("deadlines", {})
    if set(order) != set(durs):
        return False, "job set wrong"
    t = 0
    for n in order:
        t += durs[n]
        if t > deadlines[n]:
            return False, f"job {n} misses deadline"
    return True, ""


BUILDERS = {"csv_quarters": lambda s: csv_quarters(s),
            "csv_malformed": csv_malformed,
            "synthetic_report": synthetic_report,
            "cipher_blob": cipher_blob,
            "buggy_file": None,  # needs `which`; handled by build_fixtures
            "man_page": lambda s: man_page(),
            "arch_choice": arch_choice,
            "schedule_job": schedule_job}


def build_fixtures(spec: dict) -> tuple[dict, dict]:
    """spec: {builder, seed, ...extra} or {builders: [spec, ...]} (merged).
    Returns (files, ctx)."""
    if isinstance(spec.get("builders"), list):
        files: dict = {}
        ctx: dict = {}
        for sub in spec["builders"]:
            f, c = build_fixtures(sub)
            files.update(f)
            ctx.update(c)
        return files, ctx
    name = spec.get("builder", "")
    seed = int(spec.get("seed", 1))
    if name == "buggy_file":
        return buggy_file(spec.get("which", "median"))
    fn = BUILDERS.get(name)
    if fn is None:
        raise ValueError(f"unknown fixture builder {name}")
    return fn(seed)
