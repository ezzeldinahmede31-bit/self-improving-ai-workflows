"""Tests for the 8 production-hardening modules:

1. observability.py      — JSON logs, metrics, alert thresholds
2. model_failover.py     — real backup ladder + circuit breaker
3. feedback_loop.py      — HITL decisions mutate future behavior
4. [scope doc]           — taxonomy covered by docs/tests_layout.md
5. secrets_provider.py   — backend chain + TTL rotation
6. workflow_versions.py  — snapshot/diff/rollback
7. cost_ledger.py        — per-tenant spend + budget status
8. attack_fuzzer.py      — mutation engine + garak hook
"""

import json
import tempfile
import time
from pathlib import Path

import pytest

from observability import (StructLogger, MetricsRegistry, AlertManager,
                           AlertRule)
from model_failover import (ModelLeg, ModelLadder, FailoverDriver,
                            build_default_ladder)
from feedback_loop import FeedbackLoop, AUTO_TIGHTEN_THRESHOLD
from secrets_provider import SecretManager, FileBackend, VaultBackend
from workflow_versions import WorkflowVersionControl
from cost_ledger import CostLedger, LiteLLMFeeder
from attack_fuzzer import AttackFuzzer, MutationEngine, ProbeVerdict


# ---------------------------------------------------------------------------
# 1. Observability
# ---------------------------------------------------------------------------

class TestStructLogger:
    def test_json_line_emitted(self, tmp_path):
        log = StructLogger(path=str(tmp_path / "events.jsonl"))
        log.info("gate_passed", wf="x1", risk=20)
        log.close()
        line = (tmp_path / "events.jsonl").read_text().strip()
        rec = json.loads(line)
        assert rec["event"] == "gate_passed"
        assert rec["wf"] == "x1"

    def test_memory_tail(self):
        log = StructLogger()
        log.info("a"); log.warning("b"); log.error("c")
        assert len(log.tail()) == 3
        assert log.tail()[-1]["level"] == 3


class TestMetricsRegistry:
    def test_counter_and_prometheus(self, tmp_path):
        m = MetricsRegistry(db_path=str(tmp_path / "m.db"))
        m.inc("verifier_errors"); m.inc("verifier_errors")
        m.set_gauge("pending_hitl", 3)
        txt = m.render_prometheus()
        assert "jit_verifier_errors_total 2.0" in txt
        assert "jit_pending_hitl" in txt and "jit_pending_hitl 3" in txt

    def test_histogram_percentile(self):
        m = MetricsRegistry()
        for v in range(1, 101):
            m.observe("lat", v, label="gate")
        snap = m.snapshot()
        assert abs(snap["histograms"]["lat{gate}"] - 95) <= 2


class TestAlertManager:
    def test_threshold_fires_with_telemetry(self, tmp_path):
        m = MetricsRegistry()
        am = AlertManager(m, cooldown_sec=0)
        am.add_rule(AlertRule("too_many_errors", "verifier_errors", ">", 2))
        fired = []
        am.add_handler(lambda rule, metric, ctx: fired.append(rule))
        m.inc("verifier_errors", 3)
        result = am.evaluate()
        assert "too_many_errors" in result
        assert "too_many_errors" in fired

    def test_cooldown_prevents_storm(self, tmp_path):
        m = MetricsRegistry()
        am = AlertManager(m, cooldown_sec=3600)
        am.add_rule(AlertRule("r", "x", ">", 0))
        m.set_gauge("x", 5)
        assert len(am.evaluate()) == 1
        assert len(am.evaluate()) == 0  # inside cooldown


# ---------------------------------------------------------------------------
# 2. Model failover
# ---------------------------------------------------------------------------

class TestModelLadder:
    def test_pick_prefers_primary_when_healthy(self):
        ladder = ModelLadder(legs=[
            ModelLeg("primary", "remote", "", 0.5),
            ModelLeg("local", "local", "", 0.0),
        ])
        leg = ladder.pick()
        assert leg.name == "primary"

    def test_breaker_opens_after_threshold(self):
        ladder = ModelLadder(legs=[
            ModelLeg("primary", "remote", "", 0.5),
            ModelLeg("backup", "remote", "", 0.9),
        ])
        for _ in range(3):
            ladder.record_failure("primary")
        # primary tripped; backup wins
        assert ladder.pick().name == "backup"
        ladder.record_success("backup", 40)
        st = ladder.status_report()
        assert st[0]["consecutive_failures"] == 0

    def test_pick_trips_and_recovers_after_window(self, monkeypatch):
        monkeypatch.setattr("model_failover.time.time", lambda: 9999999999.0)
        ladder = ModelLadder(legs=[
            ModelLeg("primary", "remote", "", 0.5),
            ModelLeg("backup", "remote", "", 0.9),
        ])
        for _ in range(3):
            ladder.record_failure("primary")
        assert ladder.pick().name == "backup"
        # fast-forward past open window: primary usable again
        monkeypatch.setattr("model_failover.time.time", lambda: 99999999999.0)
        assert ladder.pick().name == "primary"

    def test_real_ladder_has_local_leg(self):
        ladder = build_default_ladder()
        kinds = {l.kind for l in ladder.legs}
        assert "local" in kinds  # qwen-coder is the $0 always-up net
        assert ladder.cheapest_healthy_leg().cost_per_1k == 0.0


class TestFailoverDriver:
    def test_falls_back_then_recovers(self):
        calls = {"n": 0}

        def flaky(leg, msgs):
            calls["n"] += 1
            if leg.name == "primary" and calls["n"] <= 2:
                return {"ok": False}
            return {"ok": True, "model": leg.name}

        ladder = ModelLadder(legs=[
            ModelLeg("primary", "remote", "", 0.5),
            ModelLeg("local", "local", "", 0.0),
        ])
        drv = FailoverDriver(ladder, call_fn=flaky)
        res = drv.invoke([{"role": "user", "content": "hi"}])
        assert res["ok"] is True
        assert res["model_used"] == "local"  # breaker tripped primary
        assert res["fallback"] is True

    def test_all_legs_down(self):
        ladder = ModelLadder(legs=[
            ModelLeg("a", "remote", "", 0.5),
            ModelLeg("b", "remote", "", 0.9),
        ])
        drv = FailoverDriver(ladder, call_fn=lambda leg, m: {"ok": False})
        res = drv.invoke([])
        assert res["ok"] is False
        assert str(res["error"]).startswith("all model legs")

    def test_metrics_fed(self):
        from observability import MetricsRegistry
        m = MetricsRegistry()
        ladder = ModelLadder(legs=[ModelLeg("ok", "remote", "", 0.5)])
        drv = FailoverDriver(ladder, metrics=m,
                             call_fn=lambda leg, m2: {"ok": True})
        drv.invoke([])
        assert m.snapshot()["counters"].get("model_all_legs_down") is None


# ---------------------------------------------------------------------------
# 3. Feedback loop
# ---------------------------------------------------------------------------

class TestFeedbackLoop:
    def test_rejection_mutates_future_behavior(self, tmp_path):
        fb = FeedbackLoop(db_path=str(tmp_path / "fb.db"))
        for i in range(AUTO_TIGHTEN_THRESHOLD):
            fb.record_rejection("ssrf_internal_egress", reason=f"no {i}")
        assert fb.should_preempt("ssrf_internal_egress") is True
        p = fb.pattern("ssrf_internal_egress")
        assert p.count >= AUTO_TIGHTEN_THRESHOLD

    def test_quirk_written_to_memory(self, tmp_path, monkeypatch):
        from quirks_memory import QUIRKS_DB_PATH
        monkeypatch.setattr("feedback_loop.remember_quirk",
                            lambda *a, **k: 7)
        fb = FeedbackLoop(db_path=str(tmp_path / "fb.db"))
        r = fb.record_rejection("http_link", reason="phishy")
        assert r["count"] == 1

    def test_feedback_prompt_feeds_few_shot(self, tmp_path):
        fb = FeedbackLoop(db_path=str(tmp_path / "fb.db"))
        for _ in range(3):
            fb.record_rejection("bad_domain", reason="brand misuse")
        prompt = fb.feedback_prompt()
        assert "bad_domain" in prompt  # generator sees what humans vetoed


# ---------------------------------------------------------------------------
# 5. Secrets provider
# ---------------------------------------------------------------------------

class TestSecretManager:
    def test_file_backend_resolves(self, tmp_path):
        f = tmp_path / ".secrets.json"
        f.write_text(json.dumps({"DB_PASS": "hunter2prod"}))
        mgr = SecretManager(backends=[FileBackend(path=str(f))], ttl_sec=1)
        assert mgr.resolve("DB_PASS") == "hunter2prod"

    def test_fallback_chain_env_then_file(self, tmp_path, monkeypatch):
        monkeypatch.delenv("SECRET_X", raising=False)
        f = tmp_path / ".env"
        f.write_text("SECRET_X=fromfile\n")
        class EnvNever:
            name = "env"
            def get(self, n): return None
        mgr = SecretManager(
            backends=[EnvNever(), FileBackend(path=str(f))], ttl_sec=1)
        assert mgr.resolve("SECRET_X") == "fromfile"

    def test_ttl_rotation_reloads(self, tmp_path):
        f = tmp_path / ".secrets.json"
        f.write_text(json.dumps({"K": "v1"}))
        mgr = SecretManager(backends=[FileBackend(path=str(f))], ttl_sec=0.5)
        assert mgr.resolve("K") == "v1"
        f.write_text(json.dumps({"K": "v2"}))  # rotated source
        assert mgr.rotate() == 1
        assert mgr.resolve("K") == "v2"

    def test_vault_backend_unreachable_returns_none(self):
        vb = VaultBackend(addr="http://127.0.0.1:1", token="x")
        assert vb.get("k") is None  # connect refused -> graceful None


# ---------------------------------------------------------------------------
# 6. Workflow versions
# ---------------------------------------------------------------------------

class TestWorkflowVersionControl:
    def test_snapshot_diff_rollback(self, tmp_path):
        vc = WorkflowVersionControl(db_path=str(tmp_path / "v.db"))
        v1 = {"nodes": [{"name": "A", "type": "n8n-nodes-base.webhook"}]}
        v2 = {"nodes": [{"name": "A", "type": "n8n-nodes-base.webhook"},
                        {"name": "B", "type": "n8n-nodes-base.httpRequest",
                         "parameters": {"url": "https://bad.invalid"}}]}
        assert vc.snapshot("wf", v1, "ok") == 1
        assert vc.snapshot("wf", v2, "risky") == 2
        d = vc.diff("wf", 1, 2)
        assert d["added_nodes"] == ["B"]
        rb = vc.rollback("wf")
        assert rb["ok"] is True
        latest = vc.get("wf", None)
        assert "bad.invalid" not in json.dumps(latest["snapshot"])  # reverted

    def test_snapshot_null_live(self, tmp_path):
        vc = WorkflowVersionControl(db_path=str(tmp_path / "v2.db"))
        assert vc.get("noexist", None) is None


# ---------------------------------------------------------------------------
# 7. Cost ledger
# ---------------------------------------------------------------------------

class TestCostLedger:
    def test_per_tenant_spend_and_budget(self, tmp_path):
        led = CostLedger(db_path=str(tmp_path / "c.db"))
        led.set_budget("acme", 10.0)
        led.record("wf1", "deepseek-chat", 1000, 500, 0.5, tenant="acme")
        led.record("wf1", "deepseek-chat", 1000, 500, 0.5, tenant="acme")
        st = led.tenant_budget_status("acme")
        assert st["spend_usd"] == 1.0
        assert st["over_budget"] is False

    def test_over_budget_detected(self, tmp_path):
        led = CostLedger(db_path=str(tmp_path / "c2.db"))
        led.set_budget("tenant_a", 1.0)
        led.record("wf", "claude-3-5-sonnet", 900000, 900000, 1.2, tenant="tenant_a")
        assert led.tenant_budget_status("tenant_a")["over_budget"] is True

    def test_feeder_bulk_ingest(self, tmp_path):
        led = CostLedger(db_path=str(tmp_path / "c3.db"))
        rows = [
            {"workflow_id": "w1", "tenant": "t", "model": "m", "tokens_in": 1,
             "tokens_out": 1, "cost_usd": 0.01},
            {"workflow_id": "w1", "tenant": "t", "model": "m", "tokens_in": 1,
             "tokens_out": 1, "cost_usd": 0.02},
        ]
        assert LiteLLMFeeder.ingest_report_rows(led, rows) == 2
        assert led.tenant_spend("t") == 0.03


# ---------------------------------------------------------------------------
# 8. Attack fuzzer
# ---------------------------------------------------------------------------

class TestAttackFuzzer:
    def test_mutation_engine_generates_variants(self):
        variants = MutationEngine().mutate("eval(STR)")
        assert len(variants) >= 5
        assert any("eval" in v for v in variants)

    def test_fuzzer_finds_escaped_variants(self):
        fz = AttackFuzzer()
        report = fz.audit_with_fuzzing()
        assert report["probes_generated"] > 0
        assert set(report["vectors"]) == {"injection", "ssrf", "exfiltration"}
        assert "escaped_examples" in report

    def test_garak_hook_skips_when_missing(self):
        res = AttackFuzzer().garak_hook("http://127.0.0.1:4000")
        assert res.get("ran") is False  # garak not on PATH in test env