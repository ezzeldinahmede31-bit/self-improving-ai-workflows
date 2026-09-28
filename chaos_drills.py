"""Chaos + disaster-recovery drills: prove recovery, not just backups.

Fault catalog (each fault = name + inject fn + recover fn + assert fn):
dead redis/postgres/n8n/LLM, API timeout, network partition, expired
credential, dead worker, duplicate webhook, malformed payload, clock
drift, full disk. run_drill() injects, asserts degraded-but-safe
behavior, recovers, and re-asserts healthy — recording every phase.
Disaster drills cover destroy->restore->smoke with RPO/RTO stamps:
restore_db, restore_credentials, restore_workflows, restore_config,
then smoke tests. A drill that never ran is reported missing, never
assumed green.

Only stdlib is used. Faults are caller-injected callables (safe by
construction: nothing here touches real infrastructure directly).
"""

from __future__ import annotations

import time

FAULTS = ("dead-redis", "dead-postgres", "dead-n8n", "llm-down",
          "api-timeout", "net-partition", "cred-expired", "worker-dead",
          "dup-webhook", "bad-payload", "clock-drift", "disk-full")


class ChaosDrills:
    """Fault-injection drills with inject/assert/recover phases."""

    def __init__(self):
        self._faults: dict[str, dict] = {}
        self.runs: list[dict] = []

    def register(self, name: str, inject, assert_degraded, recover,
                 assert_healthy) -> None:
        """Register one fault with its four phase callables."""
        if name not in FAULTS:
            raise ValueError(f"unknown fault (see FAULTS): {name}")
        for fn in (inject, assert_degraded, recover, assert_healthy):
            if not callable(fn):
                raise TypeError("all phases must be callable")
        self._faults[name] = {"inject": inject,
                              "assert_degraded": assert_degraded,
                              "recover": recover,
                              "assert_healthy": assert_healthy}

    def run_drill(self, name: str) -> dict:
        """Inject -> assert degraded-safe -> recover -> assert healthy."""
        spec = self._faults.get(str(name))
        if spec is None:
            return {"fault": str(name), "recovered": False,
                    "reason": "fault not registered: drill missing"}
        phases: dict[str, str] = {}
        try:
            spec["inject"]()
            phases["inject"] = "ok"
            spec["assert_degraded"]()
            phases["degraded_safe"] = "ok"
            spec["recover"]()
            phases["recover"] = "ok"
            spec["assert_healthy"]()
            phases["healthy"] = "ok"
            recovered = True
        except Exception as exc:  # noqa: BLE001 - record phase, report
            phases["failed"] = str(exc)
            recovered = False
        out = {"fault": str(name), "ts": time.time(), "phases": phases,
               "recovered": recovered}
        self.runs.append(out)
        return out

    def coverage(self) -> dict:
        """Registered faults vs catalog; unregistered = unproven."""
        have = sorted(self._faults)
        missing = [f for f in FAULTS if f not in self._faults]
        ran = sorted({r["fault"] for r in self.runs if r["recovered"]})
        return {"catalog": list(FAULTS), "registered": have,
                "missing": missing, "proven": ran}


class DisasterDrill:
    """Destroy -> restore (db/creds/workflows/config) -> smoke, with RPO/RTO."""

    STEPS = ("restore_db", "restore_credentials", "restore_workflows",
             "restore_config", "smoke")

    def __init__(self, steps: dict | None = None):
        self._steps = dict(steps or {})

    def run(self) -> dict:
        """Execute restore steps in order, then smoke tests."""
        t0 = time.time()
        done, failed = [], None
        for step in self.STEPS:
            fn = self._steps.get(step)
            if fn is None:
                failed = {"step": step, "error": "step missing: no restore"}
                break
            try:
                fn()
                done.append(step)
            except Exception as exc:  # noqa: BLE001 - record, stop
                failed = {"step": step, "error": str(exc)}
                break
        rto_s = round(time.time() - t0, 2)
        ready = failed is None
        return {"ready": ready, "done": done, "failed": failed,
                "rto_s": rto_s, "rpo": "last verified backup"}
