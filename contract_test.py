"""Consumer-driven contract testing for integrations.

Each integration declares a contract: input schema (required keys +
types), output schema, error set, timeout ceiling, auth scheme, and
pinned version. verify() runs a caller-supplied probe (live call or
recorded replay) and checks shape, errors, latency, and version —
naming the exact breach (a changed Calendar API breaks here, before
production, not in it). Contracts persist to JSON for CI diffing.

Only stdlib is used. Probes are caller callables (live or replay).
"""

from __future__ import annotations

import json
import time
from pathlib import Path

TYPES = {"str": str, "int": int, "float": float, "bool": bool,
         "list": list, "dict": dict}


def _shape_ok(payload, schema: dict, prefix="") -> list[str]:
    problems = []
    if not isinstance(payload, dict):
        return [f"{prefix or 'root'}: not an object"]
    for key, typ in (schema or {}).items():
        if key not in payload:
            problems.append(f"{prefix}{key}: missing")
        elif typ in TYPES and not isinstance(payload[key], TYPES[typ]):
            problems.append(
                f"{prefix}{key}: want {typ}, got "
                f"{type(payload[key]).__name__}")
    return problems


class ContractRegistry:
    """Contract store + verifier for external integrations."""

    def __init__(self, path: str = "contracts.json"):
        self._path = Path(path)
        self._contracts: dict[str, dict] = {}
        self._load()

    def _load(self) -> None:
        if not self._path.is_file():
            return
        try:
            data = json.loads(self._path.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            return
        if isinstance(data, dict):
            self._contracts = {str(k): v for k, v in data.items()
                               if isinstance(v, dict)}

    def save(self) -> None:
        """Persist contracts (creates parent dirs)."""
        self._path.parent.mkdir(parents=True, exist_ok=True)
        self._path.write_text(json.dumps(self._contracts, sort_keys=True,
                                         indent=1), encoding="utf-8")

    def declare(self, name: str, *, input_schema: dict,
                output_schema: dict, errors: list[str],
                timeout_s: float, auth: str, version: str) -> dict:
        """Pin one integration contract."""
        if timeout_s <= 0:
            raise ValueError("timeout_s must be positive")
        rec = {"input_schema": dict(input_schema),
               "output_schema": dict(output_schema),
               "errors": [str(e) for e in errors],
               "timeout_s": float(timeout_s), "auth": str(auth),
               "version": str(version)}
        self._contracts[str(name)] = rec
        return rec

    def verify(self, name: str, probe) -> dict:
        """Run probe() -> (request, response, latency_s, version) and
        check shape, known errors, latency ceiling, version pin."""
        spec = self._contracts.get(str(name))
        if spec is None:
            return {"integration": str(name), "ok": False,
                    "breaches": ["contract undeclared"]}
        if not callable(probe):
            raise TypeError("probe must be callable")
        breaches = []
        t0 = time.time()
        try:
            req, resp, lat, ver = probe()
        except Exception as exc:  # noqa: BLE001 - breach, not crash
            return {"integration": str(name), "ok": False,
                    "breaches": [f"probe raised: {exc}"]}
        wall = time.time() - t0
        breaches += _shape_ok(req, spec["input_schema"], prefix="in.")
        if isinstance(resp, dict) and "error" in resp:
            if resp["error"] not in spec["errors"]:
                breaches.append(f"unknown error: {resp['error']}")
        else:
            breaches += _shape_ok(resp, spec["output_schema"], prefix="out.")
        if lat > spec["timeout_s"] or wall > spec["timeout_s"] + 5.0:
            breaches.append(f"latency {lat:.2f}s over {spec['timeout_s']}s")
        if str(ver) != spec["version"]:
            breaches.append(f"version drift: live {ver} vs pinned "
                            f"{spec['version']}")
        return {"integration": str(name), "ok": not breaches,
                "breaches": breaches, "latency_s": round(wall, 3)}
