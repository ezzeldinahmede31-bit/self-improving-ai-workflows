"""External API contract monitoring: detect provider changes early.

Providers move without asking (Google, Telegram, model vendors, payment
rails). Probes — caller callables returning (status, payload_shape,
latency_s, version_string) — run on schedule; each run compares shape,
latency ceiling, error taxonomy, and version pin against the recorded
contract. First deviation opens a finding with before/after evidence;
stable runs just refresh the last-green stamp.

Only stdlib is used. Probes perform the actual calls.
"""

from __future__ import annotations

import time


class ApiMonitor:
    """Contract watch per external API with change findings."""

    def __init__(self):
        self._contracts: dict[str, dict] = {}
        self._probes: dict[str, object] = {}
        self.findings: list[dict] = []

    def watch(self, name: str, probe, *, expected_keys: list[str],
              max_latency_s: float, known_errors: list[str],
              version: str) -> None:
        """Register an API with its probe + contract expectations."""
        if not callable(probe):
            raise TypeError("probe must be callable")
        self._contracts[str(name)] = {
            "keys": [str(k) for k in expected_keys],
            "max_latency_s": float(max_latency_s),
            "errors": [str(e) for e in known_errors],
            "version": str(version), "last_green": None}

    def check(self, name: str) -> dict:
        """Run one probe; compare; record finding on first deviation."""
        spec = self._contracts.get(str(name))
        if spec is None:
            return {"api": str(name), "ok": False,
                    "reason": "unwatched"}
        return self._run(str(name), spec)

    def attach(self, name: str, probe) -> None:
        """Bind the probe callable after watch() (split registration)."""
        if name not in self._contracts:
            raise KeyError(f"unwatched api: {name}")
        if not callable(probe):
            raise TypeError("probe must be callable")
        self._probes[str(name)] = probe

    def _run(self, name: str, spec: dict) -> dict:
        fn = self._probes.get(name)
        if fn is None:
            return {"api": name, "ok": False, "reason": "no probe bound"}
        try:
            status, shape, lat, ver = fn()
        except Exception as exc:  # noqa: BLE001 - finding, not crash
            finding = {"api": name, "ts": time.time(),
                       "kind": "probe-raised", "detail": str(exc)}
            self.findings.append(finding)
            return {"api": name, "ok": False, "finding": finding}
        deviations = []
        missing = [k for k in spec["keys"] if k not in (shape or {})]
        if missing:
            deviations.append(f"shape lost keys: {missing}")
        if lat > spec["max_latency_s"]:
            deviations.append(f"latency {lat:.2f}s over "
                              f"{spec['max_latency_s']}s")
        if str(ver) != spec["version"]:
            deviations.append(f"version {ver} vs pinned {spec['version']}")
        if status not in ("ok",) + tuple(spec["errors"]):
            deviations.append(f"unknown status: {status}")
        if deviations:
            finding = {"api": name, "ts": time.time(),
                       "kind": "contract-change", "detail": deviations}
            self.findings.append(finding)
            return {"api": name, "ok": False, "finding": finding}
        spec["last_green"] = time.time()
        return {"api": name, "ok": True}
