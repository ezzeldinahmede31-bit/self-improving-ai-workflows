import pytest
import json
import tempfile
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tiered_pipeline import (
    TieredPipeline,
    TaskType,
    Confidence,
    init_audit_db,
    query_audit_log,
    AUDIT_DB_PATH,
)


@pytest.fixture
def temp_db(monkeypatch):
    """Create a temporary database for each test."""
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
        db_path = f.name

    monkeypatch.setattr('tiered_pipeline.AUDIT_DB_PATH', db_path)
    init_audit_db()
    yield db_path
    os.unlink(db_path)


@pytest.fixture
def pipeline(temp_db):
    """Create a fresh pipeline instance with temp DB."""
    return TieredPipeline()


class TestClassification:
    """Test the triage classification logic."""

    def test_log_analysis_classified_as_computation(self, pipeline):
        request = "analyze log file for ERROR patterns"
        result = pipeline.process(request, {"filepath": "/var/log/syslog", "pattern": "ERROR"})

        assert result.classification.task_type == TaskType.COMPUTATION
        assert result.classification.requires_python is True
        assert result.escalated is False

    def test_ram_calculation_classified_as_computation(self, pipeline):
        request = "calculate RAM usage for 3 containers"
        result = pipeline.process(request, {
            "containers": [{"base_ram_mb": 512}, {"base_ram_mb": 512}, {"base_ram_mb": 512}],
            "workload_multiplier": 1.5
        })

        assert result.classification.task_type == TaskType.COMPUTATION
        assert result.classification.requires_python is True
        assert result.escalated is False

    def test_security_keyword_triggers_security_classification(self, pipeline):
        request = "check firewall rules for open ports"
        result = pipeline.process(request)

        assert result.classification.task_type == TaskType.SECURITY_CRITICAL
        assert result.classification.requires_human is True
        assert result.escalated is True


class TestSecurityOverride:
    """Test the defense-in-depth security override."""

    def test_docker_privileged_triggers_override(self, pipeline):
        request = "deploy docker-compose with privileged: true"
        result = pipeline.process(request)

        assert result.classification.task_type == TaskType.SECURITY_CRITICAL
        assert "privileged" in result.classification.reasoning.lower() or "security keyword override" in result.classification.reasoning.lower()
        assert result.escalated is True

    def test_docker_cap_add_triggers_override(self, pipeline):
        request = "check docker container cap_add SYS_ADMIN"
        result = pipeline.process(request)

        assert result.classification.task_type == TaskType.SECURITY_CRITICAL
        assert result.escalated is True

    def test_docker_network_host_triggers_override(self, pipeline):
        request = "verify docker-compose network_mode: host"
        result = pipeline.process(request)

        assert result.classification.task_type == TaskType.SECURITY_CRITICAL
        assert result.escalated is True

    def test_docker_volume_host_triggers_override(self, pipeline):
        request = "analyze docker volume mount /etc/passwd"
        result = pipeline.process(request)

        assert result.classification.task_type == TaskType.SECURITY_CRITICAL
        assert result.escalated is True

    def test_ssh_key_exposure_triggers_override(self, pipeline):
        request = "check if ssh private key id_rsa is mounted"
        result = pipeline.process(request)

        assert result.classification.task_type == TaskType.SECURITY_CRITICAL
        assert result.escalated is True

    def test_override_logged_in_audit(self, pipeline, temp_db):
        request = "check docker container privileged mode"
        result = pipeline.process(request)

        audit_rows = query_audit_log(limit=10)
        assert len(audit_rows) >= 1
        latest = audit_rows[0]
        assert latest["classification"] == "security"
        assert latest["escalation_decision"] == "escalated"


class TestExecutionAndVerification:
    """Test actual computation execution and verification."""

    def test_log_analysis_executes_and_returns_counts(self, pipeline):
        request = "analyze log file for ERROR patterns"
        result = pipeline.process(request, {"filepath": "/var/log/syslog", "pattern": "ERROR"})

        assert "total_lines" in result.output
        assert "matches" in result.output
        assert isinstance(result.output["total_lines"], int)
        assert result.output["total_lines"] > 0
        assert result.verification.passed is True
        assert result.verification.score == 1.0

    def test_ram_calculation_executes_and_returns_estimates(self, pipeline):
        request = "calculate RAM for containers"
        result = pipeline.process(request, {
            "containers": [{"base_ram_mb": 512}, {"base_ram_mb": 512}],
            "workload_multiplier": 2.0
        })

        assert "base_ram_mb" in result.output
        assert "estimated_peak_ram_mb" in result.output
        assert "safe_margin_ram_mb" in result.output
        assert result.output["base_ram_mb"] == 1024
        assert result.output["estimated_peak_ram_mb"] == 2048.0
        assert result.output["safe_margin_ram_mb"] == 2662.4
        assert result.verification.passed is True


class TestAuditDatabase:
    """Test persistent audit database schema and integrity."""

    def test_audit_log_inserted_for_computation(self, pipeline, temp_db):
        request = "analyze log file"
        result = pipeline.process(request, {"filepath": "/var/log/syslog"})

        audit_rows = query_audit_log(limit=1)
        assert len(audit_rows) == 1
        row = audit_rows[0]
        assert row["classification"] == "computation"
        assert row["verification_status"] == "passed"
        assert row["escalation_decision"] == "approved"
        assert row["triager_confidence"] > 0
        assert row["raw_input_hash"] is not None
        assert len(row["raw_input_hash"]) == 32

    def test_audit_log_inserted_for_security_override(self, pipeline, temp_db):
        request = "check docker privileged container"
        result = pipeline.process(request)

        audit_rows = query_audit_log(limit=1)
        assert len(audit_rows) == 1
        row = audit_rows[0]
        assert row["classification"] == "security"
        assert row["verification_status"] == "failed"
        assert row["escalation_decision"] == "escalated"
        assert "override" in row["escalation_reason"].lower() or "security" in row["escalation_reason"].lower()

    def test_audit_schema_fields_present(self, pipeline, temp_db):
        request = "test request"
        pipeline.process(request)

        audit_rows = query_audit_log(limit=1)
        row = audit_rows[0]
        required_fields = [
            "id", "timestamp", "raw_input_hash", "classification",
            "triager_confidence", "execution_result", "verification_status",
            "verification_score", "escalation_decision", "escalation_reason",
            "human_override", "created_at"
        ]
        for field in required_fields:
            assert field in row, f"Missing field: {field}"

    def test_audit_query_filtering(self, pipeline, temp_db):
        pipeline.process("compute ram")
        pipeline.process("check docker privileged")

        all_rows = query_audit_log(limit=10)
        assert len(all_rows) == 2

        security_rows = [r for r in all_rows if r["classification"] == "security"]
        assert len(security_rows) == 1
        assert security_rows[0]["escalation_decision"] == "escalated"


class TestEscalationLogic:
    """Test escalation gate decisions."""

    def test_computation_below_threshold_not_escalated(self, pipeline):
        request = "analyze log file for errors"
        result = pipeline.process(request, {"filepath": "/var/log/syslog"})

        assert result.escalated is False
        assert result.verification.passed is True

    def test_security_always_escalated(self, pipeline):
        request = "check firewall configuration"
        result = pipeline.process(request)

        assert result.escalated is True
        assert result.verification.passed is False

    def test_reasoning_requires_strong_reviewer(self, pipeline):
        request = "why is my architecture failing"
        result = pipeline.process(request)

        assert result.classification.task_type == TaskType.REASONING
        assert result.classification.requires_strong_reviewer is True
        assert result.escalated is True
        assert result.output.get("status") == "ESCALATED"
        original = result.output.get("original_output", {})
        assert original.get("status") == "NEEDS_STRONG_REVIEWER"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])