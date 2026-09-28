"""Model benchmark harness: same tasks, every model, data-driven routing.

Each model is a callable: model_fn(task_input) -> {"output": str,
"tokens": int, "cost": float}. Tasks carry checker callables
(checker(task_input, output) -> (bool, note)) across dimensions:
reasoning, tool use, structured output, coding, safety refusal, and
any domain task the caller adds. run_suite() records per-task ok,
latency, tokens, cost; compare() ranks models by pass rate with
cost/latency tie-breaks and names the router pick. No network, no
vendor SDKs — callers inject their own model functions.

Only stdlib is used.
"""

from __future__ import annotations

import time


def contains(*needles: str):
    """Checker: output holds every required substring."""
    def _check(_inp, output) -> tuple[bool, str]:
        missing = [n for n in needles if n not in str(output)]
        if missing:
            return False, f"absent: {missing}"
        return True, ""
    return _check


def parses_json(_inp, output) -> tuple[bool, str]:
    """Checker: output is a single JSON object (no prose wrapper)."""
    import json
    try:
        val = json.loads(str(output).strip())
    except ValueError:
        return False, "not JSON"
    if not isinstance(val, dict):
        return False, "JSON but not an object"
    return True, ""


class ModelBench:
    """Task registry + suite runner + cross-model comparison."""

    def __init__(self):
        self._tasks: list[dict] = []

    def add_task(self, task_id: str, task_input: str, checker,
                 dimension: str = "general", weight: float = 1.0) -> None:
        """Register one benchmark task with its checker callable."""
        if not callable(checker):
            raise TypeError("checker must be callable")
        self._tasks.append({"id": str(task_id), "input": str(task_input),
                            "checker": checker, "dimension": str(dimension),
                            "weight": float(weight)})

    def tasks(self) -> list[str]:
        """Registered task ids."""
        return [t["id"] for t in self._tasks]

    def run_suite(self, model_fn, *, model_name: str = "model") -> dict:
        """Run every task through one model function."""
        if not callable(model_fn):
            raise TypeError("model_fn must be callable")
        rows, w_pass, w_total = [], 0.0, 0.0
        spent_t, spent_c = 0.0, 0.0
        for task in self._tasks:
            t0 = time.time()
            try:
                res = model_fn(task["input"]) or {}
                out = res.get("output", "")
                ok, note = task["checker"](task["input"], out)
            except Exception as exc:  # noqa: BLE001 - record, continue suite
                out, ok, note = "", False, f"model raised: {exc}"
                res = {}
            dt = time.time() - t0
            w_total += task["weight"]
            if ok:
                w_pass += task["weight"]
            spent_t += dt
            spent_c += float(res.get("cost", 0.0) or 0.0)
            rows.append({"task": task["id"], "dimension": task["dimension"],
                         "ok": bool(ok), "note": str(note),
                         "latency_s": round(dt, 3),
                         "tokens": int(res.get("tokens", 0) or 0),
                         "cost": float(res.get("cost", 0.0) or 0.0)})
        rate = (w_pass / w_total) if w_total else 1.0
        return {"model": str(model_name), "pass_rate": rate,
                "passed_weight": w_pass, "total_weight": w_total,
                "avg_latency_s": round(spent_t / len(rows), 3) if rows else 0.0,
                "total_cost": round(spent_c, 6), "rows": rows}

    def compare(self, models: dict) -> dict:
        """Run the suite on each model; rank by pass rate, cost, latency."""
        results = [self.run_suite(fn, model_name=name)
                   for name, fn in models.items()]
        ranked = sorted(results,
                        key=lambda r: (-r["pass_rate"], r["total_cost"],
                                       r["avg_latency_s"]))
        pick = ranked[0]["model"] if ranked else None
        return {"ranking": [r["model"] for r in ranked],
                "pick": pick, "results": {r["model"]: r for r in results}}
