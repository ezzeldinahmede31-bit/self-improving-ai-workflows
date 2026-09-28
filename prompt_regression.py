"""Prompt regression testing: versioned prompts vs frozen goldens.

Every important prompt carries a version. A golden dataset (frozen
inputs + checker callables) runs against the current version and any
candidate; compare() reports pass rates, per-case deltas, and the
regression list. Deployment blocks when the candidate loses more than
the configured tolerance — a single number gates the rollout.

Only stdlib is used. Model functions are caller-injected.
"""

from __future__ import annotations

import time


class PromptRegression:
    """Prompt versions + golden cases + blocking comparisons."""

    def __init__(self):
        self._prompts: dict[str, dict] = {}
        self._goldens: list[dict] = []

    def add_prompt(self, version: str, template: str,
                   model_fn=None) -> None:
        """Register a prompt version with its template + model function."""
        self._prompts[str(version)] = {"template": str(template),
                                       "model_fn": model_fn}

    def add_golden(self, case_id: str, model_input: str, checker,
                   weight: float = 1.0) -> None:
        """Add one frozen golden case with a checker callable."""
        if not callable(checker):
            raise TypeError("checker must be callable")
        self._goldens.append({"id": str(case_id),
                              "input": str(model_input),
                              "checker": checker, "weight": float(weight)})

    def run(self, version: str) -> dict:
        """Execute all goldens against one prompt version."""
        spec = self._prompts.get(str(version))
        if spec is None:
            raise KeyError(f"unknown prompt version: {version}")
        fn = spec["model_fn"]
        if not callable(fn):
            raise ValueError(f"version {version} has no model function")
        rows, w_pass, w_total = [], 0.0, 0.0
        for case in self._goldens:
            t0 = time.time()
            try:
                out = fn(case["input"]) or ""
                ok, note = case["checker"](case["input"], out)
            except Exception as exc:  # noqa: BLE001 - record, continue
                out, ok, note = "", False, f"model raised: {exc}"
            w_total += case["weight"]
            if ok:
                w_pass += case["weight"]
            rows.append({"case": case["id"], "ok": bool(ok),
                         "note": str(note),
                         "latency_s": round(time.time() - t0, 3)})
        rate = (w_pass / w_total) if w_total else 1.0
        return {"version": str(version), "pass_rate": rate,
                "rows": rows}

    def compare(self, old_version: str, new_version: str, *,
                tolerance: float = 0.0) -> dict:
        """Old vs new on identical goldens. blocked=True stops deploy."""
        old = self.run(old_version)
        new = self.run(new_version)
        old_map = {r["case"]: r["ok"] for r in old["rows"]}
        regressions = [r["case"] for r in new["rows"]
                       if not r["ok"] and old_map.get(r["case"], False)]
        fixes = [r["case"] for r in new["rows"]
                 if r["ok"] and not old_map.get(r["case"], True)]
        delta = new["pass_rate"] - old["pass_rate"]
        blocked = bool(regressions) or delta < -float(tolerance)
        return {"old": old["pass_rate"], "new": new["pass_rate"],
                "delta": round(delta, 4), "regressions": regressions,
                "fixes": fixes, "blocked": blocked}
