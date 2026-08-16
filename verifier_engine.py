"""Hybrid verifier engine: Programmatic gates + LLM generation loop.

Runs SecurityGate THEN QualityGate deterministically against any generated
artifact (n8n workflow JSON or script), and returns a structured feedback
payload for the LLM self-correction loop (<= 3 attempts).
"""

import json
from typing import Any, Callable, Optional

from security_gate import SecurityGate, RISK_THRESHOLD
from quality_gate import QualityGate
from hitl_gate import HITLGate, HITLState
from auto_self_evolver import SKILLS_ROOT


class VerifierEngine:
    """Routes artifacts through security + quality gates with retry loop."""

    def __init__(self, max_attempts: int = 3, generator: Optional[Callable] = None,
                 hitl_gate: Optional[HITLGate] = None,
                 rules_dir: Optional[str] = None,
                 rules_key_path: Optional[str] = None,
                 rules_audit: Any | None = None):
        # rules_dir is the promoted-rules root the gates enforce; the 
        # auto-evolver ALWAYS overrides it with the real skills root (or a test
        # tmp dir). Never silently defaults to SKILLS_ROOT here — that coupling
        # is what kept a misleading fallback alive. rules_key_path + rules_audit
        # thread the HMAC key and audit trail to the promoted-rules reader.
        self.sec_gate = SecurityGate(rules_dir=rules_dir,
                                     key_path=rules_key_path,
                                     audit=rules_audit)
        self.qual_gate = QualityGate()
        self.max_attempts = max_attempts
        self.generator = generator
        self.hitl_gate = hitl_gate
        self.history = []

    def _security_feedback(self, result: dict) -> str:
        lines = "\n".join(f"- {v}" for v in result['violations'])
        return (f"SECURITY GATE REJECTED (Risk Score: {result['risk_score']}/100):\n"
                f"{lines}\n"
                f"Required: remove banned code patterns, hardcoded secrets, "
                f"SSRF/egress targets before re-submission.")

    def _quality_feedback(self, result: dict, attempt: int) -> str:
        lines = "\n".join(f"- {v}" for v in result['violations'])
        return (f"QUALITY AUDIT FAILED (Attempt {attempt}/3)\n"
                f"VIOLATIONS DETECTED:\n"
                f"{lines}\n"
                f"REQUIRED FIX: Adjust the JSON/Code to eliminate the violations "
                f"above while preserving original business logic. "
                f"Re-output ONLY the updated JSON.")

    def _write_audit_row(self, status: str, reason: str, score: Any, attempt: int):
        """Persist a row if the tiered pipeline's audit DB interface is available."""
        try:
            from tiered_pipeline import audit_log_entry
            audit_log_entry(
                raw_input=f"VERIFIER_GATE:{status}:{reason}",
                classification="computation",
                triager_confidence=0.9,
                execution_result={"status": status, "reason": reason, "score": score,
                                  "attempt": attempt},
                verification_status="failed" if status != "READY_FOR_DEPLOYMENT" else "passed",
                verification_score=float(score or 0) / 100 if isinstance(score, (int, float)) else 0.0,
                escalation_decision="escalated" if status in ("REJECTED_SECURITY_RISK",) else
                                    ("approved" if status == "READY_FOR_DEPLOYMENT" else "retry"),
                escalation_reason=reason,
            )
        except Exception:
            pass

    def verify_and_route(
        self,
        workflow_json: Any,
        current_attempt: int = 1,
        use_generator: bool = False,
    ) -> dict:
        """Run security then quality gates. Optionally invoke an LLM generator
        callback to self-correct and retry up to max_attempts."""
        sec_result = self.sec_gate.evaluate_to_dict(workflow_json)
        if sec_result["status"] == "REJECTED_SECURITY_RISK":
            feedback = self._security_feedback(sec_result)
            self._write_audit_row("REJECTED_SECURITY_RISK", feedback,
                                  sec_result['risk_score'], current_attempt)
            self.history.append({"attempt": current_attempt, "gate": "security",
                                 "status": "REJECTED"})

            # HITL: security risks are NOT eligible for silent generator self-fix.
            # Route to human approval instead.
            if self.hitl_gate is not None:
                request = self.hitl_gate.create_pending(
                    raw_input=json.dumps(workflow_json, default=str),
                    risk_score=sec_result['risk_score'],
                    violations=sec_result['violations'],
                    payload={"feedback": feedback, "security": sec_result},
                )
                return {
                    "status": "PENDING_HUMAN_REVIEW",
                    "reason": "SECURITY_VIOLATION_REQUIRES_HUMAN",
                    "hitl_request_id": request.request_id,
                    "risk_score": sec_result['risk_score'],
                    "feedback": feedback,
                    "security": sec_result,
                    "can_retry": False,
                    "mcp_action": None,
                }

            can_retry = current_attempt < self.max_attempts and use_generator
            if not can_retry:
                return {
                    "status": "REJECTED_SECURITY_RISK",
                    "reason": "SECURITY_VIOLATION",
                    "feedback": feedback,
                    "security": sec_result,
                    "can_retry": can_retry,
                }
            # Generator self-corrects then recurse (only when HITL is disabled:
            # some setups want autonomous correction of non-fatal risks)
            fixed = self.generator(feedback, workflow_json)
            return self.verify_and_route(fixed, current_attempt + 1, use_generator)

        qual_result = self.qual_gate.evaluate_to_dict(workflow_json)
        if qual_result["status"] == "REJECTED":
            feedback = self._quality_feedback(qual_result, current_attempt)
            self._write_audit_row("QUALITY_VIOLATION", feedback,
                                  qual_result['quality_score'], current_attempt)
            self.history.append({"attempt": current_attempt, "gate": "quality",
                                 "status": "REJECTED"})
            can_retry = current_attempt < self.max_attempts and use_generator
            if not can_retry:
                return {
                    "status": "QUALITY_VIOLATION",
                    "reason": "QUALITY_VIOLATION",
                    "feedback": feedback,
                    "quality": qual_result,
                    "can_retry": can_retry,
                }
            fixed = self.generator(feedback, workflow_json)
            return self.verify_and_route(fixed, current_attempt + 1, use_generator)

        # Both passed
        self._write_audit_row("READY_FOR_DEPLOYMENT", "",
                              min(sec_result['risk_score'] == 0 and 100 or
                                  (100 - sec_result['risk_score']), qual_result['quality_score']),
                              current_attempt)
        self.history.append({"attempt": current_attempt, "gate": "all", "status": "PASSED"})
        return {
            "status": "READY_FOR_DEPLOYMENT",
            "mcp_action": "n8n_deploy_workflow",
            "security": sec_result,
            "quality": qual_result,
            "attempts_used": current_attempt,
            "can_retry": False,
        }


def build_standard_verification_payload(workflow_json: Any, max_attempts: int = 3) -> dict:
    """One-shot deterministic check (no generator) — useful as a pre-deploy gate.
    Enforces the promoted rules from the real skills root."""
    engine = VerifierEngine(max_attempts=max_attempts, rules_dir=SKILLS_ROOT)
    return engine.verify_and_route(workflow_json)


# ============================================================
# Examples
# ============================================================
if __name__ == "__main__":
    engine = VerifierEngine(rules_dir=SKILLS_ROOT)

    clean_flow = {
        "nodes": [
            {"name": "Receive Webhook", "type": "n8n-nodes-base.webhook",
             "parameters": {"path": "account-hook", "pinnedData": {"1": {"json": {"id": 1}}}}},
            {"name": "Send HTTP Response", "type": "n8n-nodes-base.httpRequest",
             "parameters": {"url": "https://api.example.com/v1/items"}},
        ],
        "connections": {
            "Receive Webhook": {"main": [{"node": "Send HTTP Response"}]},
        }
    }
    print("=== CLEAN FLOW ===")
    print(json.dumps(engine.verify_and_route(clean_flow), indent=2, ensure_ascii=False))

    malicious_flow = {
        "nodes": [
            {"name": "Code Node", "type": "n8n-nodes-base.code",
             "parameters": {"jsCode": "require('child_process').exec('rm -rf /');"}},
            {"name": "Steal metadata", "type": "n8n-nodes-base.httpRequest",
             "parameters": {"url": "http://169.254.169.254/latest/meta-data/"}},
        ],
        "connections": {}
    }
    print("=== MALICIOUS FLOW ===")
    print(json.dumps(engine.verify_and_route(malicious_flow), indent=2, ensure_ascii=False))

    bad_quality_flow = {
        "nodes": [
            {"name": "x", "type": "n8n-nodes-base.code",
             "parameters": {"jsCode": "const v = $node['x'].json; if(a){if(b){for(i;i<9;i++){catch(e){}}}}"}},
        ],
        "connections": {}
    }
    print("=== BAD QUALITY FLOW ===")
    print(json.dumps(engine.verify_and_route(bad_quality_flow), indent=2, ensure_ascii=False))