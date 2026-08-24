"""Tests for scripts/n8n_stability_verifier.py + StabilityGate integration
in scripts/build_gates_pipeline.py."""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import pytest

from scripts import n8n_stability_verifier as sv
from scripts.build_gates_pipeline import StabilityGate, run_pipeline


class _SilentReporter:
    def __init__(self):
        self.json_out = False

    def stage(self, name, status, violations=None, score=None, warnings=None):
        pass


def _wf(nodes, connections=None, extra=None):
    wf = {"name": "t", "nodes": nodes, "connections": connections or {}}
    if extra:
        wf.update(extra)
    return wf


def _run(artifact, hitl=False):
    return run_pipeline(artifact, str(artifact), hitl, _SilentReporter())


class _FakeClock:
    """Advancing fake clock: time() increments each call so a polling loop
    reaches its deadline instead of spinning forever (avoids real sleeps and
    the bound-method trap of `type("_T", (), {...})` class attributes)."""

    def __init__(self):
        self._now = 0

    def time(self):
        self._now += 1
        return self._now

    def sleep(self, seconds):
        pass


# ---------------- compare_with_expected ----------------

class TestCompareWithExpected:
    def test_exact_match(self):
        assert sv.compare_with_expected({"a": 1, "b": [1, 2]}, {"b": [1, 2], "a": 1}) is True

    def test_mismatch(self):
        assert sv.compare_with_expected({"a": 1}, {"a": 2}) is False

    def test_expected_none_always_false(self):
        assert sv.compare_with_expected({"a": 1}, None) is False
        assert sv.compare_with_expected(None, None) is False


# ---------------- trigger_workflow_execution (mocked) ----------------

class TestTriggerWorkflowExecution:
    @pytest.fixture(autouse=True)
    def _api_key(self, monkeypatch):
        monkeypatch.setattr(sv, "N8N_API_KEY", "test-key")

    def test_no_api_key(self, monkeypatch):
        monkeypatch.setattr(sv, "N8N_API_KEY", "")
        res = sv.trigger_workflow_execution("wf1", {}, api_key="")
        assert res["success"] is False
        assert "N8N_API_KEY" in res["reason"]

    def test_http_error(self, monkeypatch):
        class _Resp:
            status_code = 500
            text = "boom"

        monkeypatch.setattr(sv.requests, "post", lambda *a, **k: _Resp())
        res = sv.trigger_workflow_execution("wf1", {"x": 1})
        assert res["success"] is False
        assert "500" in res["reason"]
        assert res["node_failed"] is None

    def test_exec_error_with_node(self, monkeypatch):
        class _Resp:
            status_code = 200
            text = ""

            def json(self):
                return {"data": {"resultData": {"error": {"message": "oops",
                                                          "node": {"name": "Fetch Homepage"}}}}}

        monkeypatch.setattr(sv.requests, "post", lambda *a, **k: _Resp())
        res = sv.trigger_workflow_execution("wf1", {})
        assert res["success"] is False
        assert res["node_failed"] == "Fetch Homepage"
        assert "oops" in res["reason"]

    def test_not_finished(self, monkeypatch):
        class _Resp:
            status_code = 200
            text = ""

            def json(self):
                return {"data": {"finished": False, "resultData": {}}}

        monkeypatch.setattr(sv.requests, "post", lambda *a, **k: _Resp())
        res = sv.trigger_workflow_execution("wf1", {})
        assert res["success"] is False
        assert "did not finish" in res["reason"]

    def test_success(self, monkeypatch):
        class _Resp:
            status_code = 200
            text = ""

            def json(self):
                return {"data": {"finished": True,
                                 "resultData": {"runData": {"out": [1]}}}}

        monkeypatch.setattr(sv.requests, "post", lambda *a, **k: _Resp())
        res = sv.trigger_workflow_execution("wf1", {"in": 1})
        assert res["success"] is True
        assert res["output"] == {"out": [1]}
        assert res["duration_sec"] >= 0

    def test_timeout(self, monkeypatch):
        import requests

        def _raise(*a, **k):
            raise requests.exceptions.Timeout()

        monkeypatch.setattr(sv.requests, "post", _raise)
        res = sv.trigger_workflow_execution("wf1", {})
        assert res["success"] is False
        assert "Timed out" in res["reason"]

    def test_connection_error(self, monkeypatch):
        import requests

        def _raise(*a, **k):
            raise requests.exceptions.ConnectionError("refused")

        monkeypatch.setattr(sv.requests, "post", _raise)
        res = sv.trigger_workflow_execution("wf1", {})
        assert res["success"] is False
        assert "Cannot reach" in res["reason"]


# ---------------- verify_stability ----------------

class TestVerifyStability:
    def test_stable_verified_on_five_consecutive(self, monkeypatch):
        calls = {"n": 0}

        def _ok(wf, test_input, **kwargs):
            calls["n"] += 1
            return {"success": True, "output": {"out": "x"}}

        monkeypatch.setattr(sv, "trigger_workflow_execution", _ok)
        res = sv.verify_stability("wf1", {"in": 1}, {"out": "x"})
        assert res.status == "STABLE_VERIFIED"
        assert res.consecutive_reached == 5
        assert res.max_consecutive_reached == 5
        assert res.pattern == "STABLE"
        assert calls["n"] == 5

    def test_flat_failure_from_first_attempt(self, monkeypatch):
        def _fail(wf, test_input, **kwargs):
            return {"success": False, "reason": "exec error"}

        monkeypatch.setattr(sv, "trigger_workflow_execution", _fail)
        res = sv.verify_stability("wf1", {}, {"out": "x"})
        assert res.status == "UNSTABLE_REJECTED"
        assert res.pattern == "FLAT_FAILURE"
        assert res.consecutive_reached == 0
        assert res.max_consecutive_reached == 0
        assert len(res.attempts_log) == sv.MAX_TOTAL_ATTEMPTS

    def test_flaky_3_then_fail_then_2(self, monkeypatch):
        # Repeating 3-successes-then-failure pattern: never reaches 5
        # consecutive, so the loop exhausts MAX_TOTAL_ATTEMPTS and the verifier
        # must classify the failure as FLAKY (max consecutive >= 1).
        pattern = [True, True, True, False]
        calls = {"i": 0}

        def _seq(wf, test_input, **kwargs):
            ok = pattern[calls["i"] % len(pattern)]
            calls["i"] += 1
            if ok:
                return {"success": True, "output": {"out": "x"}}
            return {"success": False, "reason": "flaky"}

        monkeypatch.setattr(sv, "trigger_workflow_execution", _seq)
        res = sv.verify_stability("wf1", {}, {"out": "x"})
        assert res.status == "UNSTABLE_REJECTED"
        assert res.pattern == "FLAKY"
        assert res.max_consecutive_reached == 3
        assert res.consecutive_reached == 3
        assert calls["i"] == sv.MAX_TOTAL_ATTEMPTS

    def test_match_requires_exact_expected(self, monkeypatch):
        calls = {"n": 0}

        def _ok(wf, test_input, **kwargs):
            calls["n"] += 1
            return {"success": True, "output": {"out": "DIFFERENT"}}

        monkeypatch.setattr(sv, "trigger_workflow_execution", _ok)
        res = sv.verify_stability("wf1", {}, {"out": "expected"})
        assert res.status == "UNSTABLE_REJECTED"
        assert res.pattern == "FLAT_FAILURE"
        assert res.max_consecutive_reached == 0

    def test_expected_none_never_stable(self, monkeypatch):
        def _ok(wf, test_input, **kwargs):
            return {"success": True, "output": {"out": "x"}}

        monkeypatch.setattr(sv, "trigger_workflow_execution", _ok)
        res = sv.verify_stability("wf1", {}, None)
        assert res.status == "UNSTABLE_REJECTED"
        assert res.max_consecutive_reached == 0

    def test_empty_workflow_id_rejected(self, monkeypatch):
        res = sv.verify_stability("", {}, {"a": 1})
        assert res.status == "UNSTABLE_REJECTED"

    def test_to_dict_shape(self):
        r = sv.StabilityResult("STABLE_VERIFIED", [], 5, 5, "STABLE")
        d = r.to_dict()
        assert d["status"] == "STABLE_VERIFIED"
        assert d["pattern"] == "STABLE"
        assert d["consecutive_reached"] == 5
        assert d["max_consecutive_reached"] == 5


# ---------------- get_execution_method / webhook trigger ----------------

class TestExecutionMethodAndWebhook:
    def test_webhook_detected(self):
        wf = {"nodes": [{"type": "n8n-nodes-base.webhook", "parameters": {"path": "x"}},
                        {"type": "n8n-nodes-base.code"}]}
        assert sv.get_execution_method(wf) == "webhook"

    def test_formtrigger_detected(self):
        wf = {"nodes": [{"type": "n8n-nodes-base.formTrigger"}]}
        assert sv.get_execution_method(wf) == "webhook"

    def test_no_trigger_defaults_cli(self):
        wf = {"nodes": [{"type": "n8n-nodes-base.manualTrigger"}]}
        assert sv.get_execution_method(wf) == "cli"

    def test_empty_workflow_cli(self):
        assert sv.get_execution_method({"nodes": []}) == "cli"

    def test_webhook_trigger_path_found(self):
        wf = {"nodes": [{"type": "n8n-nodes-base.webhook",
                         "parameters": {"path": "/eu-brands", "httpMethod": "POST"}}]}
        path, method = sv._webhook_trigger_path(wf)
        assert path == "/eu-brands"
        assert method == "POST"

    def test_webhook_trigger_path_missing(self):
        path, method = sv._webhook_trigger_path({"nodes": [{"type": "n8n-nodes-base.code"}]})
        assert path is None
        assert method == "POST"

    def test_fetch_workflow_ok(self, monkeypatch):
        class _Resp:
            status_code = 200

            def json(self):
                return {"id": "wf1", "nodes": []}

        monkeypatch.setattr(sv.requests, "get", lambda *a, **k: _Resp())
        monkeypatch.setattr(sv, "N8N_API_KEY", "k")
        assert sv.fetch_workflow("wf1")["id"] == "wf1"

    def test_fetch_workflow_no_key(self, monkeypatch):
        monkeypatch.setattr(sv, "N8N_API_KEY", "")
        assert sv.fetch_workflow("wf1") == {}

    def test_fetch_workflow_error(self, monkeypatch):
        class _Resp:
            status_code = 404

            def json(self):
                return {}

        monkeypatch.setattr(sv.requests, "get", lambda *a, **k: _Resp())
        monkeypatch.setattr(sv, "N8N_API_KEY", "k")
        assert sv.fetch_workflow("wf1") == {}


class TestTriggerWebhook:
    @pytest.fixture(autouse=True)
    def _api_key(self, monkeypatch):
        monkeypatch.setattr(sv, "N8N_API_KEY", "test-key")

    def test_webhook_no_path_in_workflow(self, monkeypatch):
        monkeypatch.setattr(sv, "fetch_workflow",
                            lambda *a, **k: {"nodes": [{"type": "n8n-nodes-base.manualTrigger"}]})
        res = sv.trigger_workflow_execution("wf1", {}, method="webhook")
        assert res["success"] is False
        assert "No webhook trigger node" in res["reason"]

    def test_webhook_success_polls_execution(self, monkeypatch):
        posted = {"seen": False}

        class _PostResp:
            status_code = 200
            text = ""

        seq = {"i": 0}

        class _GetResp:
            status_code = 200

            def json(self):
                seq["i"] += 1
                if seq["i"] == 1:
                    return {"data": [{"id": 1}]}   # before = 1
                if seq["i"] == 2:
                    return {"data": [{"id": 2}]}   # new execution
                if seq["i"] == 3:
                    return {"id": 2, "finished": True,
                            "data": {"resultData": {
                                "runData": {
                                    "Double": [{
                                        "data": {"main": [[
                                            {"json": {"result": 42}}
                                        ]]}
                                    }]
                                },
                                "lastNodeExecuted": "Double"}}}
                return {"data": []}

        monkeypatch.setattr(sv.requests, "post", lambda *a, **k: _PostResp())
        monkeypatch.setattr(sv.requests, "get", lambda *a, **k: _GetResp())
        res = sv.trigger_workflow_execution("wf1", {"in": 1}, method="webhook",
                                            webhook_path="/stability-test")
        assert res["success"] is True
        assert res["output"] == [{"result": 42}]
        assert res["execution_id"] == 2

    def test_webhook_http_error(self, monkeypatch):
        class _PostResp:
            status_code = 403
            text = "forbidden"

        monkeypatch.setattr(sv.requests, "post", lambda *a, **k: _PostResp())
        res = sv.trigger_workflow_execution("wf1", {}, method="webhook",
                                            webhook_path="/x")
        assert res["success"] is False
        assert "403" in res["reason"]

    def test_webhook_execution_failed(self, monkeypatch):
        class _PostResp:
            status_code = 200
            text = ""

        seq = {"i": 0}

        def _latest(*a, **k):
            seq["i"] += 1
            return 1 if seq["i"] == 1 else 2

        def _fetch(*a, **k):
            return {"id": 2, "finished": False, "status": "error",
                    "data": {"resultData": {"error": {"message": "boom",
                                                      "node": {"name": "N"}}}}}

        monkeypatch.setattr(sv.requests, "post", lambda *a, **k: _PostResp())
        monkeypatch.setattr(sv, "_latest_execution_id", _latest)
        monkeypatch.setattr(sv, "_fetch_execution", _fetch)
        monkeypatch.setattr(sv, "time", _FakeClock())
        res = sv.trigger_workflow_execution("wf1", {}, method="webhook",
                                            webhook_path="/x")
        assert res["success"] is False
        assert "boom" in res["reason"]
        assert res["node_failed"] == "N"

    def test_webhook_no_finished_execution(self, monkeypatch):
        class _PostResp:
            status_code = 200
            text = ""

        monkeypatch.setattr(sv.requests, "post", lambda *a, **k: _PostResp())
        monkeypatch.setattr(sv, "_latest_execution_id", lambda *a, **k: 1)
        monkeypatch.setattr(sv, "_fetch_execution", lambda *a, **k: {"id": 1, "finished": False})
        monkeypatch.setattr(sv, "time", _FakeClock())
        res = sv.trigger_workflow_execution("wf1", {}, method="webhook",
                                            webhook_path="/x")
        assert res["success"] is False
        assert "no finished execution" in res["reason"]

    def test_cli_requires_shell(self):
        res = sv.trigger_workflow_execution("wf1", {}, method="cli")
        assert res["success"] is False
        assert "shell access" in res["reason"]

    def test_webhook_timeout(self, monkeypatch):
        import requests

        def _raise(*a, **k):
            raise requests.exceptions.Timeout()

        monkeypatch.setattr(sv.requests, "post", _raise)
        res = sv.trigger_workflow_execution("wf1", {}, method="webhook",
                                            webhook_path="/x")
        assert res["success"] is False
        assert "Timed out" in res["reason"]


class TestVerifyStabilityMethodPassthrough:
    def test_verify_stability_uses_webhook_method(self, monkeypatch):
        seen = {}

        def _trig(wf, test_input, method=None, webhook_path=None):
            seen["method"] = method
            seen["webhook_path"] = webhook_path
            return {"success": True, "output": {"out": "x"}}

        monkeypatch.setattr(sv, "trigger_workflow_execution", _trig)
        res = sv.verify_stability("wf1", {}, {"out": "x"}, method="webhook",
                                  webhook_path="/stability-test")
        assert res.status == "STABLE_VERIFIED"
        assert seen["method"] == "webhook"
        assert seen["webhook_path"] == "/stability-test"

    def test_verify_stability_legacy_default(self, monkeypatch):
        seen = {}

        def _trig(wf, test_input, method=None, webhook_path=None):
            seen["method"] = method
            return {"success": True, "output": {"out": "x"}}

        monkeypatch.setattr(sv, "trigger_workflow_execution", _trig)
        res = sv.verify_stability("wf1", {}, {"out": "x"})
        assert res.status == "STABLE_VERIFIED"
        assert seen["method"] is None




class TestLogAttempt:
    def test_failed_attempt_written(self, tmp_path, monkeypatch):
        log = tmp_path / "n8n_error_patterns.md"
        monkeypatch.setattr(sv, "ERROR_LOG_PATH", log)
        sv.log_attempt("wf1", 3, 2, {"success": False, "reason": "boom",
                                     "node_failed": "HTTP Request"})
        text = log.read_text(encoding="utf-8")
        assert "workflow=wf1" in text
        assert "attempt=3" in text
        assert "consecutive_before_fail=2" in text
        assert "node=HTTP Request" in text

    def test_success_not_logged(self, tmp_path, monkeypatch):
        log = tmp_path / "n8n_error_patterns.md"
        monkeypatch.setattr(sv, "ERROR_LOG_PATH", log)
        sv.log_attempt("wf1", 1, 0, {"success": True, "reason": ""})
        assert not log.exists()


# ---------------- StabilityGate ----------------

class TestStabilityGate:
    def test_skip_without_annotation(self):
        g = StabilityGate()
        assert g.run({})["status"] == "SKIP"

    def test_fail_missing_workflow_id(self):
        g = StabilityGate()
        res = g.run({"stability": {"test_input": {}, "expected_output": {"a": 1}}})
        assert res["status"] == "FAIL"
        assert "workflow_id" in res["violations"][0]

    def test_fail_missing_expected_output_rule5(self):
        g = StabilityGate()
        res = g.run({"stability": {"workflow_id": "wf1", "test_input": {}}})
        assert res["status"] == "FAIL"
        assert "design time" in res["violations"][0]

    def test_fail_no_api_key_fail_closed(self, monkeypatch):
        monkeypatch.setattr("scripts.build_gates_pipeline.N8N_API_KEY", "")
        g = StabilityGate()
        res = g.run({"stability": {"workflow_id": "wf1", "test_input": {},
                                   "expected_output": {"a": 1}}})
        assert res["status"] == "FAIL"
        assert "N8N_API_KEY" in res["violations"][0]

    def test_pass_on_stable_verified(self, monkeypatch):
        monkeypatch.setattr("scripts.build_gates_pipeline.N8N_API_KEY", "k")

        class _Res:
            status = "STABLE_VERIFIED"
            pattern = "STABLE"
            max_consecutive_reached = 5

            def to_dict(self):
                return {"status": "STABLE_VERIFIED", "pattern": "STABLE",
                        "consecutive_reached": 5, "max_consecutive_reached": 5,
                        "attempts_log": []}

        monkeypatch.setattr("scripts.build_gates_pipeline.verify_stability",
                            lambda *a, **k: _Res())
        g = StabilityGate()
        res = g.run({"stability": {"workflow_id": "wf1", "test_input": {},
                                   "expected_output": {"a": 1}}})
        assert res["status"] == "PASS"
        assert "STABLE_VERIFIED" in res["violations"][0]

    def test_fail_flaky_signal(self, monkeypatch):
        monkeypatch.setattr("scripts.build_gates_pipeline.N8N_API_KEY", "k")

        class _Res:
            status = "UNSTABLE_REJECTED"
            pattern = "FLAKY"
            max_consecutive_reached = 3
            attempts_log = [1, 2, 3]

            def to_dict(self):
                return {"status": "UNSTABLE_REJECTED", "pattern": "FLAKY",
                        "consecutive_reached": 2, "max_consecutive_reached": 3,
                        "attempts_log": self.attempts_log}

        monkeypatch.setattr("scripts.build_gates_pipeline.verify_stability",
                            lambda *a, **k: _Res())
        g = StabilityGate()
        res = g.run({"stability": {"workflow_id": "wf1", "test_input": {},
                                   "expected_output": {"a": 1}}})
        assert res["status"] == "FAIL"
        assert "FLAKY" in res["violations"][0]

    def test_fail_flat_signal(self, monkeypatch):
        monkeypatch.setattr("scripts.build_gates_pipeline.N8N_API_KEY", "k")

        class _Res:
            status = "UNSTABLE_REJECTED"
            pattern = "FLAT_FAILURE"
            max_consecutive_reached = 0
            attempts_log = [1, 2, 3]

            def to_dict(self):
                return {"status": "UNSTABLE_REJECTED", "pattern": "FLAT_FAILURE",
                        "consecutive_reached": 0, "max_consecutive_reached": 0,
                        "attempts_log": self.attempts_log}

        monkeypatch.setattr("scripts.build_gates_pipeline.verify_stability",
                            lambda *a, **k: _Res())
        g = StabilityGate()
        res = g.run({"stability": {"workflow_id": "wf1", "test_input": {},
                                   "expected_output": {"a": 1}}})
        assert res["status"] == "FAIL"
        assert "FLAT_FAILURE" in res["violations"][0]


# ---------------- run_pipeline integration ----------------

class TestPipelineStabilityStage:
    def _wf_ok(self, extra=None):
        """Workflow that passes SECURITY + QUALITY + INTEGRITY (webhook trigger
        with pinned data + HTTP request with verb name)."""
        wf = _wf([
            {"id": "1", "name": "Receive Webhook", "type": "n8n-nodes-base.webhook",
             "typeVersion": 2, "position": [0, 0],
             "parameters": {"path": "h", "pinnedData": {"1": {"json": {"id": 1}}},
                            "authentication": "headerAuth"}},
            {"id": "2", "name": "Send HTTP Response", "type": "n8n-nodes-base.httpRequest",
             "typeVersion": 2, "position": [240, 0], "parameters": {}},
        ], {"Receive Webhook": {"main": [{"node": "Send HTTP Response"}]}})
        if extra:
            wf.update(extra)
        return wf

    def test_skipped_by_default(self):
        res = _run(self._wf_ok())
        stage = res["stages"]["stability"]
        assert stage["status"] == "SKIP"
        assert res["verdict"] == "READY_FOR_DEPLOYMENT"

    def test_stability_fail_yields_stability_violation(self, monkeypatch):
        monkeypatch.setattr("scripts.build_gates_pipeline.N8N_API_KEY", "k")

        class _Res:
            status = "UNSTABLE_REJECTED"
            pattern = "FLAT_FAILURE"
            max_consecutive_reached = 0
            attempts_log = [1, 2]

            def to_dict(self):
                return {"status": "UNSTABLE_REJECTED", "pattern": "FLAT_FAILURE",
                        "consecutive_reached": 0, "max_consecutive_reached": 0,
                        "attempts_log": self.attempts_log}

        monkeypatch.setattr("scripts.build_gates_pipeline.verify_stability",
                            lambda *a, **k: _Res())
        wf = self._wf_ok({"_gates": {"stability": {"workflow_id": "wf1",
                                                   "test_input": {},
                                                   "expected_output": {"a": 1}}}})
        res = _run(wf)
        assert res["stages"]["stability"]["status"] == "FAIL"
        assert res["verdict"] == "STABILITY_VIOLATION"
        assert res["reason_code"] == "UNSTABLE_OR_UNVERIFIED"

    def test_stability_pass_reaches_readiness(self, monkeypatch):
        monkeypatch.setattr("scripts.build_gates_pipeline.N8N_API_KEY", "k")

        class _Res:
            status = "STABLE_VERIFIED"
            pattern = "STABLE"
            max_consecutive_reached = 5

            def to_dict(self):
                return {"status": "STABLE_VERIFIED", "pattern": "STABLE",
                        "consecutive_reached": 5, "max_consecutive_reached": 5,
                        "attempts_log": []}

        monkeypatch.setattr("scripts.build_gates_pipeline.verify_stability",
                            lambda *a, **k: _Res())
        wf = self._wf_ok({"_gates": {"stability": {"workflow_id": "wf1",
                                                   "test_input": {},
                                                   "expected_output": {"a": 1}}}})
        res = _run(wf)
        assert res["stages"]["stability"]["status"] == "PASS"
        assert res["verdict"] == "READY_FOR_DEPLOYMENT"
