"""Production isolation (NF-01 evidence, not documentation).

Proves with EXECUTION (not imports-only claims) that:
1. No production module imports scripts.* / client_portal (static AST gate).
2. A real SystemOrchestrator.execute_workflow_task run never touches the
   known DIRECT sinks (runtime spies that fail the test if called):
   LiteLLMFailover.complete, ModelLadder network probe, VaultBackend.get,
   telegram_alert_handler, DependencyHealth.probe, TieredPipeline.execute.
"""
import ast
import os
import sys
import tempfile

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

# Modules that form the production execution path (root leaves + orchestrator
# package + n8n adapter). scripts/, tests/, client_portal/, skills/ are
# deliberately OUTSIDE this set: ops/dev surfaces, gated below.
PROD_DIRS = [ROOT, os.path.join(ROOT, "orchestrator")]
SKIP_FILES = {
    "tiered_pipeline.py",  # quarantined: exec fail-closed, helpers direct
}


def _prod_files():
    out = []
    for d in PROD_DIRS:
        for name in sorted(os.listdir(d)):
            if not name.endswith(".py"):
                continue
            if name.startswith("test_"):
                continue
            if name in SKIP_FILES:
                continue
            out.append(os.path.join(d, name))
    return out


def _imports_of(path):
    with open(path, encoding="utf-8") as f:
        tree = ast.parse(f.read(), path)
    mods = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for a in node.names:
                mods.add(a.name.split(".")[0])
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                mods.add(node.module.split(".")[0])
    return mods


def test_no_production_import_of_scripts_or_portal():
    offenders = []
    for path in _prod_files():
        mods = _imports_of(path)
        bad = {m for m in mods if m in ("scripts", "client_portal")}
        # relative 'scripts' only counts when it resolves to ./scripts
        if bad:
            offenders.append(f"{os.path.basename(path)}: {sorted(bad)}")
    assert offenders == [], f"production reachable ops imports: {offenders}"


def test_verifier_imports_only_audit_surface_of_tiered():
    """verifier_engine may use the audit log, never the executor."""
    tree_imports = _imports_of(os.path.join(ROOT, "verifier_engine.py"))
    assert "tiered_pipeline" in tree_imports  # audit_log_entry only
    with open(os.path.join(ROOT, "verifier_engine.py"), encoding="utf-8") as f:
        src = f.read()
    assert "PythonExecutor" not in src
    assert ".execute(" not in src


def _benign_workflow():
    return {
        "nodes": [
            {"name": "start", "type": "n8n-nodes-base.webhook",
             "parameters": {}},
            {"name": "fetch", "type": "n8n-nodes-base.httpRequest",
             "parameters": {"url": "https://example.com/api"}},
        ],
        "connections": {"start": {"main": [[{"node": "fetch"}]]}},
    }


def test_production_run_touches_no_direct_sink(monkeypatch):
    """Spies raise if the production path reaches any DIRECT network/exec."""
    import tool_gateway
    import model_failover
    import secrets_provider
    import observability
    import health_probes
    import tiered_pipeline
    import platform_wiring
    from master_system_orchestrator import SystemOrchestrator

    def _boom(*a, **k):
        raise AssertionError("DIRECT sink reached from production path")

    monkeypatch.setattr(tool_gateway.LiteLLMFailover, "complete", _boom)
    monkeypatch.setattr(model_failover.ModelLadder, "_default_probe", _boom)
    monkeypatch.setattr(model_failover.ModelLadder, "probe_all", _boom)
    monkeypatch.setattr(secrets_provider.VaultBackend, "get", _boom)
    monkeypatch.setattr(observability, "telegram_alert_handler",
                        lambda *a, **k: _boom())
    monkeypatch.setattr(health_probes.DependencyHealth, "probe", _boom)
    monkeypatch.setattr(tiered_pipeline.PythonExecutor, "execute", _boom)

    with tempfile.TemporaryDirectory() as tmp:
        orch = SystemOrchestrator(
            budget_usd=5.0,
            enforcement=platform_wiring.EnforcementProfile(
                policy={"default": "allow", "rules": []},
                egress=platform_wiring.EgressPolicy(
                    allow_public_internet=True),
            ),
            evidence_dir=tmp,
            elide_output=True,
        )
        res = orch.execute_workflow_task(
            task_prompt="isolation probe task",
            workflow_json=_benign_workflow(),
            daily_reqs=1,
        )
    assert res["status"] in ("READY_FOR_DEPLOYMENT", "PENDING_HUMAN_REVIEW",
                             "REJECTED", "BUDGET_REJECTED")


def test_audit_outage_is_explicit_never_silent():
    """Phase-13 declaration: audit failure preserves the verdict (denials
    stay denials) but flags the result audit_failed=True + stderr, so no
    consumer mistakes it for a fully-evidenced delivery."""
    import platform_wiring
    from master_system_orchestrator import SystemOrchestrator

    with tempfile.TemporaryDirectory() as tmp:
        orch = SystemOrchestrator(budget_usd=5.0, enforcement=None,
                                  evidence_dir=tmp, elide_output=True)

        class _Broken:
            def append(self, **k):
                raise OSError("disk gone")

        orch.evidence["audit"] = _Broken()
        res = orch.execute_workflow_task(
            task_prompt="audit outage probe",
            workflow_json=_benign_workflow(),
            daily_reqs=1,
        )
    assert res.get("evidence", {}).get("audit_failed") is True
    assert res["status"] in ("READY_FOR_DEPLOYMENT", "PENDING_HUMAN_REVIEW",
                             "REJECTED", "BUDGET_REJECTED")
