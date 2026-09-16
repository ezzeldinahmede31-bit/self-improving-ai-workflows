"""Task Contract schema: small, closed, machine-checkable.

A worker receives ONLY this contract (+ explicit small inputs), never the
project history. Anything not machine-checkable is rejected at validation.
"""
from __future__ import annotations

REQUIRED_FIELDS = ("task_id", "goal", "outputs", "allowed_files",
                   "dependencies", "acceptance", "role")
ACCEPTANCE_KINDS = ("file_exists", "file_contains", "json_field", "no_secrets")

DEFAULTS = {
    "inputs": {},
    "max_attempts": 3,
    "timeout_s": 120,
    "context_limit_bytes": 8192,
    "max_output_bytes": 4096,
    "fallback_role": None,
    "splittable": False,
    "kind": "generic",
}


def with_defaults(raw: dict) -> dict:
    c = dict(DEFAULTS)
    c.update(raw or {})
    return c


def validate(raw: dict) -> list[str]:
    """Return a list of error strings; empty means valid."""
    errors: list[str] = []
    if not isinstance(raw, dict):
        return ["contract must be a dict"]
    for f in REQUIRED_FIELDS:
        if f not in raw:
            errors.append(f"missing required field: {f}")
    if errors:
        return errors
    if not isinstance(raw["task_id"], str) or not raw["task_id"]:
        errors.append("task_id must be a non-empty string")
    if not isinstance(raw["goal"], str) or not raw["goal"]:
        errors.append("goal must be a non-empty string")
    for f in ("outputs", "allowed_files", "dependencies", "acceptance"):
        if not isinstance(raw.get(f), list):
            errors.append(f"{f} must be a list")
    if not isinstance(raw.get("role"), str) or not raw.get("role"):
        errors.append("role must be a non-empty string")
    acc = raw.get("acceptance", [])
    if not acc:
        errors.append("acceptance must be non-empty (every task needs checkable criteria)")
    for i, item in enumerate(acc):
        if not isinstance(item, dict):
            errors.append(f"acceptance[{i}] must be a dict")
            continue
        kind = item.get("kind")
        if kind not in ACCEPTANCE_KINDS:
            errors.append(f"acceptance[{i}].kind must be one of {ACCEPTANCE_KINDS}")
            continue
        if kind in ("file_exists", "file_contains") and not item.get("path"):
            errors.append(f"acceptance[{i}] needs 'path'")
        if kind == "file_contains" and "text" not in item:
            errors.append(f"acceptance[{i}] needs 'text'")
        if kind == "json_field" and (not item.get("path") or "field" not in item):
            errors.append(f"acceptance[{i}] needs 'path' and 'field'")
    for f in ("max_attempts", "timeout_s", "context_limit_bytes", "max_output_bytes"):
        v = raw.get(f, DEFAULTS[f])
        if not isinstance(v, int) or v <= 0:
            errors.append(f"{f} must be a positive int")
    return errors
