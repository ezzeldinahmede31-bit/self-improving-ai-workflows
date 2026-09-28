import json
import re
import sqlite3
import subprocess
import sys
import threading
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone, timezone
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Optional
from abc import ABC, abstractmethod


# ============================================================
# SECURITY OVERRIDE (Defense-in-depth: triager AND forced review)
# ============================================================
SECURITY_SENSITIVE_KEYWORDS = {
    'port', 'privileged', 'volume', 'network_mode', 'cap_add',
    'user:', 'env', 'secret', 'expose', '--net=host', 'sudo', 'root',
    'cap_drop', 'cap_add', 'read_only', 'security_opt', 'apparmor',
    'seccomp', 'sysctl', 'ipc_mode', 'pid_mode', 'uts_mode',
    'docker.sock', '/var/run/docker.sock', 'hostnetwork', 'hostpid',
    'runc', 'containerd', 'selinux', 'apparmor', 'capability',
    'namespace', 'unshare', 'chroot', 'pivot_root', 'mount',
    'ssh', 'authorized_keys', 'id_rsa', 'private_key', 'cert',
    'password', 'token', 'credential', 'api_key', 'secret_key',
    'iptables', 'firewall', 'ufw', 'nftables', 'selinux',
}


def force_security_review(raw_input: str, triager_classification: str) -> str:
    """Force security classification if any sensitive keyword detected.
    This is an AND gate, not OR — Python executes anyway, but results escalate."""
    text = raw_input.lower()
    if any(kw in text for kw in SECURITY_SENSITIVE_KEYWORDS):
        if triager_classification != TaskType.SECURITY_CRITICAL.value:
            return TaskType.SECURITY_CRITICAL.value
    return triager_classification


# ============================================================
# PERSISTENT AUDIT DB (SQLite)
# ============================================================
AUDIT_DB_PATH = Path(__file__).parent / "audit.db"
_DB_LOCK = threading.Lock()


def init_audit_db() -> None:
    with _DB_LOCK:
        conn = sqlite3.connect(AUDIT_DB_PATH)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS audit_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                raw_input_hash TEXT NOT NULL,
                classification TEXT NOT NULL,
                triager_confidence REAL NOT NULL,
                execution_result TEXT,
                verification_status TEXT NOT NULL,
                verification_score REAL,
                escalation_decision TEXT NOT NULL,
                escalation_reason TEXT,
                human_override INTEGER DEFAULT 0,
                created_at TEXT DEFAULT (datetime('now'))
            )
        """)
        conn.commit()
        conn.close()


def audit_log_entry(
    raw_input: str,
    classification: str,
    triager_confidence: float,
    execution_result: Any,
    verification_status: str,
    verification_score: float,
    escalation_decision: str,
    escalation_reason: str,
    human_override: bool = False,
) -> None:
    import hashlib
    input_hash = hashlib.sha256(raw_input.encode()).hexdigest()[:32]
    result_json = json.dumps(execution_result, default=str) if execution_result else None

    with _DB_LOCK:
        conn = sqlite3.connect(AUDIT_DB_PATH)
        conn.execute("""
            INSERT INTO audit_log (
                timestamp, raw_input_hash, classification, triager_confidence,
                execution_result, verification_status, verification_score,
                escalation_decision, escalation_reason, human_override
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            datetime.now(timezone.utc).isoformat(),
            input_hash,
            classification,
            triager_confidence,
            result_json,
            verification_status,
            verification_score,
            escalation_decision,
            escalation_reason,
            1 if human_override else 0,
        ))
        conn.commit()
        conn.close()


def query_audit_log(limit: int = 100, since: Optional[str] = None) -> list[dict]:
    """Query audit log for review."""
    with _DB_LOCK:
        conn = sqlite3.connect(AUDIT_DB_PATH)
        conn.row_factory = sqlite3.Row
        if since:
            rows = conn.execute(
                "SELECT * FROM audit_log WHERE timestamp >= ? ORDER BY timestamp DESC LIMIT ?",
                (since, limit)
            ).fetchall()
        else:
            rows = conn.execute(
                "SELECT * FROM audit_log ORDER BY timestamp DESC LIMIT ?",
                (limit,)
            ).fetchall()
        conn.close()
    return [dict(r) for r in rows]


# Initialize DB on import
init_audit_db()


class TaskType(Enum):
    KNOWLEDGE = "knowledge"          # search/RAG/lookup
    COMPUTATION = "computation"      # Python execution required
    REASONING = "reasoning"          # complex judgment, needs strong model
    EXECUTION = "execution"          # direct skill/docs/action
    SECURITY_CRITICAL = "security"   # mandatory human review


class Confidence(Enum):
    HIGH = 0.9
    MEDIUM = 0.6
    LOW = 0.3


@dataclass
class TaskClassification:
    task_type: TaskType
    confidence: Confidence
    reasoning: str
    requires_python: bool = False
    requires_strong_reviewer: bool = False
    requires_human: bool = False
    metadata: dict = field(default_factory=dict)


@dataclass
class VerificationResult:
    passed: bool
    score: float
    issues: list[str]
    details: dict = field(default_factory=dict)


@dataclass
class PipelineResult:
    classification: TaskClassification
    output: Any
    verification: VerificationResult
    escalated: bool = False
    audit_log: list[str] = field(default_factory=list)


class Triager:
    """Layer 1: Classifies incoming request and routes to appropriate handler."""

    KEYWORDS_COMPUTATION = [
        r'\b(حسب|احسب|calculate|compute|ram|memory|cpu|disk|usage|consumption)\b',
        r'\b(analyze|تحليل|parse|استخراج|extract|pattern|regex|log.{0,5}file)\b',
        r'\b(compare|مقارنة|diff|before|after|قبل|بعد)\b',
        r'\b(simulate|نمذجة|model|predict|estimate|تقدير)\b',
        r'\b(verify|تحقق|validate|check|فحص)\b',
    ]

    KEYWORDS_SECURITY = [
        r'\b(security|أمان|firewall|expose|open|permission|sudo|root)\b',
        r'\b(ssh|ssl|tls|certificate|key|secret|password|credential)\b',
        r'\b(production|prod|live|حقيقي|حرج|critical)\b',
    ]

    KEYWORDS_REASONING = [
        r'\b(why|لماذا|how|كيف|diagnose|تشخيص|root cause|سبب جذري)\b',
        r'\b(architecture|معمارية|design|تصميم|tradeoff|مقايضة)\b',
        r'\b(recommend|أنصح|should|ينبغي|best practice|أفضل ممارسة)\b',
    ]

    def classify(self, request: str) -> TaskClassification:
        req_lower = request.lower()

        # Security check first - highest priority
        if any(re.search(kw, req_lower) for kw in self.KEYWORDS_SECURITY):
            return TaskClassification(
                task_type=TaskType.SECURITY_CRITICAL,
                confidence=Confidence.HIGH,
                reasoning="Security-related keywords detected",
                requires_human=True,
                requires_strong_reviewer=True,
            )

        # Computation check
        comp_matches = [kw for kw in self.KEYWORDS_COMPUTATION if re.search(kw, req_lower)]
        if comp_matches:
            return TaskClassification(
                task_type=TaskType.COMPUTATION,
                confidence=Confidence.HIGH if len(comp_matches) > 1 else Confidence.MEDIUM,
                reasoning=f"Computation keywords: {comp_matches}",
                requires_python=True,
            )

        # Reasoning check
        reason_matches = [kw for kw in self.KEYWORDS_REASONING if re.search(kw, req_lower)]
        if reason_matches:
            return TaskClassification(
                task_type=TaskType.REASONING,
                confidence=Confidence.MEDIUM,
                reasoning=f"Reasoning keywords: {reason_matches}",
                requires_strong_reviewer=True,
            )

        # Default: knowledge/lookup
        return TaskClassification(
            task_type=TaskType.KNOWLEDGE,
            confidence=Confidence.MEDIUM,
            reasoning="No specific computation/reasoning/security keywords",
        )


class PythonExecutor:
    """Layer 2a: Executes computation tasks with actual Python.

    SECURITY (GAP-01 closure): in-process exec() of caller-supplied code is
    DISABLED by default (fail-closed). execute() raises RuntimeError unless
    the executor was constructed with allow_arbitrary_exec=True (explicit
    local-dev opt-in only — never in production paths). The built-in
    helpers (analyze_logs / verify_docker_compose / compute_resources) no
    longer generate + exec code at all: they are plain Python functions, so
    filepath/pattern inputs cannot break out of a code string.
    """

    def __init__(self, allow_arbitrary_exec: bool = False):
        self.globals = {}
        self.locals = {}
        self.allow_arbitrary_exec = bool(allow_arbitrary_exec)

    def execute(self, code: str, timeout: int = 30) -> dict:
        """Execute Python code and return result with metadata."""
        if not self.allow_arbitrary_exec:
            raise RuntimeError(
                "PythonExecutor.execute is disabled by default (arbitrary "
                "in-process exec). Construct with allow_arbitrary_exec=True "
                "for explicit local-dev use, or route untrusted code through "
                "agent_sandbox + EnforcedExecutor(code.execute).")
        import io
        import contextlib
        import traceback

        stdout_capture = io.StringIO()
        stderr_capture = io.StringIO()

        try:
            with contextlib.redirect_stdout(stdout_capture), \
                 contextlib.redirect_stderr(stderr_capture):
                exec(code, self.globals, self.locals)

            return {
                "success": True,
                "stdout": stdout_capture.getvalue(),
                "stderr": stderr_capture.getvalue(),
                "locals": {k: v for k, v in self.locals.items() if not k.startswith('_')},
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "traceback": traceback.format_exc(),
                "stdout": stdout_capture.getvalue(),
                "stderr": stderr_capture.getvalue(),
            }

    def analyze_logs(self, filepath: str, pattern: str = None) -> dict:
        """Built-in log analysis (direct implementation, no codegen)."""
        import re

        if len(str(filepath)) > 1024:
            return {"error": "filepath too long"}
        if pattern is not None and len(str(pattern)) > 200:
            return {"error": "pattern too long"}
        try:
            with open(filepath) as f:
                lines = f.readlines()
        except OSError as e:
            return {"error": str(e)}
        results = {"total_lines": len(lines)}
        if pattern:
            try:
                rx = re.compile(pattern)
            except re.error as e:
                return {"error": f"bad pattern: {e}"}
            matches = [line for line in lines if rx.search(line)]
            results["matches"] = len(matches)
            results["samples"] = matches[:10]
        else:
            # Basic stats
            results["error_count"] = sum(1 for line in lines if 'ERROR' in line.upper())
            results["warn_count"] = sum(1 for line in lines if 'WARN' in line.upper())
            results["sample"] = lines[:5]
        return results

    def verify_docker_compose(self, filepath: str) -> dict:
        """Built-in docker-compose verification (direct, no codegen)."""
        import yaml

        try:
            with open(filepath) as f:
                config = yaml.safe_load(f)
        except OSError as e:
            return {"error": str(e)}
        except yaml.YAMLError as e:
            return {"error": f"bad yaml: {e}"}
        if not isinstance(config, dict):
            return {"error": "compose file did not parse to a mapping"}

        ports: dict = {}
        for svc, cfg in (config.get('services', {}) or {}).items():
            for p in (cfg or {}).get('ports', []):
                host_port = str(p).split(':')[0]
                ports.setdefault(host_port, []).append(svc)

        conflicts = {p: s for p, s in ports.items() if len(s) > 1}
        return {
            "valid": len(conflicts) == 0,
            "conflicts": conflicts,
            "services": list((config.get('services', {}) or {}).keys()),
            "total_ports": len(ports),
        }

    def compute_resources(self, containers: list, workload_multiplier: float = 1.5) -> dict:
        """Resource estimation (direct arithmetic, no codegen)."""
        try:
            base_ram = sum(float(c.get('base_ram_mb', 0)) for c in containers)
            base_cpu = sum(float(c.get('base_cpu_percent', 0)) for c in containers)
            multiplier = float(workload_multiplier)
        except Exception as e:  # malformed container specs fail as data errors
            return {"error": f"bad input: {e.__class__.__name__}"}

        peak_ram = base_ram * multiplier
        peak_cpu = min(base_cpu * multiplier, 100 * len(containers))
        return {
            "base_ram_mb": base_ram,
            "base_cpu_percent": base_cpu,
            "estimated_peak_ram_mb": round(peak_ram, 1),
            "estimated_peak_cpu_percent": round(peak_cpu, 1),
            "safe_margin_ram_mb": round(peak_ram * 1.3, 1),
            "container_count": len(containers),
        }


class Verifier:
    """Layer 2b: Verification layer - independent checks."""

    @staticmethod
    def sanity_check(result: dict, expected_ranges: dict = None) -> VerificationResult:
        """Basic sanity checks on computed results."""
        issues = []
        score = 1.0

        if expected_ranges:
            for key, (min_val, max_val) in expected_ranges.items():
                if key in result:
                    val = result[key]
                    if not (min_val <= val <= max_val):
                        issues.append(f"{key}={val} outside expected range [{min_val}, {max_val}]")
                        score -= 0.3

        # Check for NaN/None
        for k, v in result.items():
            if v is None or (isinstance(v, float) and (v != v)):  # NaN check
                issues.append(f"{k} is None/NaN")
                score -= 0.2

        return VerificationResult(
            passed=len(issues) == 0,
            score=max(0.0, score),
            issues=issues,
            details={"checked_keys": list(result.keys())}
        )

    @staticmethod
    def cross_check(source_result: dict, reference_result: dict, keys: list) -> VerificationResult:
        """Compare results from two independent computations."""
        issues = []
        score = 1.0
        details = {}

        for key in keys:
            if key in source_result and key in reference_result:
                src = source_result[key]
                ref = reference_result[key]
                if isinstance(src, (int, float)) and isinstance(ref, (int, float)):
                    diff_pct = abs(src - ref) / max(abs(ref), 1) * 100
                    details[key] = {"source": src, "reference": ref, "diff_pct": diff_pct}
                    if diff_pct > 10:
                        issues.append(f"{key} differs by {diff_pct:.1f}% (src={src}, ref={ref})")
                        score -= 0.25

        return VerificationResult(
            passed=len(issues) == 0,
            score=max(0.0, score),
            issues=issues,
            details=details
        )

    @staticmethod
    def verify_code_syntax(code: str, language: str = "python") -> VerificationResult:
        """Static analysis of generated code."""
        issues = []
        score = 1.0

        if language == "python":
            try:
                compile(code, '<string>', 'exec')
            except SyntaxError as e:
                issues.append(f"Syntax error: {e}")
                score = 0.0
            except Exception as e:
                issues.append(f"Compile error: {e}")
                score = 0.0

            # Basic lint checks
            if 'eval(' in code or 'exec(' in code:
                issues.append("Dangerous function: eval/exec")
                score -= 0.3
            if 'subprocess' in code and 'shell=True' in code:
                issues.append("Security risk: shell=True")
                score -= 0.2

        return VerificationResult(
            passed=len(issues) == 0,
            score=max(0.0, score),
            issues=issues,
            details={"language": language}
        )


class EscalationGate:
    """Layer 3: Decides if task needs human/stronger model review."""

    def __init__(self, confidence_threshold: float = 0.5):
        self.confidence_threshold = confidence_threshold

    def should_escalate(self, classification: TaskClassification, verification: VerificationResult) -> tuple[bool, str]:
        reasons = []

        if classification.requires_human:
            reasons.append("Security-critical task requires human review")

        if classification.confidence.value < self.confidence_threshold:
            reasons.append(f"Low classification confidence: {classification.confidence.value}")

        if not verification.passed:
            reasons.append(f"Verification failed: {verification.issues}")

        if verification.score < 0.7:
            reasons.append(f"Low verification score: {verification.score}")

        if classification.task_type == TaskType.REASONING and not classification.requires_strong_reviewer:
            reasons.append("Complex reasoning without strong reviewer")

        return (len(reasons) > 0, "; ".join(reasons))


class TieredPipeline:
    """Main pipeline orchestrating all layers."""

    def __init__(self, allow_arbitrary_exec: bool = False):
        self.triager = Triager()
        self.executor = PythonExecutor(
            allow_arbitrary_exec=allow_arbitrary_exec)
        self.verifier = Verifier()
        self.escalation = EscalationGate()
        self.audit_log = []

    def _log(self, msg: str):
        self.audit_log.append(msg)
        print(f"[AUDIT] {msg}", file=sys.stderr)

    def process(self, request: str, context: dict = None) -> PipelineResult:
        context = context or {}
        self.audit_log = []
        self._log(f"Request received: {request[:100]}...")

        # Layer 1: Triage
        classification = self.triager.classify(request)
        
        # SECURITY OVERRIDE: Defense-in-depth — force security review on sensitive keywords
        forced_classification = force_security_review(request, classification.task_type.value)
        if forced_classification != classification.task_type.value:
            self._log(f"SECURITY OVERRIDE: {classification.task_type.value} -> {forced_classification}")
            classification = TaskClassification(
                task_type=TaskType(forced_classification),
                confidence=Confidence.HIGH,
                reasoning=f"Forced by security keyword override (original: {classification.reasoning})",
                requires_human=True,
                requires_strong_reviewer=True,
            )
        
        self._log(f"Classification: {classification.task_type.value} (confidence: {classification.confidence.value})")

        # Layer 2: Execute based on type
        output = None
        verification = VerificationResult(passed=True, score=1.0, issues=[])

        if classification.task_type == TaskType.COMPUTATION:
            output = self._handle_computation(request, classification, context)
            verification = self.verifier.sanity_check(output, context.get("expected_ranges"))

        elif classification.task_type == TaskType.SECURITY_CRITICAL:
            output = {"status": "ESCALATED", "message": "Security-critical task requires human review", "request": request}
            verification = VerificationResult(passed=False, score=0.0, issues=["Requires human approval"])

        elif classification.task_type == TaskType.REASONING:
            output = {"status": "NEEDS_STRONG_REVIEWER", "message": "Complex reasoning task", "request": request}
            verification = VerificationResult(passed=True, score=0.5, issues=["Requires stronger model review"])

        else:  # KNOWLEDGE or EXECUTION
            output = {"status": "KNOWLEDGE_TASK", "message": "Route to search/RAG/skills", "request": request}
            verification = VerificationResult(passed=True, score=0.8, issues=[])

        # Layer 3: Escalation check
        escalated, reason = self.escalation.should_escalate(classification, verification)
        if escalated:
            self._log(f"ESCALATION: {reason}")
            output = {"status": "ESCALATED", "reason": reason, "original_output": output}

        # Persistent audit log
        try:
            init_audit_db()
            audit_log_entry(
                raw_input=request,
                classification=classification.task_type.value,
                triager_confidence=classification.confidence.value,
                execution_result=output,
                verification_status="passed" if verification.passed else "failed",
                verification_score=verification.score,
                escalation_decision="escalated" if escalated else "approved",
                escalation_reason=reason if escalated else "",
            )
        except Exception as e:
            self._log(f"AUDIT LOG FAILED: {e}")

        return PipelineResult(
            classification=classification,
            output=output,
            verification=verification,
            escalated=escalated,
            audit_log=self.audit_log
        )

    def _handle_computation(self, request: str, classification: TaskClassification, context: dict) -> dict:
        """Route computation requests to appropriate executor method."""
        req_lower = request.lower()

        # Detect specific computation type
        if 'log' in req_lower and ('analy' in req_lower or 'parse' in req_lower or 'تحليل' in req_lower):
            filepath = context.get("filepath", "/var/log/syslog")
            pattern = context.get("pattern")
            self._log(f"Running log analysis on {filepath}")
            return self.executor.analyze_logs(filepath, pattern)

        if 'docker' in req_lower and 'compose' in req_lower:
            filepath = context.get("filepath", "docker-compose.yml")
            self._log(f"Verifying docker-compose: {filepath}")
            return self.executor.verify_docker_compose(filepath)

        if 'ram' in req_lower or 'memory' in req_lower or 'resource' in req_lower:
            containers = context.get("containers", [])
            multiplier = context.get("workload_multiplier", 1.5)
            self._log(f"Computing resources for {len(containers)} containers")
            return self.executor.compute_resources(containers, multiplier)

        # Generic: execute provided code (fail-closed unless explicitly opted in)
        if "code" in context:
            if not self.executor.allow_arbitrary_exec:
                self._log("REFUSED custom code execution (not opted in)")
                return {"error": "custom code execution disabled: construct "
                                 "TieredPipeline(allow_arbitrary_exec=True) "
                                 "for local-dev use, or route untrusted code "
                                 "through agent_sandbox"}
            self._log("Executing custom Python code")
            result = self.executor.execute(context["code"])
            if result["success"]:
                return result.get("locals", {})
            return {"error": result["error"]}

        return {"error": "No computation handler matched", "request": request}


# Convenience function for direct use
def run_pipeline(request: str, context: dict = None,
                 allow_arbitrary_exec: bool = False) -> PipelineResult:
    pipeline = TieredPipeline(allow_arbitrary_exec=allow_arbitrary_exec)
    return pipeline.process(request, context)


if __name__ == "__main__":
    # Demo
    import sys
    request = sys.argv[1] if len(sys.argv) > 1 else "analyze log file /var/log/syslog for ERROR patterns"
    context = json.loads(sys.argv[2]) if len(sys.argv) > 2 else {}

    result = run_pipeline(request, context)
    print(json.dumps({
        "classification": result.classification.task_type.value,
        "confidence": result.classification.confidence.value,
        "output": result.output,
        "verification_passed": result.verification.passed,
        "verification_score": result.verification.score,
        "escalated": result.escalated,
        "audit_log": result.audit_log
    }, indent=2, ensure_ascii=False))