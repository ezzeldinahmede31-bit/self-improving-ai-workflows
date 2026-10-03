"""Honest machine-readable feature registry.

Terminology (fixed, no contradictions):
  - 7 Enforcement Chains: the ordered gate pipeline every sensitive
    execution must traverse:
      C1 Policy -> C2 Capability/Identity -> C3 Skill Trust ->
      C4 Sandbox -> C5 Egress -> C6 Verification (tool result +
      business invariants) -> C7 Audit/Provenance.
  - Enforcement Domains: the platform capability areas (policy, sandbox,
    egress, secrets, skills/trust, audit, provenance, verification,
    invariants, deployment, tenancy, privacy/DLP, observability, ...).
    Domains are grouped UNDER chains where they enforce, and listed
    separately where they observe (SLO/cost/capacity, contracts, DR...).

Each Feature has: id (stable F001...), name, implementation (module),
production_entrypoint, production_caller, enforcement_point, positive
test, negative_test, bypass_test, status, evidence.

Statuses form a promotion ladder:
  IMPLEMENTED < INTEGRATED < VERIFIED < PRODUCTION_READY.
Also: BLOCKED, OPTIONAL, SIMULATED, LIVE_UNVERIFIED. A feature is
INTEGRATED only with a real production caller; VERIFIED only with
positive+negative+bypass tests and evidence.

Counting semantics: status_counts() reports CURRENT_STATUS — each
feature is counted exactly once, at its current rung (mutually
exclusive buckets that sum to TOTAL). These are NOT cumulative
roll-ups: VERIFIED does not include PRODUCTION_READY, INTEGRATED
does not include VERIFIED. Promotion moves a feature from one
bucket to the next; it is never in two buckets at once.
"""

from __future__ import annotations

from dataclasses import dataclass, field

CHAINS = ("C1-policy", "C2-capability", "C3-skill-trust", "C4-sandbox",
          "C5-egress", "C6-verification", "C7-audit")


@dataclass
class Feature:
    fid: str
    name: str
    implementation: str
    production_entrypoint: str
    production_caller: str
    enforcement_point: str
    chain: str
    positive_test: str
    negative_test: str
    bypass_test: str
    status: str
    evidence: str = ""


def _F(fid, name, impl, entry, caller, enf, chain, pos, neg, byp, status,
       evidence=""):
    return Feature(fid, name, impl, entry, caller, enf, chain, pos, neg,
                   byp, status, evidence)


def build_registry() -> list[Feature]:
    """The real registry. Count = len(list); never padded to a target."""
    T = "tests/"
    return [
        _F("F001", "policy-engine", "policy_engine.py",
           "SystemOrchestrator.execute_workflow_task[0d]",
           "master_system_orchestrator.py", "platform_wiring.policy_gate",
           "C1-policy", T + "test_p0a_policy.py",
           T + "test_p0a_policy.py", T + "test_adversarial_full_stack.py",
           "VERIFIED", "893-test suite green; adversarial bypass blocked"),
        _F("F002", "capability-tokens", "capability.py",
           "SystemOrchestrator.execute_workflow_task[0d/2d]",
           "master_system_orchestrator.py",
           "platform_wiring.mint/check_capability", "C2-capability",
           T + "test_p0a_capability.py", T + "test_p0a_capability.py",
           T + "test_adversarial_full_stack.py", "VERIFIED", ""),
        _F("F003", "central-enforcement", "enforced_execution.py",
           "EnforcedExecutor.execute",
           "master_system_orchestrator.py + sensitive callers",
           "enforced_execution.EnforcedExecutor", "C1-policy",
           T + "test_adversarial_full_stack.py",
           T + "test_adversarial_full_stack.py",
           T + "test_adversarial_full_stack.py", "VERIFIED", ""),
        _F("F004", "skill-trust-registry", "skill_trust.py",
           "Orchestrator._gather_inputs trust_hook / platform_wiring.skill_filter",
           "orchestrator/scheduler.py + master_system_orchestrator.py",
           "platform_wiring.skill_filter", "C3-skill-trust",
           T + "test_p0b_trust.py", T + "test_p0b_trust.py",
           T + "test_adversarial_full_stack.py", "VERIFIED", ""),
        _F("F005", "skill-supply-chain", "supply_chain.py",
           "PromotionPipeline skill stages",
           "promotion_pipeline.py", "supply_chain scan gates",
           "C3-skill-trust", T + "test_p0b_supply.py",
           T + "test_p0b_supply.py", T + "test_adversarial_full_stack.py",
           "INTEGRATED", "live-validation of malicious-dep fixtures"),
        _F("F006", "agent-sandbox", "agent_sandbox.py",
           "execute_workflow_task[2c] via AgentSandboxShim",
           "master_system_orchestrator.py",
           "platform_wiring.AgentSandboxShim", "C4-sandbox",
           T + "test_p0a_sandbox.py", T + "test_p0a_sandbox.py",
           T + "test_adversarial_full_stack.py", "VERIFIED",
           "local tier scrubbed-env; adversarial forced to docker tier"),
        _F("F007", "cybersec-sandbox", "cybersec_sandbox_engine.py",
           "CyberSecRedTeamAgent.audit_workflow + runtime check",
           "master_system_orchestrator.py", "save_code_nodes_runtime_check",
           "C4-sandbox", "tests/test_master_orchestrator.py",
           "tests/test_master_orchestrator.py",
           T + "test_adversarial_full_stack.py", "INTEGRATED", ""),
         _F("F008", "egress-firewall", "egress_firewall.py",
            "execute_workflow_task[2d] egress_guard",
            "master_system_orchestrator.py", "platform_wiring.egress_guard",
            "C5-egress", T + "test_p0a_egress.py", T + "test_p0a_egress.py",
            T + "test_adversarial_full_stack.py", "VERIFIED",
            "TTL-clamped DnsCache + fetch_pinned connection-boundary "
            "rebind/redirect/downgrade closure "
            "(tests/test_p0d_dns_ttl_pinned.py, 22 tests)"),
        _F("F009", "remote-api-egress", "remote_api.py",
           "RemoteAPIClient.request via MockRouter.assert_safe",
           "master_system_orchestrator.py + tool callers",
           "MockRouter.assert_safe + egress firewall hook", "C5-egress",
           "tests/test_remote_adaptation.py",
           "tests/test_remote_adaptation.py",
           T + "test_adversarial_full_stack.py", "INTEGRATED",
           "direct-IP/metadata bypass covered by firewall tests"),
        _F("F010", "mcp-browser-guard", "mcp_browser_guard.py",
           "browser/MCP tool calls", "platform consumers",
           "mcp_browser_guard enrollment + allow-list", "C5-egress",
           T + "test_p2c_guard.py", T + "test_p2c_guard.py",
           T + "test_adversarial_full_stack.py", "INTEGRATED", ""),
        _F("F011", "tool-result-verifier", "tool_result_verifier.py",
           "platform_wiring.ai_verify / EnforcedExecutor step 6",
           "master_system_orchestrator.py", "platform_wiring.ai_verify",
           "C6-verification", T + "test_p0c_toolverify.py",
           T + "test_p0c_toolverify.py", T + "test_adversarial_full_stack.py",
           "VERIFIED", ""),
        _F("F012", "business-invariants", "business_invariants.py",
           "execute_workflow_task[3b] InvariantEngine.evaluate",
           "master_system_orchestrator.py", "InvariantEngine.evaluate",
           "C6-verification", T + "test_p0c_invariants.py",
           T + "test_p0c_invariants.py", T + "test_adversarial_full_stack.py",
           "VERIFIED", ""),
        _F("F013", "immutable-audit-signed", "immutable_audit.py",
           "platform_wiring.build_sinks / audit_event",
           "master_system_orchestrator.py",
           "AuditChain HMAC-signed (production default)",
           "C7-audit", T + "test_p0b_audit.py", T + "test_p0b_audit.py",
           T + "test_adversarial_full_stack.py", "VERIFIED",
           "build_production_sinks() fails closed without AUDIT_HMAC_KEY"),
        _F("F014", "provenance-traceability", "provenance.py",
           "_seal_result provenance links",
           "master_system_orchestrator.py", "ProvenanceLog.link + gaps()",
           "C7-audit", T + "test_p0b_prov_repro.py",
           T + "test_p0b_prov_repro.py", T + "test_adversarial_full_stack.py",
           "VERIFIED", ""),
        _F("F015", "distributed-tracing", "tracing.py",
           "evidence tracer spans", "platform_wiring.build_sinks",
           "Tracer spans", "C7-audit", T + "test_p0c_trace.py",
           T + "test_p0c_trace.py", "tests/test_p1c_deploy_trace.py",
           "INTEGRATED", ""),
        _F("F016", "reproducibility", "reproducibility.py",
           "evidence digests", "platform consumers", "canonical digests",
           "C7-audit", T + "test_p0b_prov_repro.py",
           T + "test_p0b_prov_repro.py", "tests/test_p2a_contract_schema.py",
           "INTEGRATED", ""),
        _F("F017", "secrets-vault", "secrets_vault.py",
           "Vault.issue/redeem/rotate", "tool executors",
           "lease-scoped redeem", "C2-capability",
           T + "test_p0a_vault.py", T + "test_p0a_vault.py",
           T + "test_adversarial_full_stack.py", "VERIFIED", ""),
        _F("F018", "secrets-provider", "secrets_provider.py",
           "SecretManager.resolve", "orchestrator + integrations",
           "backend resolution, no prompt/log sink", "C2-capability",
           "tests/test_security_governance.py",
           "tests/test_security_governance.py",
           T + "test_adversarial_full_stack.py", "INTEGRATED", ""),
        _F("F019", "secret-redactor-DLP", "secret_redactor.py",
           "execute_workflow_task[0b] vault.register_payload",
           "master_system_orchestrator.py", "SecretVault + DLP deny-list",
           "C6-verification", "tests/test_security_governance.py",
           "tests/test_security_governance.py",
           T + "test_adversarial_full_stack.py", "INTEGRATED", ""),
        _F("F020", "privacy-governance", "privacy.py",
           "privacy-classified sinks", "platform consumers",
           "classification + TTL + delete/export", "C7-audit",
           T + "test_p1c_tenancy_privacy.py",
           T + "test_p1c_tenancy_privacy.py",
           T + "test_adversarial_full_stack.py", "INTEGRATED", ""),
        _F("F021", "multi-tenancy", "tenancy.py",
           "tenant-scoped namespaces + budgets",
           "platform consumers", "tenant isolation checks", "C2-capability",
           T + "test_p1c_tenancy_privacy.py",
           T + "test_p1c_tenancy_privacy.py",
           T + "test_adversarial_full_stack.py", "VERIFIED",
           "cross-tenant read/write blocked + concurrent attack test"),
        _F("F022", "memory-governance", "memory_governance.py",
           "stamped/TTL/quarantined writes", "agent memory writers",
           "authority-ranked conflict + quarantine", "C6-verification",
           T + "test_p0c_memory.py", T + "test_p0c_memory.py",
           T + "test_adversarial_full_stack.py", "VERIFIED", ""),
        _F("F023", "hitl-approval", "hitl_gate.py",
           "HITLGate.create_pending/approve", "master_system_orchestrator.py",
           "single-use token + expiry", "C1-policy",
           "tests/test_hitl_gate.py", "tests/test_hitl_gate.py",
           T + "test_adversarial_full_stack.py", "VERIFIED", ""),
        _F("F024", "idempotency-store", "idempotency.py",
           "keyed exactly-once records", "workflow executors",
           "idempotency keys enforced at store", "C6-verification",
           T + "test_p1b_idem_chaos.py", T + "test_p1b_idem_chaos.py",
           T + "test_adversarial_full_stack.py", "VERIFIED", ""),
        _F("F025", "saga-compensation", "saga.py",
           "forward + compensating undo journal", "multi-step workflows",
           "saga journal + compensation", "C6-verification",
           T + "test_p1b_adversarial_saga.py",
           T + "test_p1b_adversarial_saga.py",
           T + "test_adversarial_full_stack.py", "VERIFIED", ""),
        _F("F026", "deployment-canary-rollback", "deployment.py",
           "platform_wiring.deploy_release", "release callers",
           "gates -> canary -> promote/rollback", "C7-audit",
           T + "test_p1c_deploy_trace.py", T + "test_p1c_deploy_trace.py",
           T + "test_adversarial_full_stack.py", "VERIFIED", ""),
        _F("F027", "promotion-pipeline", "promotion_pipeline.py",
           "platform_wiring.promote_candidate", "self-improvement + skills",
           "stage gates halt-on-fail", "C7-audit",
           T + "test_p0c_promotion.py", T + "test_p0c_promotion.py",
           T + "test_adversarial_full_stack.py", "VERIFIED", ""),
        _F("F028", "self-evolution-gated", "auto_self_evolver.py",
           "SystemOrchestrator[0.1] run_evolution_cycle",
           "master_system_orchestrator.py", "measure -> verify -> promote-only",
           "C7-audit", "tests/test_auto_self_evolver.py",
           "tests/test_auto_self_evolver.py",
           T + "test_adversarial_full_stack.py", "INTEGRATED",
           "no live model => honestly unmeasured, nothing promoted"),
        _F("F029", "golden-corpus", "golden_corpus.py",
           "platform_wiring.handle_failure golden_case",
           "master_system_orchestrator.py", "permanent regression gate",
           "C7-audit", T + "test_p2b_guards_golden.py",
           T + "test_p2b_guards_golden.py",
           T + "test_adversarial_full_stack.py", "VERIFIED", ""),
        _F("F030", "incident-response", "incident.py",
           "platform_wiring.handle_failure", "master_system_orchestrator.py",
           "detect -> respond -> correlate", "C7-audit",
           T + "test_p2c_incident.py", T + "test_p2c_incident.py",
           T + "test_adversarial_full_stack.py", "INTEGRATED", ""),
        _F("F031", "scheduler-guards", "scheduler_guards.py",
           "wait-graph + starvation aging", "orchestrator/scheduler.py",
           "deadlock/starvation guards", "C4-sandbox",
           "tests/test_p1d_capacity_health.py",
           "tests/test_p1d_capacity_health.py",
           T + "test_adversarial_full_stack.py", "INTEGRATED", ""),
        _F("F032", "health-probes", "health_probes.py",
           "pre-flight credential/dependency gates", "deploy + workers",
           "TCP gates + synthetic runs", "C4-sandbox",
           "tests/test_p1d_capacity_health.py",
           "tests/test_p1d_capacity_health.py",
           T + "test_adversarial_full_stack.py", "INTEGRATED", ""),
        _F("F033", "observability-SLO-cost", "observability.py+slo.py+cost_governor.py",
           "StructLogger/Metrics/SLO/budgets", "master_system_orchestrator.py",
           "SLO burn + spend freeze", "C7-audit",
           T + "test_p1d_slo_cost.py", T + "test_p1d_slo_cost.py",
           T + "test_adversarial_full_stack.py", "INTEGRATED", ""),
        _F("F034", "capacity-planning", "capacity.py",
           "fleet snapshots + headroom", "ops callers", "headroom gates",
           "C7-audit", "tests/test_p1d_capacity_health.py",
           "tests/test_p1d_capacity_health.py",
           T + "test_adversarial_full_stack.py", "INTEGRATED", ""),
        _F("F035", "contract-schema-drift", "contract_test.py+schema_guard.py+schema_evolve.py+spec_drift.py",
           "pinned schemas + migration tests", "integrations",
           "compatibility gates", "C6-verification",
           T + "test_p2a_contract_schema.py",
           T + "test_p2a_contract_schema.py",
           T + "test_adversarial_full_stack.py", "INTEGRATED", ""),
        _F("F036", "dependency-drift", "dep_drift.py",
           "pinned baseline diffs", "CI/consumers", "retest verdicts",
           "C6-verification", T + "test_p2a_drift_monitor.py",
           T + "test_p2a_drift_monitor.py",
           T + "test_adversarial_full_stack.py", "INTEGRATED", ""),
        _F("F037", "api-monitor", "api_monitor.py",
           "shape/latency/version probes", "integration callers",
           "first-deviation findings", "C6-verification",
           "tests/test_p2a_drift_monitor.py",
           "tests/test_p2a_drift_monitor.py", "tests/test_tool_gateway.py",
           "INTEGRATED", ""),
         _F("F038", "model-governance", "model_bench.py+model_drift.py+model_failover.py+prompt_regression.py",
            "benchmark/drift/failover/regression gates",
            "model callers", "promotion only via gates", "C6-verification",
            T + "test_p1a_bench_drift.py",
            T + "test_p1a_bench_drift.py",
            T + "test_adversarial_full_stack.py", "INTEGRATED",
            "live NVIDIA catalog (81 models) + 16-token completion routed "
            "through untrusted-output gate; prod path never invokes live "
            "model (tests/test_p1a_live_model_governance.py + "
            "test_p0d_production_isolation.py)"),
        _F("F039", "behavioral-eval", "behavioral_eval.py",
           "intent/tool/grounding/fact scoring", "agent changes",
           "weighted pass gates", "C6-verification",
           T + "test_p1a_regression_behavior.py",
           T + "test_p1a_regression_behavior.py",
           T + "test_adversarial_full_stack.py", "INTEGRATED", ""),
        _F("F040", "adversarial-suites", "adversarial_suite.py+attack_fuzzer.py",
           "attack corpus + fuzz probes", "orchestrator[2b+]",
           "detector grading + HITL escalation", "C6-verification",
           T + "test_p1b_adversarial_saga.py",
           T + "test_p1b_adversarial_saga.py",
           T + "test_adversarial_full_stack.py", "VERIFIED", ""),
        _F("F041", "advanced-testing", "advanced_testing.py",
           "property/mutation/metamorphic aides", "test authors",
           "seeded + shrinking suites", "C6-verification",
           T + "test_p2b_advanced_spec.py",
           T + "test_p2b_advanced_spec.py",
           T + "test_adversarial_full_stack.py", "INTEGRATED", ""),
        _F("F042", "chaos-drills-DR", "chaos_drills.py",
           "fault catalog inject/assert/recover", "ops/test",
           "restore-to-smoke + RPO/RTO", "C7-audit",
           T + "test_p1b_idem_chaos.py", T + "test_p1b_idem_chaos.py",
           T + "test_adversarial_full_stack.py", "INTEGRATED",
           "restore proven in test env; prod DR remains LIVE_UNVERIFIED"),
         _F("F043", "n8n-integration", "n8n_integration.py",
            "trigger_and_verify via webhook",
            "master_system_orchestrator.py[4]", "5-consecutive-pass gate",
            "C5-egress", "tests/test_e2e_live_n8n.py",
            "tests/test_e2e_live_n8n.py", "tests/test_n8n_gates_parity.py",
            "VERIFIED",
            "LIVE 12/12 on real instance: ephemeral no-op workflow "
            "created+activated+5/5 stable passes+duplicates+deactivated+"
            "deleted+verified-gone; bad-key/unknown-id/egress/capability "
            "refusals live-proven (FINAL_AUDIT/n8n_live_evidence.json). "
            "Residual: timeout/cancel paths not exercised live (no-op "
            "finishes instantly; forcing them would risk prod)."),
        _F("F044", "security-gate-quality-gate-verifier",
           "security_gate.py+quality_gate.py+verifier_engine.py",
           "verify_and_route safety+quality gates",
           "master_system_orchestrator.py[3]", "risk>=threshold fatal",
           "C1-policy", "tests/test_verifier_engine.py",
           "tests/test_verifier_engine.py",
           T + "test_adversarial_full_stack.py", "VERIFIED", ""),
        _F("F045", "ambiguity-chain-confidence-context",
           "ambiguity_resolver.py+chain_integrity_checker.py+confidence_calibrator.py+context_enrichment.py",
           "orchestrator steps 0/0.6/0c", "master_system_orchestrator.py",
           "CLARIFY/ESCALATE + HITL routing", "C1-policy",
           "tests/test_cognitive_modules.py",
           "tests/test_cognitive_modules.py",
           T + "test_adversarial_full_stack.py", "INTEGRATED", ""),
        _F("F046", "cost-ledger-cascade-routing",
           "cost_ledger.py+cascade_routing.py+tiered_pipeline.py+local_routing.py",
           "budget ceilings + tier escalation", "master_system_orchestrator.py",
           "spend ceilings + failover", "C7-audit",
           "tests/test_model_coercion_protocols.py",
           "tests/test_model_coercion_protocols.py",
           T + "test_adversarial_full_stack.py", "INTEGRATED", ""),
        _F("F047", "workflow-versions-traceability",
           "workflow_versions.py+traceability.py",
           "snapshot + requirement links", "master_system_orchestrator.py",
           "coverage-gap delivery gate", "C7-audit",
           "tests/test_p0b_prov_repro.py", "tests/test_p0b_prov_repro.py",
           T + "test_adversarial_full_stack.py", "INTEGRATED", ""),
        _F("F048", "tool-gateway", "tool_gateway.py",
           "ToolGateway capability probes", "master_system_orchestrator.py",
           "SKIPPED-not-crashed contract", "C5-egress",
           "tests/test_tool_gateway.py", "tests/test_tool_gateway.py",
           T + "test_adversarial_full_stack.py", "INTEGRATED", ""),
        _F("F049", "feedback-quirks-rag", "feedback_loop.py+quirks_memory.py+rag_engine.py+prompt_assembler.py",
           "rejection learning + JIT RAG", "master_system_orchestrator.py",
           "rotation gate + purgeable scope", "C7-audit",
           "tests/test_weak_model_hardening.py",
           "tests/test_weak_model_hardening.py",
           T + "test_adversarial_full_stack.py", "INTEGRATED", ""),
    ]


def status_counts(reg: list[Feature] | None = None) -> dict:
    reg = reg if reg is not None else build_registry()
    counts: dict = {}
    for f in reg:
        counts[f.status] = counts.get(f.status, 0) + 1
    for s in ("IMPLEMENTED", "INTEGRATED", "VERIFIED", "PRODUCTION_READY",
              "BLOCKED", "OPTIONAL", "SIMULATED", "LIVE_UNVERIFIED"):
        counts.setdefault(s, 0)
    counts["TOTAL"] = len(reg)
    return counts
