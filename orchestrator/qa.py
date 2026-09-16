"""QA gates: deterministic checks over the work directory.

Every acceptance item in the contract is machine-checkable by construction
(schema.py rejects anything else). PASS = all green, else FAIL with details.
"""
from __future__ import annotations
import json
import os

from .worker import scan_secrets, snapshot_files


def run_acceptance(work_dir: str, acceptance: list[dict]) -> list[dict]:
    results: list[dict] = []
    for item in acceptance:
        kind = item.get("kind")
        iid = item.get("id", kind)
        if kind == "file_exists":
            p = os.path.join(work_dir, item.get("path", ""))
            ok = os.path.isfile(p)
            results.append({"id": iid, "passed": ok,
                            "detail": f"exists={ok} :: {item.get('path')}"})
        elif kind == "file_contains":
            p = os.path.join(work_dir, item.get("path", ""))
            try:
                with open(p, "r", errors="ignore") as fh:
                    ok = item.get("text", "") in fh.read()
            except OSError:
                ok = False
            results.append({"id": iid, "passed": ok,
                            "detail": f"contains={ok} :: {item.get('path')}"})
        elif kind == "json_field":
            p = os.path.join(work_dir, item.get("path", ""))
            try:
                with open(p, "r", errors="ignore") as fh:
                    data = json.load(fh)
                cur = data
                for part in str(item.get("field", "")).split("."):
                    cur = cur[part] if isinstance(cur, dict) else None
                ok = cur == item.get("equals")
                detail = f"{item.get('field')}={cur!r} expected={item.get('equals')!r}"
            except (OSError, ValueError, KeyError, TypeError) as e:
                ok, detail = False, f"error: {e}"
            results.append({"id": iid, "passed": ok, "detail": detail})
        elif kind == "no_secrets":
            changed = list(snapshot_files(work_dir))
            hits = scan_secrets(work_dir, changed)
            results.append({"id": iid, "passed": not hits,
                            "detail": f"hits={hits}"})
        else:
            results.append({"id": iid, "passed": False,
                            "detail": f"unknown kind: {kind}"})
    return results


def verdict(results: list[dict]) -> tuple[bool, list[str]]:
    failed = [r["id"] for r in results if not r["passed"]]
    return (not failed, failed)
