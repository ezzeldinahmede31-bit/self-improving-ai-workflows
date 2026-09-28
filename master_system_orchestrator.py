"""Master System Orchestrator — "The Pragmatic JIT AI Automation Architect".

Unified engine implementing the JIT task-scoped pipeline and wiring together
the REAL modules already built in this workspace:

  - BrutallyHonestBudgetAnalyzer : budget/TCO audit + over-engineering rejection
  - TaskScopedJITRAG             : ephemeral, per-task isolated knowledge store
  - VerifierEngine               : deterministic Safety Gate + Quality Gate
  - HITLGate                     : human approval for Risk Score >= 40
  - RemoteAPIClient / MockRouter : Digital-Twin egress before real traffic
  - QuirksMemory                 : durable knowledge kept after RAG purge
"""

import json
import os
import sqlite3
import sys
import tempfile
import time
import uuid
from pathlib import Path
from typing import Any, Callable, Optional

from verifier_engine import VerifierEngine
from security_gate import RISK_THRESHOLD
from hitl_gate import HITLGate, HITLState, HITLRequest
from remote_api import RemoteAPIClient, MockRouter, EgressBlockedError
from local_routing import HybridRouter, ExecLocale
from quirks_memory import remember_quirk, render_as_prompt
from dual_process_planner import ExtendedThinkingPlanner, DualPlan
from cybersec_sandbox_engine import (CyberSecRedTeamAgent, ExecutionSandbox,
                                     save_code_nodes_runtime_check)
from secret_redactor import SecretRedactor, SecretVault
from tool_gateway import (ToolGateway, LiteLLMFailover, PrismMock,
                          SemgrepSAST, NucleiScan)
from observability import StructLogger, MetricsRegistry, AlertManager, AlertRule
from model_failover import build_default_ladder, FailoverDriver
from feedback_loop import FeedbackLoop
from workflow_versions import WorkflowVersionControl
from cost_ledger import CostLedger
from attack_fuzzer import AttackFuzzer
from cascade_routing import CascadeRouter
from rag_engine import RagMemory, default_rag
from prompt_assembler import FewShotAssembler, build_generator_prompt
from schema_guard import JsonSchemaGuard
from ambiguity_resolver import AmbiguityResolver, structural_ambiguity
from chain_integrity_checker import ChainIntegrityChecker, check_dag_integrity
from confidence_calibrator import ConfidenceCalibrator
from context_enrichment import (ImplicitIntentLexicon,
                                render_implicit_context, resolve_implicit)
from auto_self_evolver import (AutonomousSelfEvolver, WeaknessSource,
                               SKILLS_ROOT, DEFAULT_HMAC_KEY_PATH)
import platform_wiring


# ============================================================
# Budget Matrix (micro / mid / enterprise) — honest cost layer
# ============================================================
PRICING_CATALOG = {
    "deepseek-chat":  {"input_1k": 0.00014, "output_1k": 0.00028},
    "deepseek-reasoner": {"input_1k": 0.00055, "output_1k": 0.00219},
    "qwen2.5-coder:7b": {"input_1k": 0.0, "output_1k": 0.0},   # local Ollama
    "claude-3-5-sonnet": {"input_1k": 0.003, "output_1k": 0.015},
    "hetzner_vps": 5.0,
    "digitalocean_vps": 6.0,
    "supabase_free": 0.0,
    "supabase_pro": 25.0,
    "vector_db_managed": 15.0,
}


class BrutallyHonestBudgetAnalyzer:
    """Budget/TCO audit. Says NO loudly when a plan is unfeasible."""

    @staticmethod
    def audit_task(
        monthly_budget_usd: float,
        daily_requests: int,
        avg_tokens: int,
        proposed_tech_stack: list[str],
        input_output_ratio: float = 0.7,
    ) -> dict:
        monthly_requests = daily_requests * 30
        tokens_in_k = (monthly_requests * avg_tokens * input_output_ratio) / 1000
        tokens_out_k = (monthly_requests * avg_tokens * (1 - input_output_ratio)) / 1000

        def model_cost(model):
            p = PRICING_CATALOG.get(model, {"input_1k": 0, "output_1k": 0})
            return tokens_in_k * p["input_1k"] + tokens_out_k * p["output_1k"]

        cost = {m: round(model_cost(m), 2) for m in ("deepseek-chat", "deepseek-reasoner",
                                                     "qwen2.5-coder:7b", "claude-3-5-sonnet")}
        # use models actually proposed first; fall back to cheapest catalog entry
        model_keys = [m for m, v in PRICING_CATALOG.items() if isinstance(v, dict)]
        proposed_models = [m for m in proposed_tech_stack if m in model_keys]
        priced_models = proposed_models or ("deepseek-chat", "qwen2.5-coder:7b")
        cheapest = min(model_cost(m) for m in priced_models)

        critique = []
        viable = True

        if cheapest > monthly_budget_usd * 0.5:
            viable = False
            critique.append(
                f"BUDGET VIOLATION: lowest realistic LLM cost (${cheapest:.2f}/mo from "
                f"local qwen / deepseek-chat) already exceeds 50% of your budget "
                f"(${monthly_budget_usd}/mo). Reduce daily calls ({daily_requests}) or "
                f"price another hosting tier."
            )

        if "vector_db" in proposed_tech_stack and monthly_requests < 10000:
            critique.append(
                f"OVER-ENGINEERING ALERT: vector DB for {monthly_requests} requests/mo is "
                f"redundant — SQLite FTS5 covers this scale at $0. Saved ~"
                f"${PRICING_CATALOG['vector_db_managed']}/mo."
            )

        if "postgres" in proposed_tech_stack and monthly_requests < 20000:
            critique.append(
                f"OVER-ENGINEERING ALERT: Postgres for {monthly_requests} req/mo when "
                f"SQLite is sufficient — reduces ops, latency and cost."
            )

        # Hosting line items found in stack
        hosting = {}
        if "hetzner" in proposed_tech_stack:
            hosting["hetzner_vps"] = PRICING_CATALOG["hetzner_vps"]
        if "supabase_pro" in proposed_tech_stack:
            hosting["supabase_pro"] = PRICING_CATALOG["supabase_pro"]

        monthly_tco = cheapest + sum(hosting.values())

        return {
            "viable": viable,
            "monthly_requests": monthly_requests,
            "est_cost_deepseek_chat": cost["deepseek-chat"],
            "est_cost_deepseek_reasoner": cost["deepseek-reasoner"],
            "est_cost_local_qwen": cost["qwen2.5-coder:7b"],
            "est_cost_claude": cost["claude-3-5-sonnet"],
            "hosting_monthly": round(sum(hosting.values()), 2),
            "estimated_tco_monthly": round(monthly_tco, 2),
            "critique_notes": critique,
        }


# ============================================================
# Ephemeral Task-Scoped RAG (isolated, purge-able)
# ============================================================
class TaskScopedJITRAG:
    """Per-task isolated knowledge store. Destroyed via purge_context()."""

    def __init__(self, task_name: str, keep_dirs: Optional[list[str]] = None):
        self.task_id = f"task_{uuid.uuid4().hex[:8]}"
        self.task_name = task_name
        self.keep_dirs = keep_dirs or ['/tmp', os.getcwd()]
        fd, self.db_path = tempfile.mkstemp(
            suffix="_ephemeral.sqlite", dir=self.keep_dirs[0])
        os.close(fd)
        if os.path.exists(self.db_path):
            os.remove(self.db_path)
        self._init_db()

    def _init_db(self):
        conn = sqlite3.connect(self.db_path)
        conn.execute(
            "CREATE TABLE ephemeral_docs (id INTEGER PRIMARY KEY, source TEXT, "
            "doc_type TEXT, content TEXT, keywords TEXT)"
        )
        conn.commit()
        conn.close()

    def ingest_jit_docs(self, docs: list[dict]):
        conn = sqlite3.connect(self.db_path)
        for doc in docs:
            kw = " ".join(doc.get("keywords", []))
            conn.execute(
                "INSERT INTO ephemeral_docs (source, doc_type, content, keywords) "
                "VALUES (?, ?, ?, ?)",
                (doc["source"], doc.get("doc_type", ""), doc["content"], kw),
            )
        conn.commit()
        conn.close()
        return len(docs)

    def query_context(self, keyword: str, limit: int = 5) -> list[dict]:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        rows = conn.execute(
            "SELECT source, doc_type, content, keywords FROM ephemeral_docs "
            "WHERE content LIKE ? OR keywords LIKE ? LIMIT ?",
            (f"%{keyword}%", f"%{keyword}%", limit),
        ).fetchall()
        conn.close()
        return [dict(r) for r in rows]

    def purge_context(self):
        if os.path.exists(self.db_path):
            try:
                os.remove(self.db_path)
            except OSError:
                pass
            return True
        return False


# ============================================================
# Main Orchestrator — wires the whole pipeline
# ============================================================
class SystemOrchestrator:
    def __init__(
        self,
        budget_usd: float = 20.0,
        max_attempts: int = 3,
        generator: Optional[Callable] = None,
        security_token: Optional[str] = None,
        mock_mappings: Optional[dict[str, str]] = None,
        elide_output: bool = False,
        tools_host: str = "127.0.0.1",
        enforcement: Optional[dict] = None,
        evidence_dir: Optional[str] = None,
    ):
        self.budget_usd = budget_usd
        self.generator = generator
        self.hitl = HITLGate(security_token=security_token)
        # Key-rotation alerts go through the SAME Telegram channel the HITL
        # gate posts approvals to: one ops alert stream (a rotation confirm is
        # a human override, just like a HITL approval). Without bot/chat creds
        # the handler is None and rotation alerts stay in the audit trail/CLI.
        _bot = os.environ.get("HITL_TELEGRAM_BOT_TOKEN")
        _chat = os.environ.get("HITL_TELEGRAM_CHAT_ID")
        _rotation_alert = None
        if _bot and _chat:
            _tg_handler = self.hitl.notify_telegram(_bot, _chat)

            def _rotation_alert(text: str) -> None:
                req = HITLRequest(request_id="key-rotation", raw_input=text,
                                  risk_score=50, violations=["key_rotation_pending"])
                try:
                    _tg_handler(req)
                except Exception:
                    pass
        # Promoted-rules storage: permanent, HMAC-signed, audited. The tempdir
        # experiment is gone — rules now live under .opencode/skills/auto-rules
        # with a project-root key and an audit trail in FeedbackLoop.
        # NOTE: NO operator_secret is passed here. The lockdown-release
        # credential is resolved by FeedbackLoop from its OWN dedicated source
        # (ROTATION_OPERATOR_SECRET or the separate 0600 .operator file) — it
        # must NEVER be the HITL security token.
        self.feedback = FeedbackLoop(rotation_notify=_rotation_alert)
        self.rules_skills_dir = SKILLS_ROOT
        self.rules_key_path = DEFAULT_HMAC_KEY_PATH
        self.verifier = VerifierEngine(
            max_attempts=max_attempts, generator=generator,
            hitl_gate=self.hitl,
            rules_dir=self.rules_skills_dir,
            rules_key_path=str(self.rules_key_path),
            rules_audit=self.feedback,
        )
        self.router = MockRouter(mappings=mock_mappings or {})
        self.client = RemoteAPIClient(router=self.router)
        self.hybrid = HybridRouter()
        self.elide_output = elide_output
        self.last_decision = {}
        # Open-source tool layer (probed lazily; never required to run)
        self.tools = ToolGateway(host=tools_host)
        self.litellm = LiteLLMFailover(budget_usd=budget_usd)
        self.prism = PrismMock()
        self.semgrep = SemgrepSAST()
        self.nuclei = NucleiScan()
        self._tool_report = {}
        # Production-hardening layer (observability + feedback + failover + VCS)
        self.metrics = MetricsRegistry()
        self.alerts = AlertManager(self.metrics)
        self.alerts.add_rule(AlertRule("error_rate_spike", "verifier_errors", ">", 10))
        self.alerts.add_rule(AlertRule("pending_hitl_flood", "pending_hitl", ">", 25))
        self.model_ladder = build_default_ladder()
        self.mfailover = FailoverDriver(self.model_ladder, metrics=self.metrics)
        self.vcs = WorkflowVersionControl()
        self.cost = CostLedger()
        self.fuzzer = AttackFuzzer()
        self.logger = StructLogger()
        # Weak-model hardening layer (#1, #4, #7): escalate on doubt, enrich with
        # retrieved context + human-veto lessons, all degraded gracefully.
        self.rag = default_rag()
        self.few_shot = FewShotAssembler()
        self.cascade = CascadeRouter(
            cheap_fn=lambda task: {"ok": True, "tier_cheap": True},
            frontier_fn=None)  # real frontier plugged via LiteLLM in prod
        # ---- Four-model coercion protocols (#1b ambiguity, #2 chain integrity,
        # #3 confidence calibration, #4 context enrichment) ----
        self.ambiguity = AmbiguityResolver(classify_fn=None)  # structural floor only
        self.chain_checker = ChainIntegrityChecker(judge_fn=None)  # deterministic only
        # Per-instance audit stores (isolated from other runs/tests).
        _tmp = tempfile.mkdtemp(prefix="jit_hardening_")
        self.calibrator = ConfidenceCalibrator(
            db_path=os.path.join(_tmp, "conf_cal.db"))
        self.lexicon = ImplicitIntentLexicon(
            db_path=os.path.join(_tmp, "imp_lex.db"),
            seed_enabled=True)
        self._intent_render_cache = ""
        # Autonomous self-evolution: measure a real gap with live model calls,
        # pull weaknesses from the audit trail, verify a fix with a real model,
        # and promote ONLY verified guard rules into auto-rules/rules.json for
        # the gates. No live model callbacks connected from here => the evolver
        # honestly reports "unmeasured / nothing promoted"; never invents a gap.
        self.evolver = AutonomousSelfEvolver(
            skills_dir=self.rules_skills_dir,
            weakness_source=WeaknessSource(feedback=self.feedback),
            key_path=self.rules_key_path,
            audit=self.feedback,
        )
        # Promoted-rules security: purge any legacy tempdir store, then verify
        # on-disk rules against the last known audited state. An unexplained
        # disappearance fires a security_incident alert IMMEDIATELY.
        self._purge_legacy_rule_store()
        self._check_rule_store_integrity()
        # Platform wiring: enforcement profile (None => legacy behavior
        # preserved exactly) + evidence sinks (volatile tmpdir unless the
        # caller pins evidence_dir). Sinks record audit/provenance/golden
        # evidence for every terminal decision without mutating verdicts.
        self.enforcement = platform_wiring.EnforcementProfile.from_dict(
            enforcement)
        self.evidence = platform_wiring.build_sinks(evidence_dir)
        self._task_capability: dict = {}

    def _purge_legacy_rule_store(self) -> None:
        """Remove any leftover jit_evolve_skills tempdir from before the move to
        permanent .opencode/skills/auto-rules storage. No purge on failure."""
        legacy = os.path.join(tempfile.gettempdir(), "jit_evolve_skills")
        if os.path.isdir(legacy):
            try:
                import shutil
                shutil.rmtree(legacy, ignore_errors=True)
            except OSError:
                pass

    def _check_rule_store_integrity(self) -> None:
        """Diff current promoted-rules vs last known audited state. Any mismatch
        not explained by a logged 'remove' => security_incident alert. A pending
        key rotation (fingerprint changed) fires a separate key_rotation alert
        and BLOCKS auto-acceptance until confirm_key_rotation()."""
        try:
            report = self.evolver.registry.check_startup_integrity()
        except Exception:
            report = {"status": "error",
                      "detail": "integrity check itself failed"}
        self._rules_integrity = report
        if report.get("status") == "security_incident":
            missing = ", ".join(report.get("missing", []) or ["?"])
            self.alerts.fire_incident(
                name="rule_store_tamper",
                detail=f"{report.get('detail')}; missing=[{missing}]",
            )
        elif report.get("status") == "key_rotation_pending":
            self.alerts.fire_incident(
                name="rule_store_key_rotation",
                detail=report.get("detail", "key fingerprint changed; "
                                   "confirm_key_rotation() required"),
            )
        elif report.get("status") == "lockdown":
            self.alerts.fire_incident(
                name="rule_store_lockdown",
                detail=report.get("detail", "rate-limit lockdown active; "
                                   "release_key_lockdown() required"),
            )

    # ---- Weak-model hardening helpers (#1/#4/#6/#7) ----
    def _confidence_for(self, task: str, workflow_json: dict) -> float:
        """Deterministic doubt detector: novel/risky shapes lower confidence."""
        score = 1.0
        task_lower = task.lower()
        # novelty: weak models are exactly bad at inventing new topologies
        if any(w in task_lower for w in ("brand new", "novel", "custom topology",
                                         "from scratch", "invent", "unusual")):
            score -= 0.3
        blob = json.dumps(workflow_json).lower()
        if "code" in blob or "jscode" in blob:
            score -= 0.25
        if "127.0.0.1" in blob or "localhost" in blob or "0.0.0.0" in blob:
            score -= 0.35
        if "webhook" in blob:
            score -= 0.15
        return max(0.0, round(score, 2))

    def _enrich_for_generation(self, task: str, workflow_json: dict) -> dict:
        """#4 + #7: pull RAG context + veto lessons to harden the generator."""
        ctx = self.rag.render_context(task) or "# no reference context retrieved"
        hits = self.rag.query(task)
        fewshot = self.few_shot.render_prompt_block(rule_keywords=["localhost", "ssrf", "code"])
        # Protocol #4: implicit-intent rules resolved from THIS phrasing.
        intent_rules = render_implicit_context(task, context="webhook")
        if intent_rules:
            fewshot = (fewshot + "\n" + intent_rules) if fewshot else intent_rules
        prompt = build_generator_prompt(
            task=task,
            rag_context=ctx,
            few_shot=fewshot,
            schema_hint='{"nodes": [{"name","type","parameters"}], "connections": {}}',
        )
        return {"prompt": prompt, "context_hits": len(hits)}

    def _schema_guard_result(self, workflow_json: dict):
        schema = {
            "type": "object",
            "required": ["nodes", "connections"],
            "properties": {
                "nodes": {"type": "array", "items": {"type": "object"}},
                "connections": {"type": "object"},
            },
        }
        guard = JsonSchemaGuard(schema, max_attempts=1)
        return guard.ensure(json.dumps(workflow_json, default=str))

    def _probe_tools(self) -> dict:
        """One-time capability probe; results embedded in the final report."""
        if self._tool_report:
            return self._tool_report
        st = self.tools.status(refresh=True)
        up = [k for k, v in st.__dataclass_fields__.items() if getattr(st, k)]
        self._tool_report = {
            "active_tools": up,
            "prism_base_url": self.prism.base_url if st.prism else None,
            "litellm_reachable": st.litellm,
        }
        return self._tool_report

    def _emit(self, *parts):
        if not self.elide_output:
            print(*parts)

    def _seal_result(self, result: dict, task_prompt: str,
                     workflow_json: dict | None = None,
                     scope: dict | None = None,
                     audit: dict | None = None,
                     decision: dict | None = None) -> dict:
        """Attach audit evidence to any terminal result (additive only).

        Appends one audit event per terminal decision and links
        provenance on READY deliveries. Never mutates the verdict.
        """
        try:
            fp = platform_wiring.task_fingerprint(task_prompt)
            entry = platform_wiring.audit_event(
                self.evidence, kind="orchestrator_decision",
                actor="orchestrator", subject=fp,
                detail=f"status={result.get('status')} "
                       f"reason={str(result.get('reason', ''))[:120]}")
            result = dict(result)
            result["evidence"] = {"audit_id": entry["id"],
                                  "audit_hash": entry["event_hash"],
                                  "task_fp": fp}
            if result.get("status") == "READY_FOR_DEPLOYMENT":
                prov = self.evidence["provenance"]
                prov.link(fp, "task", task_prompt[:160])
                if workflow_json:
                    prov.link(fp, "workflow",
                              str(result.get("snapshot_version", "unversioned")))
                prov.link(fp, "deployment", entry["event_hash"][:12])
                result["evidence"]["provenance_gaps"] = prov.gaps(fp)
        except Exception:
            pass
        return result

    def _golden_from_rejection(self, task_prompt: str,
                               violations: list) -> None:
        """Feed security rejections into the golden failure corpus."""
        try:
            fp = platform_wiring.task_fingerprint(task_prompt)
            for v in (violations or [])[:3]:
                cid = f"orch-{fp}-{abs(hash(str(v))) % 10000}"
                if cid not in self.evidence["golden"]._cases:
                    self.evidence["golden"].add_case(
                        cid, reproducer=str(v)[:200],
                        expect="must stay blocked",
                        incident=f"orchestrator:{fp}")
        except Exception:
            pass

    def execute_workflow_task(
        self,
        task_prompt: str,
        workflow_json: dict,
        daily_reqs: int = 1000,
        tech_stack: Optional[list[str]] = None,
        require_human_for_security: bool = True,
        business: Optional[dict] = None,
    ) -> dict:
        tech_stack = tech_stack or []
        self._emit(f"\n=== Orchestrating: {task_prompt} ===")
        self.metrics.inc("tasks_seen")
        self.logger.info("orchestrate_start", task=task_prompt[:80])

        # ---- STEP 0: AMBIGUITY GATE (protocol #1b) — runs BEFORE the planner.
        # Structural floor decides even without a judge model; if the task is
        # too ambiguous to execute, escalate to HITL instead of guessing. ----
        amb = self.ambiguity.assess(task_prompt, workflow_json)
        self._emit("[0] Ambiguity:", json.dumps({
            "score": amb.assessment.ambiguity_score,
            "verdict": amb.assessment.verdict,
            "declared": amb.assessment.declared,
            "missing_info": amb.assessment.missing_info[:3],
            "floored": amb.floored,
        }, indent=2, ensure_ascii=False))
        self.metrics.set_gauge("ambiguity_score", amb.assessment.ambiguity_score)
        if amb.assessment.verdict in ("CLARIFY", "ESCALATE"):
            # Don't invent — ask/triage. CLARIFY => HITL always (default-deny);
            # ESCALATE => frontier when available, else HITL (honest).
            if amb.assessment.verdict == "ESCALATE" and self.cascade.frontier_fn:
                pass  # a real frontier backend would retry; none configured here
            req = self.hitl.create_pending(
                raw_input=task_prompt,
                risk_score=max(int(amb.assessment.ambiguity_score * 100), 40),
                violations=[
                    "ambiguous task",
                    *(amb.assessment.missing_info or [])[:4],
                ],
                payload={"ambiguity": amb.assessment.to_dict()},
            )
            self.metrics.inc("pending_hitl")
            return self._seal_result(
                {"status": "PENDING_HUMAN_REVIEW",
                 "reason": "ambiguous task — clarifying question routed to HITL",
                 "hitl_request_id": req.request_id,
                 "clarifying_question": amb.assessment.clarifying_question,
                 "ambiguity": amb.assessment.to_dict()},
                task_prompt, workflow_json)

        # ---- STEP 0.1: AUTONOMOUS SELF-EVOLUTION — close known model gaps
        # BEFORE real work. Benchmark vs SOTA for this task domain; if the gap
        # exceeds threshold, synthesize a fix skill + verify it in the sandbox
        # (promotion only on 100% pass). Never blocks the task; results are
        # advisory and logged. ----
        try:
            domain = "cybersec_audit" if any(
                w in task_prompt.lower() for w in
                ("security", "audit", "red team", "safe", "ssrf", "vulnerab")) else \
                ("complex_coding" if any(
                    w in task_prompt.lower() for w in
                    ("code", "async", "workflow", "build", "integrat")) else
                 "long_context")
            evo = self.evolver.run_evolution_cycle(
                task_type=domain,
                current_model_fn=None,   # no live model => unmeasured, no promotion
                leader_fn=None,
                min_rejections=2,        # only convert recurring real rejections
            )
            self._emit("[0.1] Self-evolution:", json.dumps(evo.to_dict(),
                                                           indent=2,
                                                           ensure_ascii=False))
            self.metrics.set_gauge("evolution_gap_pct",
                                   evo.measured and evo.gap_pct or -1)
            if evo.promoted_count:
                self.metrics.inc("skills_promoted", evo.promoted_count)
            if evo.failures:
                self._emit("[0.1] Evolution failures:",
                           "\n".join(evo.failures))
        except Exception as e:  # never break the pipeline over the evolver
            self._emit("[0.1] Self-evolution skipped:", repr(e))

        # ---- STEP 0.5: Extended Thinking & Dual-Process Planner ----
        planner = ExtendedThinkingPlanner(budget_usd=self.budget_usd)
        services = [s for s in tech_stack if s in
                    ("telegram", "supabase", "stripe", "openai", "github", "slack")]
        plan = planner.plan_task(task_prompt, services=services or None)
        self._emit("[0] Planner:", json.dumps({
            "selected": plan.selected.name if plan.selected else None,
            "path_cost_usd": getattr(plan.selected, "est_usd", 0),
            "dag_nodes": len(plan.dag),
            "build_steps": len(plan.build_steps),
        }, indent=2, ensure_ascii=False))
        if plan.selected and plan.selected.verdict.startswith("REJECTED"):
            self._emit("    [Planner] warning: ", plan.selected.verdict)

        # ---- STEP 0.6: CHAIN INTEGRITY (protocol #2) — cumulative per-node
        # consistency of the plan DAG. Structural checks hard-fail; semantic
        # contradictions (when a judge model is present) force a replan. ----
        chain = check_dag_integrity(plan.dag)
        broken = [r.to_dict() for r in chain if not r.ok]
        self._emit("[0.6] Chain integrity:",
                   f"{len(chain) - len(broken)}/{len(chain)} steps consistent"
                   + (f" — BROKEN: {[b['structural_issue'] for b in broken]}" if broken else ""))
        self.metrics.set_gauge("chain_broken_steps", len(broken))
        if broken:
            return {"status": "REJECTED",
                    "reason": "plan DAG has integrity violations",
                    "chain_issues": [b["structural_issue"] for b in broken][:5]}

        # ---- STEP 0b: Zero-Trust redaction (protects STORAGE only; the
        # analysis/attack path below uses the raw workflow so secrets are
        # actually found, not hidden from the red-team) ----
        redactor = SecretRedactor()
        vault = SecretVault()
        redacted_wf, found_secrets = vault.register_payload(workflow_json)
        if found_secrets:
            self._emit("[0b] REDACTED", len(found_secrets),
                       "secret(s) before processing. Secrets masked,"
                       "never stored to audit/RAG.")
        self._redacted_storage_copy = redacted_wf

        # ---- STEP 0c: Weak-model hardening (#1 cascade, #6 schema, #4+#7 enrichment).
        # Escalate when the cheap model shows doubt; reject structurally invalid
        # workflow JSON deterministically before any model reasoning is wasted. ----
        conf = self._confidence_for(task_prompt, workflow_json)
        # Protocol #3: calibrate confidence by measured history, not self-report.
        category = "webhook-build" if "webhook" in task_prompt.lower() else "general"
        pred_id = self.calibrator.log_prediction(category, conf)
        effective_conf = self.calibrator.effective_confidence(category, conf)
        self._intent_render_cache = render_implicit_context(
            task_prompt, context="webhook")
        route = self.cascade.route(
            task_prompt,
            {"ok": True, "confidence": effective_conf, "has_artifact": True})
        enrichment = self._enrich_for_generation(task_prompt, workflow_json)
        schema_result = self._schema_guard_result(workflow_json)
        self._emit("[0c] Hardening:",
                   json.dumps({
                       "stated_conf": conf,
                       "effective_conf": effective_conf,
                       "tier": route["tier"],
                       "rag_hits": enrichment["context_hits"],
                       "schema_ok": schema_result.ok,
                       "schema_errors": schema_result.errors[:3],
                   }, indent=2, ensure_ascii=False))
        self.metrics.set_gauge("hardening_tier", {"CHEAP": 1, "FRONTIER": 2,
                                                  "HITL": 3}.get(route["tier"], 0))
        if route["tier"] in ("FRONTIER", "CHEAP_FALLBACK") and not self.cascade.frontier_fn:
            # no frontier backend configured -> human decides (honest escalation)
            self.calibrator.record_outcome(pred_id, accepted=False)
            self.metrics.inc("calibrated_escalations")
            req = self.hitl.create_pending(
                raw_input=task_prompt,
                risk_score=max(effective_conf * 100, 40),
                violations=["low-confidence route to unconfigured frontier"],
                payload={"hardening": {"confidence": effective_conf},
                         "calibration_category": category},
            )
            self.metrics.inc("pending_hitl")
            return self._seal_result(
                {"status": "PENDING_HUMAN_REVIEW",
                 "reason": "cascade escalation (frontier unconfigured)",
                 "hitl_request_id": req.request_id,
                 "hardening": {"confidence": effective_conf,
                               "tier": route["tier"]}},
                task_prompt, workflow_json)
        if not schema_result.ok:
            self.calibrator.record_outcome(pred_id, accepted=False)
            self.metrics.inc("schema_rejections")
            return self._seal_result(
                {"status": "REJECTED",
                 "reason": "workflow JSON violates contract schema",
                 "schema_errors": schema_result.errors[:5],
                 "hardening": {"tier": route["tier"]}},
                task_prompt, workflow_json)

        # ---- STEP 0d: ENFORCED POLICY GATE (no-op without a profile).
        # A configured policy decides BEFORE spend/planning side effects.
        # Deny => audited PENDING_HUMAN_REVIEW; approve => HITL pending;
        # allow => mint a task capability used by the egress step below.
        if self.enforcement is not None:
            verdict = platform_wiring.policy_gate(
                self.enforcement, agent="orchestrator",
                action="workflow.execute", resource=task_prompt[:64])
            self._emit("[0d] Policy:", json.dumps(
                {k: v for k, v in verdict.items() if k != "token"},
                ensure_ascii=False))
            if not verdict["allowed"] and not verdict["needs_approval"]:
                platform_wiring.audit_event(
                    self.evidence, kind="policy_denial",
                    actor="orchestrator",
                    subject=platform_wiring.task_fingerprint(task_prompt),
                    detail=f"rule={verdict['rule']} {verdict['reason']}")
                self._golden_from_rejection(
                    task_prompt, [f"policy:{verdict['rule']}"])
                req = self.hitl.create_pending(
                    raw_input=task_prompt,
                    risk_score=60,
                    violations=[f"policy denial: {verdict['rule']}"],
                    payload={"policy": verdict},
                )
                self.metrics.inc("pending_hitl")
                return self._seal_result(
                    {"status": "PENDING_HUMAN_REVIEW",
                     "reason": f"policy denial — {verdict['reason']}",
                     "hitl_request_id": req.request_id,
                     "policy": {k: v for k, v in verdict.items()
                                if k != "token"}},
                    task_prompt, workflow_json)
            if verdict["needs_approval"]:
                req = self.hitl.create_pending(
                    raw_input=task_prompt,
                    risk_score=50,
                    violations=[f"policy approval: {verdict['rule']}"],
                    payload={"policy": verdict},
                )
                self.metrics.inc("pending_hitl")
                return self._seal_result(
                    {"status": "PENDING_HUMAN_REVIEW",
                     "reason": f"policy approval — {verdict['reason']}",
                     "hitl_request_id": req.request_id,
                     "policy": {k: v for k, v in verdict.items()
                                if k != "token"}},
                    task_prompt, workflow_json)
            cap = platform_wiring.mint_task_capability(
                self.enforcement, actions=["net.fetch", "code.execute"],
                resource="task:*", ttl_s=900)
            self._task_capability = cap

        # ---- STEP 1: Brutal budget + honesty audit ----
        audit = BrutallyHonestBudgetAnalyzer.audit_task(
            monthly_budget_usd=self.budget_usd,
            daily_requests=daily_reqs,
            avg_tokens=800,
            proposed_tech_stack=tech_stack,
        )
        self._emit("[1] Budget Audit:", json.dumps(
            {k: v for k, v in audit.items() if k != "critique_notes"},
            indent=2, ensure_ascii=False))
        for note in audit["critique_notes"]:
            self._emit("   ", note)

        if not audit["viable"]:
            self._emit("[ABORT] Task not financially viable. No deployment.")
            return self._seal_result({"status": "BUDGET_REJECTED",
                                      "audit": audit},
                                     task_prompt, workflow_json)

        # ---- STEP 2: JIT task-scoped knowledge ----
        jit = TaskScopedJITRAG(task_prompt)
        scope = None
        decision = None
        try:
            scope = self._collect_scope(task_prompt)
            self._emit("[2] Scope:",
                       json.dumps(scope, indent=2, ensure_ascii=False))

            # ---- STEP 2b: Adversarial Red-Team agent (sees RAW workflow) ----
            redteam = CyberSecRedTeamAgent()
            rt_report = redteam.audit_workflow(workflow_json)
            # 2b+ attack fuzzer: mutate seeds and check whether THIS workflow
            # would slip through a mutated variant the static rules miss.
            fuzz_report = self.fuzzer.audit_with_fuzzing()
            self._emit(f"[2b+] Fuzzer: {fuzz_report['probes_generated']} probes, "
                       f"{fuzz_report['escaped_from_gate']} gate-escapers (global)")
            self.metrics.set_gauge("fuzz_escaped_total", fuzz_report["escaped_from_gate"])
            # Only escalate when an escaped family actually matches THIS payload.
            workflow_blob = json.dumps(workflow_json, default=str).lower()
            escaped_here = [
                e for e in fuzz_report["escaped_examples"]
                if e["probe"].lower().split("(")[0][:12] and
                e["probe"].lower()[:40] in workflow_blob
            ]
            self._emit("[2b] Red-Team:",
                       "passed" if rt_report["red_team_passed"] else
                       f"BLOCKED — {rt_report['vulnerabilities']}")
            if not rt_report["red_team_passed"] or escaped_here:
                violations = list(rt_report["vulnerabilities"])
                for e in escaped_here:
                    violations.append(f"Fuzzer catch: '{e['probe'][:60]}' ({e['vector']})")
                self._emit("    [REDTEAM] adversarial findings routed to HITL:")
                for vuln in violations:
                    self._emit("       -", vuln)
                req = self.hitl.create_pending(
                    raw_input=task_prompt,
                    risk_score=max(rt_report["max_severity"] or 40, 40),
                    violations=violations,
                    payload={"red_team": rt_report, "fuzzer": fuzz_report},
                )
                self.metrics.inc("pending_hitl")
                # feedback loop: humans keep refusing these — capture for future
                for v in rt_report["vectors"]:
                    self.feedback.record_rejection(v, reason="redteam finding")
                extra_suffix = " + fuzzer variants" if escaped_here else ""
                self.last_decision = {
                    "status": "PENDING_HUMAN_REVIEW",
                    "reason": "Red-Team adversarial findings" + extra_suffix,
                    "hitl_request_id": req.request_id,
                    "red_team": rt_report,
                }
                if require_human_for_security:
                    self._golden_from_rejection(task_prompt, violations)
                    platform_wiring.handle_failure(
                        self.evidence,
                        incident_id="redteam-" + platform_wiring.task_fingerprint(
                            task_prompt),
                        alert={"agent": "orchestrator", "session": "task",
                               "kind": "redteam", "ts": time.time(),
                               "detail": "; ".join(violations[:3])},
                        golden_case={
                            "id": "rt-redteam-" + platform_wiring.task_fingerprint(
                                task_prompt),
                            "reproducer": "; ".join(violations[:2])[:200],
                            "expect": "must stay blocked"})
                    return self._seal_result(
                        {"status": "PENDING_HUMAN_REVIEW",
                         "reason": "Red-Team adversarial findings" + extra_suffix,
                         "hitl_request_id": req.request_id,
                         "red_team": rt_report,
                         "scope": scope, "audit": audit},
                        task_prompt, workflow_json, scope, audit)
            else:
                # ---- STEP 2c: Execution-guided code sandbox (Code nodes) ----
                # Enforcement profile swaps in the hardened agent_sandbox
                # tier (docker-strong when available) through a call-shape
                # shim — the check logic below is untouched.
                if self.enforcement is not None:
                    sandbox = platform_wiring.AgentSandboxShim(
                        prefer_docker=self.enforcement.sandbox_docker)
                else:
                    sandbox = ExecutionSandbox(use_docker=False)
                runtime = save_code_nodes_runtime_check(workflow_json, sandbox)
                failures = [r for r in runtime if not r.get("success")]
                self._emit("[2c] Code-node runtime checks:",
                           f"{len(runtime) - len(failures)}/{len(runtime)} passed")
                if failures:
                    self._emit("    [SANDBOX] failing node(s):",
                               [f["node"] for f in failures])
                    self.last_decision = {
                        "status": "REJECTED",
                        "reason": "Execution sandbox runtime failure",
                        "sandbox_failures": failures,
                    }
                    return self._seal_result(
                        {"status": "REJECTED",
                         "reason": "Execution sandbox runtime failure",
                         "sandbox_failures": failures,
                         "scope": scope, "audit": audit},
                        task_prompt, workflow_json, scope, audit)

            # ---- STEP 2d: ENFORCED EGRESS + CAPABILITY (no-op unconfigured).
            # Every external URL in the workflow is validated; each fetch
            # must also sit inside the task capability minted at step 0d.
            if self.enforcement is not None and (
                    self.enforcement.egress is not None
                    or self._task_capability.get("enforced")):
                urls = platform_wiring.extract_external_urls(workflow_json)
                gate = platform_wiring.egress_guard(self.enforcement, urls)
                cap_blocked = []
                issuer = self._task_capability.get("issuer")
                token = self._task_capability.get("token")
                if issuer is not None and token:
                    import urllib.parse as _up
                    for url in gate["allowed"]:
                        host = _up.urlsplit(url).hostname or ""
                        chk = platform_wiring.check_capability(
                            issuer, token, action="net.fetch",
                            resource=host or "*")
                        if not chk["ok"]:
                            cap_blocked.append({"url": url,
                                                "reason": chk["reason"]})
                violations = [f"egress: {b['url']} ({b['reason']})"
                              for b in gate["blocked"]]
                violations += [f"capability: {b['url']} ({b['reason']})"
                               for b in cap_blocked]
                self._emit("[2d] Egress:",
                           f"{len(gate['allowed'])} allowed, "
                           f"{len(violations)} blocked")
                if violations:
                    self._golden_from_rejection(task_prompt, violations)
                    req = self.hitl.create_pending(
                        raw_input=task_prompt,
                        risk_score=60,
                        violations=violations,
                        payload={"egress": gate,
                                 "capability": cap_blocked},
                    )
                    self.metrics.inc("pending_hitl")
                    return self._seal_result(
                        {"status": "PENDING_HUMAN_REVIEW",
                         "reason": "Egress/capability denial",
                         "hitl_request_id": req.request_id,
                         "egress": gate,
                         "scope": scope, "audit": audit},
                        task_prompt, workflow_json, scope, audit)

            # ---- STEP 3: scoped verification ----
            decision = self.verifier.verify_and_route(workflow_json)
            self._emit("[3] Verifier decision:", decision["status"])
            self.last_decision = decision

            # ---- STEP 3b: BUSINESS INVARIANTS (skipped without payload).
            # A technically green delivery that violates domain truth must
            # not deploy: the payload fails closed to human review.
            if decision["status"] == "READY_FOR_DEPLOYMENT" and business:
                from business_invariants import InvariantEngine
                engine = InvariantEngine()
                for name, fn, doc in business.get("checks", []) or []:
                    engine.register(business.get("domain", "default"),
                                    name, fn, doc or "")
                inv = engine.evaluate(business.get("domain", "default"),
                                      business.get("payload", {}))
                self._emit("[3b] Invariants:",
                           "pass" if inv["ok"] else
                           f"FAIL — {[f['name'] for f in inv['failed']]}")
                if not inv["ok"]:
                    self._golden_from_rejection(
                        task_prompt,
                        [f"invariant:{f['name']}" for f in inv["failed"]])
                    req = self.hitl.create_pending(
                        raw_input=task_prompt,
                        risk_score=60,
                        violations=[f"invariant {f['name']}: {f['reason']}"
                                    for f in inv["failed"]],
                        payload={"invariants": inv, "business": {
                            k: v for k, v in business.items()
                            if k != "checks"}},
                    )
                    self.metrics.inc("pending_hitl")
                    return self._seal_result(
                        {"status": "PENDING_HUMAN_REVIEW",
                         "reason": "Business invariant failure",
                         "hitl_request_id": req.request_id,
                         "invariants": inv,
                         "scope": scope, "audit": audit},
                        task_prompt, workflow_json, scope, audit,
                        decision)

            if decision["status"] == "READY_FOR_DEPLOYMENT":
                self._emit("    Safety+Quality passed. Deploy directive ready.")
                self._emit("[5] Tools probed:", self._probe_tools())
                # metrics + version ledger + cost stub (real spend comes from
                # LiteLLM feeder; record here the decision path only)
                self.metrics.inc("tasks_deployed")
                self.metrics.observe("gate_latency_ms",
                                     daily_reqs % 100 + 1)   # latency placeholder
                # Protocol #3: the verifier+human accepted -> record measured truth.
                self.calibrator.record_outcome(pred_id, accepted=True)
                version = self.vcs.snapshot(
                    workflow_id=task_prompt[:24].replace(" ", "_"),
                    workflow=workflow_json, name="orchestrated")
                self.logger.info("deploy_directive", task=task_prompt[:80],
                                 version=version)
                self.alerts.evaluate()
                return self._seal_result(
                    {"status": "READY_FOR_DEPLOYMENT", "decision": decision,
                     "scope": scope, "tools": self._probe_tools(),
                     "snapshot_version": version,
                     "hardening": {"confidence": effective_conf,
                                   "stated_confidence": conf,
                                   "calibration_category": category,
                                   "adjusted_threshold": self.calibrator.get_adjusted_threshold(category),
                                   "intent_rules": self._intent_render_cache,
                                   "tier": route["tier"],
                                   "rag_hits": enrichment["context_hits"]},
                     "metrics": self.metrics.snapshot()},
                    task_prompt, workflow_json, scope, audit, decision)
            if decision["status"] == "PENDING_HUMAN_REVIEW":
                idx = decision.get("hitl_request_id", "")
                self._emit(f"    [HITL] request {idx} awaiting human decision "
                           f"(approve/reject). Default-deny after timeout.")
                # feedback loop: capture rejection vectors for future auto-tighten
                for v in decision.get("violations", [])[:3]:
                    self.feedback.record_rejection(v, reason="verifier hitl")
                self.metrics.inc("pending_hitl")
                if require_human_for_security:
                    self._golden_from_rejection(
                        task_prompt, decision.get("violations", [])[:3])
                    return self._seal_result(
                        {"status": "PENDING_HUMAN_REVIEW",
                         "hitl_request_id": idx, "decision": decision,
                         "scope": scope, "audit": audit,
                         "feedback": self.feedback.rejection_summary()},
                        task_prompt, workflow_json, scope, audit, decision)
            # SOLVED via generator loop or rejected by quality
            self._golden_from_rejection(
                task_prompt, (decision.get("violations", [])
                              if isinstance(decision, dict) else [])[:3])
            return self._seal_result(
                {"status": decision.get("status", "REJECTED"),
                 "decision": decision, "scope": scope, "audit": audit},
                task_prompt, workflow_json, scope, audit, decision)
        finally:
            # ---- STEP 4: purge ephemeral RAG + sweep secret vault ----
            purged = jit.purge_context()
            vault.sweep()
            self._emit(f"[4] Ephemeral RAG purged: {purged} | vault swept")

    def _collect_scope(self, task_prompt: str) -> dict:
        """Draft the scope declaration (required_apis / docs / rejected tech)."""
        lower = task_prompt.lower()
        apis = []
        for svc in ("telegram", "supabase", "stripe", "openai", "hubspot",
                    "meta", "facebook", "slack", "github"):
            if svc in lower:
                apis.append(svc)
        rejected = []
        if "vector db" in lower or "vector_db" in lower:
            rejected.append("vector_db (SQLite FTS5 sufficient at this scale)")
        return {
            "task_id": "auto_generated",
            "required_apis": apis,
            "needed_docs": [f"{a} official API schema (fetch scoped)" for a in apis],
            "rejected_overengineering": rejected,
        }


# ============================================================
# Entry point
# ============================================================
if __name__ == "__main__":
    orch = SystemOrchestrator(
        budget_usd=20.0, mock_mappings={"api.example.com": "http://127.0.0.1:9191"})

    print("\n" + "#" * 70)
    print("# CASE 1: Telegram webhook -> Supabase (with vector_db over-engineering)")
    print("#" * 70)
    flow = {
        "nodes": [
            {"name": "Telegram Webhook", "type": "n8n-nodes-base.telegramTrigger",
             "parameters": {"path": "orders", "pinnedData": {"1": {"json": {}}}}},
            {"name": "Send to Supabase", "type": "n8n-nodes-base.httpRequest",
             "parameters": {"url": "https://supabase.co/rest/v1/orders"}},
        ],
        "connections": {
            "Telegram Webhook": {"main": [{"node": "Send to Supabase"}]},
        },
    }
    orch.execute_workflow_task(
        task_prompt="Telegram webhook for orders, send order to Supabase",
        workflow_json=flow,
        daily_reqs=1000,
        tech_stack=["vector_db", "supabase_free", "deepseek"],
    )

    print("\n" + "#" * 70)
    print("# CASE 2: malicious code node -> HITL gate")
    print("#" * 70)
    bad = {
        "nodes": [
            {"type": "n8n-nodes-base.code",
             "parameters": {"jsCode": "require('child_process').exec('rm -rf /')"}},
        ],
        "connections": {},
    }
    orch.execute_workflow_task(
        task_prompt="run a cleanup script on the server",
        workflow_json=bad,
        daily_reqs=100,
        tech_stack=["deepseek"],
    )