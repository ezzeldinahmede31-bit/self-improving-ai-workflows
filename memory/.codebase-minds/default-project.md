# default-project mind map (mechanical AST pass)

## Inventory & entry points
- .: 32 files
- client_portal: 1 files
- scripts: 12 files
- tests: 20 files
- TOTAL: 65 files | {'.py': 65}

## Symbols (public top-level name:line)
- ambiguity_resolver.py: AmbiguityAssessment(54), AmbiguityResult(129), AmbiguityResolver(134), structural_ambiguity(74), parse_contract(108)
    +4 more (see .json)
- attack_fuzzer.py: MutationEngine(34), ProbeVerdict(63), FuzzResult(70), AttackFuzzer(78), mutate(48)
    +3 more (see .json)
- auto_self_evolver.py: RuleTamperingError(71), ProbeError(109), BenchmarkReport(151), WeaknessSource(229), SkillRegistry(274)
    +27 more (see .json)
- cascade_routing.py: ConfidenceEstimate(43), CascadeRouter(71), Candidate(149), SelfConsistencyPool(156), ChecklistItem(207)
    +9 more (see .json)
- chain_integrity_checker.py: StepReview(53), ChainIntegrityChecker(130), structural_integrity_check(74), check_dag_integrity(185), to_dict(63)
    +1 more (see .json)
- confidence_calibrator.py: ConfidenceCalibrator(39), build_calibrated_cascade(161), log_prediction(69), record_outcome(85), effective_confidence(125)
    +3 more (see .json)
- context_enrichment.py: ExplicitRule(54), ImplicitIntentLexicon(66), resolve_implicit(187), render_implicit_context(191), to_dict(61)
    +5 more (see .json)
- cost_ledger.py: CostLedger(23), LiteLLMFeeder(120), record(58), set_budget(71), spend_by_workflow(82)
    +3 more (see .json)
- cybersec_sandbox_engine.py: RedTeamFinding(29), CyberSecRedTeamAgent(36), ExecutionSandbox(157), save_code_nodes_runtime_check(244), audit_workflow(79)
    +5 more (see .json)
- dual_process_planner.py: DAGNode(18), ArchitectPath(27), DualPlan(38), ExtendedThinkingPlanner(46), plan_dag(55)
    +5 more (see .json)
- feedback_loop.py: AuditStoreTamperingError(58), RotationRejectedError(64), RotationLockedError(69), RejectionPattern(82), FeedbackLoop(89)
    +21 more (see .json)
- hitl_gate.py: HITLState(30), HITLRequest(38), ApprovalWithheldError(69), HITLGate(73), cli_approve(321)
    +9 more (see .json)
- local_routing.py: ExecLocale(14), RoutingDecision(21), HybridRouter(43), ollama_command(95), route(51)
- lora_dataset.py: DatasetStats(25), LoRADatasetExporter(32), export_jsonl(76), few_shot_from_corpus(92)
- master_system_orchestrator.py: BrutallyHonestBudgetAnalyzer(70), TaskScopedJITRAG(147), SystemOrchestrator(207), audit_task(74), ingest_jit_docs(170)
    +4 more (see .json)
- mock_server.py: MockHandler(26), MockAPIServer(73), log_message(69), base_url(91), start(94)
    +2 more (see .json)
- model_failover.py: ModelLeg(30), ModelLadder(41), FailoverDriver(144), build_default_ladder(125), record_success(52)
    +6 more (see .json)
- observability.py: StructLogger(39), Histogram(78), MetricsRegistry(92), AlertRule(180), AlertManager(188)
    +23 more (see .json)
- prompt_assembler.py: FewShotAssembler(22), build_generator_prompt(59), negative_examples(26), render_prompt_block(38)
- quality_gate.py: QualityResult(35), QualityGate(41), evaluate(108), evaluate_to_dict(170)
- quirks_memory.py: init_quirks_db(22), remember_quirk(41), query_quirks(60), render_as_prompt(87)
- rag_engine.py: RagMemory(30), default_rag(150), ingest(61), query(84), render_context(120)
    +2 more (see .json)
- remote_api.py: EgressBlockedError(40), TelemetryEntry(45), MockRouter(108), RemoteAPIClient(163), init_telemetry_db(55)
    +6 more (see .json)
- remote_api_adapter.py: RemoteNodeSpec(18), RemoteAPIAdapter(65), to_n8n_node(27), from_curl(74), from_openapi(143)
    +1 more (see .json)
- schema_guard.py: SchemaResult(22), JsonSchemaGuard(29), CallResult(136), FunctionCallContract(144), validate(41)
    +2 more (see .json)
- scripts/ai_skill_standards_updater.py: log(64), fetch(75), strip_html(83), extract(92), build_snapshot(100)
    +6 more (see .json)
- scripts/build_gates_pipeline.py: MathLogicGate(385), DeepReasoningGate(471), ErrorPatternDB(527), AttemptGuard(582), SchemaPreflightGate(622)
    +16 more (see .json)
- scripts/build_repo_mind.py: iter_source_files(35), py_symbols(43), js_ts_symbols(80), build(93), render_md(159)
    +1 more (see .json)
- scripts/gate_complaints.py: ComplaintsRegistry(132), extract_keywords(87), default_find_skills(368), default_install_skill(395), default_create_skill(413)
    +5 more (see .json)
- scripts/gate_skill_invoker.py: SkillInvocationError(82), find_skill(87), load_router_registry(116), verify_skill_readiness(128), run_mandatory_skills_for_gate(153)
    +1 more (see .json)
- scripts/memory-encode.py: encode(17), decode(24), bits(33)
- scripts/n8n_stability_verifier.py: StabilityResult(58), get_execution_method(77), fetch_workflow(88), trigger_workflow_execution(231), compare_with_expected(295)
    +3 more (see .json)
- scripts/opencode_to_sleep.py: load_session_messages(77), export_session(105), main(159)
- scripts/router_register.py: read_frontmatter(51), classify(63), ensure_routing_row(72), ensure_registry_entry(87), bump_total(143)
    +1 more (see .json)
- scripts/skills_docs_generator.py: fallback_bucket(54), parse_frontmatter(63), extract_headers(109), extract_commands(114), skill_doc_path(134)
    +5 more (see .json)
- scripts/swe_local_harness.py: sh(30), find_fix_commits(37), run_tests(65), test_tokens(78), grade(82)
    +1 more (see .json)
- scripts/zap2n8n.py: uid(30), get_field(113), lookup(123), parse_trigger_export(142), port_inputs(154)
    +2 more (see .json)
- secret_redactor.py: SecretRedactor(23), SecretVault(84), redact_workflow(121), shannon_entropy(38), scan_and_redact(54)
    +5 more (see .json)
- secrets_provider.py: SecretBackend(26), EnvBackend(33), FileBackend(40), VaultBackend(72), SecretManager(96)
    +7 more (see .json)
- security_gate.py: SecurityFindings(97), SecurityGate(104), evaluate(429), evaluate_to_dict(537)
- tests/test_ai_automation_security.py: TestToolScopeLock(22), TestPromptInjectionAutoFix(49), TestCredentialToolBinding(80), TestChainedHighRisk(104), TestWebhookAuth(141)
    +29 more (see .json)
- tests/test_auto_self_evolver.py: TestBenchmark(66), TestWeaknessSource(108), TestProbes(145), TestSkillRegistry(182), TestEvolutionCycle(249)
    +46 more (see .json)
- tests/test_build_gates_pipeline.py: test_clean_workflow_approved(56), test_child_process_is_fatal(67), test_ssrf_metadata_is_fatal(75), test_hardcoded_secret_is_fatal(81), test_bare_json_quality_reject(95)
    +49 more (see .json)
- tests/test_cognitive_modules.py: TestExtendedThinkingPlanner(24), TestCyberSecRedTeamAgent(69), TestExecutionSandbox(134), TestSecretRedactor(174), TestOrchestratorIntegration(221)
    +28 more (see .json)
- tests/test_e2e_live_n8n.py: TestLiveN8nE2E(42), cleanup(47), test_create_workflow_via_api(59)
- tests/test_gate_complaints.py: test_extract_keywords_filters_stopwords(50), test_extract_keywords_respects_limit(57), test_record_skill_gap_writes_complaint(66), test_record_skill_gap_suppressed_when_local_skill_covers(79), test_record_skill_gap_dedupes_open_complaints(87)
    +14 more (see .json)
- tests/test_hitl_gate.py: TestHITLStateMachine(36), TestHITLTimeout(95), TestHITLNotification(130), TestHITLVerifierIntegration(154), db_path(22)
    +21 more (see .json)
- tests/test_master_orchestrator.py: TestBudgetAnalyzer(17), TestTaskScopedJITRAG(73), TestOrchestrator(101), test_viable_small_scale(18), test_low_budget_viable_deepseek(26)
    +12 more (see .json)
- tests/test_model_coercion_protocols.py: TestAmbiguityResolver(27), TestChainIntegrity(91), TestConfidenceCalibrator(144), TestContextEnrichment(183), TestOrchestratorProtocols(218)
    +28 more (see .json)
- tests/test_n8n_precision_gate.py: test_is_trigger_node(53), test_extract_node_refs(64), test_duplicate_node_names_fail(74), test_no_trigger_fails(85), test_subworkflow_escape_hatch_skips_p2(92)
    +64 more (see .json)
- tests/test_n8n_stability_verifier.py: TestCompareWithExpected(50), TestTriggerWorkflowExecution(64), TestVerifyStability(154), TestExecutionMethodAndWebhook(241), TestTriggerWebhook(297)
    +65 more (see .json)
- tests/test_orchestrator_hardening_wiring.py: TestOrchestratorHardening(15), orch(9), test_schema_violation_rejected_before_verify(16), test_low_confidence_escalates_to_hitl(26), test_valid_workflow_reaches_deploy_with_hardening(38)
    +1 more (see .json)
- tests/test_production_hardening.py: TestStructLogger(35), TestMetricsRegistry(52), TestAlertManager(69), TestModelLadder(94), TestFailoverDriver(136)
    +36 more (see .json)
- tests/test_promoted_rules_security.py: TestWrongSignature(118), TestPermissionCheck(145), TestStartupIntegrity(165), TestKeyRotationVsTampering(196), TestAttackerInjection(294)
    +35 more (see .json)
- tests/test_remote_adaptation.py: TestMockRouter(42), TestRemoteAPIClient(72), TestTelemetry(107), TestRemoteAPIAdapter(120), TestQuirksMemory(171)
    +26 more (see .json)
- tests/test_router_register.py: test_read_frontmatter_extracts_name_and_description(61), test_read_frontmatter_missing_description(69), test_read_frontmatter_no_frontmatter(78), test_classify_matches_keyword_bucket(92), test_classify_n8n_preferred_bucket(96)
    +16 more (see .json)
- tests/test_security_governance.py: TestClassification(37), TestSecurityOverride(68), TestExecutionAndVerification(118), TestAuditDatabase(148), TestEscalationLogic(204)
    +20 more (see .json)
- tests/test_tool_gateway.py: TestCapabilityProbe(29), TestLiteLLMFailover(52), TestPrismMock(100), TestScannersWithoutImages(112), TestOrchestratorTools(162)
    +25 more (see .json)
- tests/test_verifier_engine.py: TestSecurityGate(28), TestQualityGate(109), TestVerifierEngine(168), sec_gate(14), qual_gate(19)
    +17 more (see .json)
- tests/test_weak_model_hardening.py: TestCascadeRouter(35), TestSelfConsistencyPool(81), TestGeneratorCriticSplit(108), TestRagMemory(140), TestMicroDecompose(173)
    +38 more (see .json)
- tiered_pipeline.py: TaskType(135), Confidence(143), TaskClassification(150), VerificationResult(161), PipelineResult(169)
    +20 more (see .json)
- tool_gateway.py: ToolStatus(51), ToolGateway(61), LiteLLMResult(112), LiteLLMFailover(119), PrismMock(176)
    +12 more (see .json)
- verifier_engine.py: VerifierEngine(17), build_standard_verification_payload(159), verify_and_route(74)
- workflow_versions.py: WorkflowVersionControl(23), snapshot(56), get(76), diff(92), rollback(112)
    +1 more (see .json)

## Module summaries (truncated)
- ambiguity_resolver.py: Ambiguity Resolver — forced-ex
- attack_fuzzer.py: Adversarial attack FUZZER — tu
- auto_self_evolver.py: Autonomous Self-Evolution Engi
- cascade_routing.py: Cascade Routing — the #1 highe
- chain_integrity_checker.py: Chain Integrity Checker — cumu
- confidence_calibrator.py: Confidence Calibrator — extern
- context_enrichment.py: Context Enrichment — implicit-
- cost_ledger.py: Per-workflow / per-tenant cost
- cybersec_sandbox_engine.py: Adversarial Red-Team & Executi
- dual_process_planner.py: Extended Thinking & Dual-Proce
- feedback_loop.py: Feedback loop — the system LEA
- hitl_gate.py: Human-in-the-Loop (HITL) Gate 
- local_routing.py: Hybrid Speculative Model Routi
- lora_dataset.py: LoRA dataset exporter — #8.
- master_system_orchestrator.py: Master System Orchestrator — "
- mock_server.py: Bundled local Mock API server 
- model_failover.py: Model failover made REAL — not
- observability.py: Observability — structured JSO
- prompt_assembler.py: Few-shot prompt assembler — #7
- quality_gate.py: Programmatic implementation of
- quirks_memory.py: Remote-API Quirks & RAG Memory
- rag_engine.py: Real task-scoped RAG — #4.
- remote_api.py: Local-first Egress layer for n
- remote_api_adapter.py: Universal Remote API Adapter.
- schema_guard.py: Structured output enforcement 
- scripts/ai_skill_standards_updater.py: Daily auto-evolution for the A
- scripts/build_gates_pipeline.py: Build Gates Pipeline — runs AL
- scripts/build_repo_mind.py: Mechanical codebase mind-map b
- scripts/gate_complaints.py: ComplaintsRegistry — per-gate 
- scripts/gate_skill_invoker.py: GateSkillInvoker — mandatory-s
- scripts/memory-encode.py: Memory compact encoder.
- scripts/n8n_stability_verifier.py: Stability verifier — runs a de
- scripts/opencode_to_sleep.py: Bridge: export opencode sessio
- scripts/router_register.py: Register newly installed skill
- scripts/skills_docs_generator.py: Generate a per-skill documenta
- scripts/swe_local_harness.py: swe_local_harness.py — run a l
- scripts/zap2n8n.py: zap2n8n.py — Convert exported 
- secret_redactor.py: Zero-Trust Secret Redactor & V
- secrets_provider.py: Real secret management — plugg
- security_gate.py: Programmatic implementation of
- tests/test_ai_automation_security.py: Tests for the 8 AI-automation 
- tests/test_auto_self_evolver.py: Tests for the Autonomous Self-
- tests/test_build_gates_pipeline.py: Tests for the Build Gates Pipe
- tests/test_cognitive_modules.py: Tests for the 4 Cognitive & Cy
- tests/test_e2e_live_n8n.py: LIVE end-to-end test against t
- tests/test_gate_complaints.py: Tests for the per-gate Complai
- tests/test_model_coercion_protocols.py: Tests for the four "weak model
- tests/test_n8n_precision_gate.py: Tests for the N8nPrecisionGate
- tests/test_n8n_stability_verifier.py: Tests for scripts/n8n_stabilit
- tests/test_orchestrator_hardening_wiring.py: End-to-end wiring of the weak-
- tests/test_production_hardening.py: Tests for the 8 production-har
- tests/test_promoted_rules_security.py: Promoted-rules storage securit
- tests/test_router_register.py: Tests for scripts/router_regis
- tests/test_tool_gateway.py: Tests for the open-source tool
- tests/test_weak_model_hardening.py: Tests for the 9 weak-model-har
- tool_gateway.py: Open-source tool gateway — the
- verifier_engine.py: Hybrid verifier engine: Progra
- workflow_versions.py: Workflow version control — sna

## Dependency graph (internal edges)
- scripts/build_gates_pipeline.py -> scripts.n8n_stability_verifier.verify_stability, scripts.n8n_stability_verifier.N8N_API_KEY, scripts.n8n_stability_verifier.N8N_BASE_URL, scripts.n8n_stability_verifier.REQUIRED_CONSECUTIVE_PASSES …
- tests/test_build_gates_pipeline.py -> scripts.build_gates_pipeline.run_pipeline, scripts.build_gates_pipeline.MathLogicGate, scripts.build_gates_pipeline.DeepReasoningGate, scripts.build_gates_pipeline.COUNTING_KEYWORDS …
- tests/test_gate_complaints.py -> scripts.gate_complaints.ComplaintsRegistry, scripts.gate_complaints.extract_keywords, scripts.gate_complaints.default_find_skills, scripts.gate_complaints._skill_corpus …
- tests/test_n8n_precision_gate.py -> scripts.build_gates_pipeline.run_pipeline, scripts.build_gates_pipeline.N8nPrecisionGate, scripts.build_gates_pipeline.DryRunGate, scripts.build_gates_pipeline._is_trigger_node …
- tests/test_n8n_stability_verifier.py -> scripts.n8n_stability_verifier, scripts.build_gates_pipeline.StabilityGate, scripts.build_gates_pipeline.run_pipeline
- tests/test_router_register.py -> scripts.router_register.read_frontmatter, scripts.router_register.classify, scripts.router_register.ensure_routing_row, scripts.router_register.ensure_registry_entry …

## Test map
- tests/test_ai_automation_security.py (covers: security_gate, security_gate)
- tests/test_auto_self_evolver.py (covers: json, auto_self_evolver, auto_self_evolver)
- tests/test_build_gates_pipeline.py (covers: json, sys, tempfile)
- tests/test_cognitive_modules.py (covers: json, dual_process_planner, cybersec_sandbox_engine)
- tests/test_e2e_live_n8n.py (covers: json, os, urllib)
- tests/test_gate_complaints.py (covers: json, sys, tempfile)
- tests/test_hitl_gate.py (covers: json, os, sys)
- tests/test_master_orchestrator.py (covers: json, os, sys)
- tests/test_model_coercion_protocols.py (covers: json, ambiguity_resolver, ambiguity_resolver)
- tests/test_n8n_precision_gate.py (covers: json, sys, pathlib)
- tests/test_n8n_stability_verifier.py (covers: sys, pathlib, scripts)
- tests/test_orchestrator_hardening_wiring.py (covers: master_system_orchestrator)
- tests/test_production_hardening.py (covers: json, tempfile, time)
- tests/test_promoted_rules_security.py (covers: hashlib, json, os)
- tests/test_remote_adaptation.py (covers: json, os, sys)
- tests/test_router_register.py (covers: sys, pathlib, scripts)
- tests/test_security_governance.py (covers: json, tempfile, os)
- tests/test_tool_gateway.py (covers: json, tool_gateway, tool_gateway)
- tests/test_verifier_engine.py (covers: json, os, sys)
- tests/test_weak_model_hardening.py (covers: json, tempfile, pathlib)

## Unknowns (honest limits)
- Raw bodies NOT read; names parsed mechanically. Rehydrate
  exact regions via the name(line) pointers above.
