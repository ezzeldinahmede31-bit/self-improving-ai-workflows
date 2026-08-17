# Skill Library — fast lookup index

One-line reference for every skill under `.opencode/skills/`.
The tool-invocation skill scans this file to find the right skill fast:
pick a family, read the one-liners, then open `memory/skills-docs/<name>.md`
for the full doc of the chosen skill. Grouping matches the router
registry buckets (`compensatory-router/SKILL.md`), so new skills that were
registered in the router appear under the same family here automatically.

## Automation (per-tool) (41)

- **ai-skill-authoring-standards** — The GLOBAL standards gate for creating, reviewing, designing, and building ANY AI agent skill in this workspace.
- **airtable-automation** — Airtable database automation - views, automations, integrations, and workflow triggers
- **ansible-automation** — Infrastructure automation and configuration management using Ansible playbooks, roles, and inventory.
- **asana-automation** — Automate Asana project management workflows, task tracking, team collaboration, and reporting
- **calendar-automation** — Google Calendar and Outlook automation - scheduling optimization, meeting workflows, time blocking, and Slack/Sheets integration
- **clickup-automation** — Automate ClickUp workspace management, task workflows, time tracking, and team productivity
- **crm-automation** — CRM workflow automation for HubSpot, Salesforce, Pipedrive - lead management, deal tracking, and multi-CRM synchronization
- **devops-automation** — DevOps and IT Ops automation - CI/CD, monitoring, incident management, and infrastructure workflows
- **docusign-automation** — Automate document signing workflows, envelope management, and e-signature processes
- **email-marketing** — Email marketing automation - campaign creation, sequence building, A/B testing, deliverability optimization, and analytics
- **excel-automation** — Automate Excel spreadsheets: formulas, data cleanup, chart creation, VBA macros, and reporting workflows.
- **home-assistant-automation** — Automate smart home devices and create intelligent home automation workflows with Home Assistant
- **hr-automation** — HR workflow automation - recruiting, onboarding, employee management, and offboarding processes
- **intercom-automation** — Automate Intercom customer messaging, support workflows, user engagement, and product tours
- **invoice-automation** — Automate invoice generation, sending, tracking, and payment reconciliation across accounting platforms
- **jira-automation** — Automate Jira project management workflows, sprint planning, issue tracking, and reporting
- **linear-automation** — Automate Linear issue tracking, cycle planning, roadmap management, and engineering workflows
- **linkedin-automation** — Automate LinkedIn marketing, lead generation, content publishing, and professional networking
- **mailchimp-automation** — Automate Mailchimp email marketing campaigns, audience management, automations, and analytics
- **microsoft-teams-automation** — Automate Microsoft Teams messaging, meetings, channels, and workflow integrations
- **monday.com-automation** — Automate Monday.com workflows, board management, team collaboration, and cross-board integrations
- **notion-automation** — Notion database automation - sync, templates, workflows, and cross-platform integrations
- **obsidian-automation** — Automate Obsidian knowledge management, note linking, and personal knowledge base workflows
- **pipedrive-automation** — Automate Pipedrive CRM workflows including deal management, pipeline tracking, and sales reporting
- **podcast-automation** — Automate podcast production workflows including recording, editing, publishing, and distribution
- **quickbooks-automation** — Automate QuickBooks accounting workflows including invoicing, expenses, reporting, and bank reconciliation
- **security-monitoring** — Automate security monitoring, threat detection, incident response, and compliance workflows
- **sheets-automation** — Google Sheets automation workflows - data sync, task management, reporting dashboards, and multi-platform integrations
- **shopify-automation** — Shopify e-commerce automation - inventory management, order processing, customer workflows, and analytics
- **skillopt-sleep** — Use when the user wants their Claude agent to self-improve from past usage, asks about a nightly/offline 'sleep' or 'dream' cycle, memory/skill consolidation, o…
- **spotify-automation** — Automate Spotify music playback, playlist management, and audio analysis workflows
- **transcription-automation** — Automate audio/video transcription, meeting notes, subtitle generation, and content processing
- **trello-automation** — Automate Trello board management, card workflows, power-ups, and team collaboration
- **twilio-sms-automation** — Automate SMS communications, two-way messaging, notifications, and voice workflows with Twilio
- **twitter-x-automation** — Automate Twitter/X social media workflows including posting, engagement, analytics, and audience growth
- **weather-automation** — Automate weather-based workflows, forecasts, alerts, and location-aware notifications
- **webhook-automation** — Build and manage webhook-based integrations for real-time event processing and API connections
- **whatsapp-automation** — WhatsApp Business automation - customer support, notifications, chatbots, and broadcast messaging
- **woocommerce-automation** — Automate WooCommerce e-commerce operations including orders, inventory, customers, and marketing
- **youtube-automation** — Automate YouTube content workflows including video management, analytics, scheduling, and channel optimization
- **zendesk-automation** — Automate customer support workflows with Zendesk ticket management, routing, and analytics

## n8n (15)

- **n8n-agents-official** — Use when building or editing any AI feature in n8n: AI Agents, Text Classifier, Information Extractor, Sentiment Analysis, Summarization Chain, Basic LLM Chain,…
- **n8n-autodoc-mermaid** — Automatically generate a README.md with a Mermaid flowchart, inputs/outputs table, and step-by-step client runbook for every n8n workflow delivered.
- **n8n-code-nodes-official** — Use when the user reaches for a Code node, mentions writing JavaScript or Python in n8n, or any custom logic comes up in workflow design.
- **n8n-credential-security-guard** — Prevent ANY API key, secret, token, or password from being written into n8n node parameters, expressions, or Code-node source.
- **n8n-debugging-official** — Use when an n8n workflow isn't working, errors appear, results don't match what was expected, or the user says "this isn't working." Triggers on errors, unexpec…
- **n8n-e2e-test-runner** — Run a real end-to-end integration test after deploying an n8n workflow: hit the live webhook/trigger with a sample payload and verify it returns a 200 OK (plus…
- **n8n-error-boundary-architect** — Automatically add error handling to every n8n workflow: Error Trigger nodes, Continue On Fail with error branches, and exponential-backoff retry strategies.
- **n8n-git-sync** — Sync every n8n workflow JSON to a local/cloud Git repository automatically after create/update success.
- **n8n-mcp-workflow-builder** — Forces the LLM to build n8n workflows locally using the n8n MCP Server schema cache, bypassing external API documentation fetching and eliminating hardcoded key…
- **n8n-pinned-data-mocking** — Generate realistic pinned data inside every n8n node so the workflow can be tested instantly in the n8n UI without firing the real trigger.
- **n8n-schema-guardrail** — Verify generated n8n workflow JSON against the actual installed node schemas before deploy.
- **n8n-subworkflow-modularizer** — Split complex n8n automations into small, independent sub-workflows wired together with Execute Workflow nodes.
- **n8n-syntax-v2-enforcer** — Enforce modern n8n 2.x expression and Code-node syntax deterministically.
- **n8n-workflow** — Automate document workflows with n8n - 7800+ workflow templates
- **n8n-workflow-lifecycle-official** — Use when starting, designing, organizing, finishing, or shipping an n8n workflow.

## Zapier (9)

- **workflows-create** — Create a durable Zapier workflow from natural language using @zapier/zapier-durable and the Zapier SDK CLI.
- **workflows-doctor** — Diagnose Zapier Workflows skill and SDK CLI compatibility.
- **workflows-history** — Show run history for a specific durable workflow using the Zapier SDK experimental Code Workflows commands.
- **workflows-install** — Install the Zapier SDK CLI for Zapier Workflows Early Access and bootstrap the workflows companion skills.
- **workflows-list** — List durable workflows in the authenticated Zapier account using the Zapier SDK experimental Code Workflows commands.
- **workflows-modify** — Modify and republish an existing durable workflow using the Zapier SDK experimental Code Workflows commands.
- **zapier-make-patterns** — No-code automation democratizes workflow building.
- **zapier-sdk** — Zapier SDK for TypeScript.
- **zapier-system-cloner** — Replicates any Zapier (Zap) system — especially premium/expensive ones — with identical outputs and quality on n8n or code, using different (free/local) tools w…

## Marketing/SEO/Growth (16)

- **apify-audience-analysis** — Understand audience demographics, preferences, behavior patterns, and engagement quality across Facebook, Instagram, YouTube, and TikTok.
- **audience-psychology-analyst** — Build a psychological profile of any target audience and translate it into marketing AND video-editing decisions.
- **co-marketing** — When the user wants to find co-marketing partners, plan joint campaigns, or brainstorm partnership opportunities.
- **community-marketing** — Build and leverage online communities to drive product growth and brand loyalty.
- **content-research-writer** — Research topics and write content like blog posts, articles, and copy
- **conversion-psychology** — Psychology of conversion for sponsored content.
- **customer-research** — When the user wants to conduct, analyze, or synthesize customer research.
- **influence-psychology** — Apply the seven principles of ethical persuasion (reciprocity, commitment, social proof, authority, liking, scarcity, unity) to product design, copy, and sales.
- **influencer-marketing** — When the user wants to run influencer, creator, or ambassador partnerships to promote their product — finding and vetting partners, structuring deals, briefing…
- **lead-research-assistant** — Research company and contact information for sales outreach
- **marketing-council** — When the user wants multiple expert perspectives on a marketing question — a simulated board of advisors staffed by legendary marketers (Seth Godin, David Ogilv…
- **marketing-loops** — When the user wants to set up a recurring, self-running marketing workflow — a repeatable loop an AI agent runs on a cadence (weekly, daily, on a trigger) rathe…
- **marketing-plan** — When the user needs a comprehensive marketing plan for a client, a company they advise, or their own product.
- **marketing-psychology** — When the user wants to apply psychological principles, mental models, or behavioral science to marketing.
- **persuasion-principles** — Master Robert Cialdini's 6 (+1) Principles of Persuasion from "Influence: The Psychology of Persuasion" (1984).
- **viral-hooks** — Expert in creating opening lines, thumbnails, and hooks that stop the scroll.

## Social media (7)

- **social** — When the user wants help creating, scheduling, or optimizing social media content for LinkedIn, Twitter/X, Instagram, TikTok, Facebook, or other platforms, or w…
- **social-media** — Drafts engaging social media posts, writes hooks, suggests hashtags, creates thread structures, and generates companion images.
- **social-media-analyzer** — Social media campaign analysis and performance tracking.
- **social-media-generator** — This skill should be used when the user requests social media content creation for Twitter, Instagram, LinkedIn, or Facebook.
- **social-media-image-sizes** — Check and resize images for social media platforms.
- **social-publisher** — Multi-platform social media publishing automation - schedule, post, and track content across TikTok, Instagram, YouTube, LinkedIn, and more
- **tiktok-marketing** — TikTok content strategy, video creation workflows, posting optimization, and analytics.

## Video/Media (7)

- **audio-whisper-transcriber** — Transcribes extracted audio files (mp3/wav) into text using local OpenAI Whisper / faster-whisper — no per-use API cost, no network upload, runs fully on-device…
- **media-downloader-extractor** — Downloads and extracts video/audio streams from social-media links (Facebook Reels, YouTube, TikTok, Instagram) using yt-dlp — bypassing browser scrapers, Cloud…
- **video** — When the user wants to create, generate, or produce video content using AI tools or programmatic frameworks.
- **video-edit** — Edit existing video on RunComfy — this skill is a smart router that matches the user's intent to the right edit model in the RunComfy catalog.
- **video-editing** — AI-assisted video editing workflows for cutting, structuring, and augmenting real footage.
- **video-inpainting** — Region edits across video frames on RunComfy via the `runcomfy` CLI — remove an object that appears across many frames, clean up wires or watermarks, replace a…
- **video-processing-editing** — FFmpeg automation for cutting, trimming, concatenating videos.

## Research (11)

- **academic-search** — Search and analyze academic literature.
- **company-research** — Conduct comprehensive company research and due diligence.
- **data-analysis** — Generate statistical analysis code with 4-round review.
- **deep-research** — Conduct comprehensive research on any topic.
- **evidence-over-memory** — Kill hallucination by making verification a reflex: any factual claim, API detail, library version, file path, or numeric fact must come from a tool result, not…
- **firecrawl-deep-research** — Produce an intensive, cited analytical report: executive summary, multi-angle findings, contrarian views, open questions, and full sources.
- **github-research** — Explore and analyze GitHub repositories related to a research topic.
- **literature-search** — Search academic literature using Semantic Scholar, arXiv, and OpenAlex APIs.
- **parallel-deep-research** — ONLY use when user explicitly says 'deep research', 'exhaustive', 'comprehensive report', or 'thorough investigation'.
- **parallel-web-search** — DEFAULT for all research and web queries.
- **web-search** — Formulate effective web search queries, analyze search results, and synthesize findings.

## Reasoning/Math/Logic (13)

- **algorithmic-math-reasoner** — Raises correctness on hard algorithmic and mathematical problems where a fast model tends to jump to plausible-but-wrong answers: forces formal restatement, inv…
- **critical-thinking-logical-reasoning** — Critically analyse the reasoning in written content (articles, blogs, transcripts, reports), not code.
- **execution-guided-tot-validator** — Validates Tree-of-Thought (ToT) reasoning branches using real execution feedback in a local Docker sandbox rather than relying on LLM self-judgment.
- **formal-math-logic-verification-engine** — Deterministic, mechanical verification for math and logic answers using real solver tooling installed in this workspace's venv — math-verify (HuggingFace: parse…
- **frontier-deep-reasoner** — Compensate for shallow/degraded multi-step reasoning by forcing an explicit decomposition ladder (Problem -> Constraints -> Steps -> Verify -> Output).
- **math-olympiad** — Solve competition math problems (IMO, Putnam, USAMO, AIME) with adversarial verification that catches the errors self-verification misses.
- **math-reasoning** — Formal mathematical reasoning for research papers — derive equations, write proofs, formalize problem settings, select statistical tests, and generate LaTeX mat…
- **off-by-one-boundary-guard** — Destroys the off-by-one class of errors in counting problems (open vs closed intervals, fence-post counts, period-crossing counts, inclusive/exclusive ranges, e…
- **self-benchmark-runner** — Runs the agent against a public benchmark that frontier models have also been scored on (AIME, MATH-500, GSM8K, GPQA, HLE), so the user gets an honest head-to-h…
- **symbolic-equation** — Discover scientific equations from data using LLM-guided evolutionary search (LLM-SR).
- **test-time-compute-scaling** — Brings frontier-level accuracy to a fast/cheap model on HARD problems only, using test-time scaling: generate multiple independent solution paths in parallel, t…
- **thought-based-reasoning** — Use when facing complex reasoning tasks - multi-step math, logic puzzles, decisions with tradeoffs, problems where direct answers fail, or when you need to show…
- **unit-test-boundary-conditions** — Provides edge case, corner case, boundary condition, and limit testing patterns for Java unit tests.

## Thinking frames (28)

- **thinking-bounded-rationality** — Use when search or investigation could run forever.
- **thinking-circle-of-competence** — Use when a specific claim may lack grounding.
- **thinking-cynefin** — When the right response mode is unclear, classify the cause-effect domain first; decompose disorder.
- **thinking-effectuation** — Under genuine uncertainty with no reliable forecast, inventory means, cap downside at affordable loss, act for commitments, and let goals emerge from controllab…
- **thinking-first-principles** — When a constraint is treated as fixed, separate physics from convention, keep only independently supported primitives, and rebuild the simplest solution that sa…
- **thinking-five-whys-plus** — When a fault is localized and the proximate cause is known but the systemic root is not, chain evidence-linked whys with a counterfactual stop and a countermeas…
- **thinking-jobs-to-be-done** — Deciding what to build or why adoption fails.
- **thinking-kepner-tregoe** — Use when a selective defect needs IS/IS-NOT difference analysis or a consequential option choice needs must/want weighting and adverse-consequence comparison.
- **thinking-lindy-effect** — Use when longevity of a non-perishable option matters.
- **thinking-map-territory** — When a claim, doc, test, metric, or assumption conflicts with observed behavior, stop theorizing from the map and verify the live code or data; let territory ov…
- **thinking-margin-of-safety** — When provisioning, setting a limit, or committing an estimate under uncertainty, size a buffer to residual error and the cost of breach—not to the optimistic ed…
- **thinking-model-combination** — When one mental model leaves a material blind spot on a multi-domain or high-stakes problem, sequence complementary models with named roles and a conflict rule.
- **thinking-model-router** — When unsure which thinking skill fits, map domain and problem type, then return NONE or one primary skill by default (at most three complementary).
- **thinking-ooda** — Use under time pressure when the situation is still changing and you must act before certainty — cycle Observe→Orient→Decide→Act on ~70% confidence, then re-obs…
- **thinking-opportunity-cost** — Before committing scarce time, people, or money, name the best forgone use of those resources and the value delta of the chosen path versus that alternative.
- **thinking-pre-mortem** — Before committing to a plan or launch, assume it already failed and reason backward through concrete causes — convert failure paths into mitigations, gates, and…
- **thinking-probabilistic** — Use when forecasting, estimating, or sizing risk — anchor on base rates, give ranges, update prior→likelihood→posterior on evidence, and factor unmeasured quant…
- **thinking-red-team** — For authorized security review of code, auth, or APIs you control, model the attacker, map the attack surface, and report only findings with a reproducible expl…
- **thinking-reversibility** — Before heavy deliberation, classify the decision as cheap or costly to undo; decide two-way doors fast and stage one-way doors to preserve options.
- **thinking-scientific-method** — When a symptom has several plausible causes, rank falsifiable hypotheses and run the cheapest discriminating observation first; prefer least-assumptive survivor…
- **thinking-second-order** — When a change has effects past the immediate fix—incentives, scale, feedback—trace consequence chains with timing and probability before committing.
- **thinking-socratic** — When a request is vague, assumption-laden, or "obvious," ask the few load-bearing questions that expose hidden requirements before building or committing.
- **thinking-steel-manning** — Before rejecting a proposal or reflexively agreeing, build the strongest faithful opposing case, state agreement conditions, then update or reaffirm.
- **thinking-systems** — When behavior is emergent across components—fixes elsewhere break, loops/delays dominate—map boundary, stocks/flows, feedback, archetypes, then rank leverage.
- **thinking-theory-of-constraints** — When throughput or latency is pipeline-limited, identify the single binding constraint and exploit, subordinate, elevate, then recheck—ignore non-constraints.
- **thinking-thought-experiment** — When a real test is too rare, large, or irreversible, run a controlled counterfactual: isolate one variable, fix conditions, trace the mechanistic chain, and bo…
- **thinking-triz** — When two design requirements seem mutually exclusive, name the contradiction, separate conflicting states, then invent a concrete no-compromise resolution.
- **thinking-via-negativa** — Use when the reflex is to add a feature, layer, or process.

## Context/Memory/System (34)

- **advanced-evaluation** — This skill should be used for advanced LLM evaluation: LLM-as-judge systems, direct scoring, pairwise comparison, rubric calibration, evaluator bias mitigation,…
- **ambiguity-resolver** — Forced-explicit ambiguity gate for weak/free models.
- **automation-known-issues-compass** — The known-issues catalog + design-time checklist for n8n and Zapier: every common failure mode, its symptom, root cause and fix, encoded so that ANY automation/…
- **bdi-mental-states** — This skill should be used when modeling agent mental states with BDI concepts: beliefs, desires, intentions, RDF-to-belief transformations, rational agency trac…
- **chain-integrity-checker** — Cumulative per-step consistency verification for multi-step plans/DAGs produced by weak models.
- **cognitive-task-triager** — Analyzes task complexity and assigns execution to the optimal LLM tier (Routine, Code, Long-Context, Critical Reasoning) before any model call.
- **confidence-calibrator** — Externally-measured confidence calibration for weak/free models.
- **context-budget-governor** — Protect a small context window so it behaves like a big one.
- **context-compression** — This skill should be used when long-running agent sessions need context compression, structured summarization, compaction, token-per-task optimization, or durab…
- **context-degradation** — This skill should be used for diagnosing and mitigating context degradation: lost-in-middle failures, context poisoning, context clash, context confusion, atten…
- **context-engineering** — Optimizes agent context setup.
- **context-enrichment** — Explicit-rule lexicon for implicit intents (weak-model hardening).
- **context-fundamentals** — This skill should be used to explain or reason about the foundational concepts of context engineering: what context is, the anatomy of a context window, how att…
- **context-optimization** — This skill should be used for improving context efficiency: context budgeting, observation masking, prefix or KV-cache strategy, partitioning, token-cost reduct…
- **durable-experience-consolidator** — Turns a finished working session into durable cross-session knowledge so nothing important is forgotten after the chat ends: extracts principles, verified facts…
- **evaluation** — This skill should be used when building agent evaluation systems: deterministic checks, regression suites, multi-dimensional rubrics, quality gates, production…
- **filesystem-context** — This skill should be used when agent work needs file-backed context: durable scratchpads, tool-output offloading, just-in-time discovery, cross-agent handoff fi…
- **harness-engineering** — This skill should be used when designing autonomous agent harnesses: research loops, evaluation scaffolds, locked and editable surfaces, durable logs, novelty g…
- **hosted-agents** — This skill should be used when designing hosted or background agent infrastructure: sandboxed execution, remote coding environments, warm pools, session persist…
- **latent-briefing** — This skill should be used when the user asks to "share memory between agents", "KV cache compaction for multi-agent", "orchestrator worker context", "latent bri…
- **long-context-sharding-engine** — Prevents context degradation by sharding large documents into JIT task-scoped chunks and dynamically routing massive contexts to long-context frontier models.
- **long-horizon-executor** — Survive long, many-step tasks without losing the thread or compounding errors: plan first, checkpoint state to disk, verify each step, and recover explicitly in…
- **long-horizon-prompting** — This skill should be used when writing, enhancing, or evaluating the launch prompt for a long-running autonomous agent or a parallel multi-agent orchestration a…
- **long-term-memory-retriever** — Provides persistent memory for the agent.
- **mcp-context-trimmer** — Sort, summarize, and trim outputs returned from MCP tools / API responses before passing them to the next workflow node, to avoid context-window exhaustion and…
- **memory-systems** — This skill should be used for persistent semantic memory in agent systems: cross-session knowledge retention, entity tracking, temporal validity, graph or vecto…
- **million-token-reader** — Reads corpora that are 10-100x our context window (docs, books, transcripts, big repos, logs, full datasets — 50K tokens and up, up to a million) with ZERO forg…
- **multi-agent-patterns** — This skill should be used when designing multi-agent systems that need context isolation, supervisor or swarm coordination, explicit handoffs, parallel executio…
- **progressive-context-compressor** — Survives long sessions without losing fidelity: instead of a single late collapse, maintains a rolling structured summary as the conversation grows, decides WHA…
- **project-development** — This skill should be used for project-level decisions about LLM-powered systems: whether an LLM is the right primitive for the task at hand, the shape of a mult…
- **rate-limit-and-cost-guard** — Calculate expected API cost and call volume for every n8n workflow, then add rate-control (Wait/Loop limits) so API keys are not banned and budgets are not blow…
- **self-improvement-loops** — This skill should be used when the harness, scaffold, workflow, or optimizer itself is the optimization target: recursive self-improvement (RSI) loops, meta-har…
- **state-machine-persistence** — Design n8n automations as recoverable state machines: persist multi-turn or long-running state (conversation context, job progress, dedupe keys) to Supabase, Re…
- **tool-design** — This skill should be used for the tool-interface layer of an agent system specifically: writing tool descriptions agents can route on, designing tool schemas an…

## Agents/Architecture (5)

- **agent-arch-system-design** — Expert system architecture design: patterns, scalability planning, ADRs, C4 diagrams, technology trade-offs, non-functional requirements.
- **agent-reach** — Read and search external sources through the channels installed on this machine.
- **autonomous-git-coworker** — Manages Git workflows natively: checks status, creates feature branches, crafts atomic commits with descriptive logs, and prepares PRs.
- **autonomous-model-self-evolver** — Autonomous meta-skill that MEASURES the current model against a live leader with real model calls on deterministic probes, pulls real weaknesses from the audit…
- **site-architecture** — When the user wants to plan, map, or restructure their website's page hierarchy, navigation, URL structure, or internal linking.

## Security (7)

- **better-auth-security-best-practices** — Configure rate limiting, manage auth secrets, set up CSRF protection, define trusted origins, secure sessions and cookies, encrypt OAuth tokens, track IP addres…
- **enterprise-quality-audit-loop** — Deterministic Quality & ISO/IEC 25010 compliance gate paired with an automated feedback and self-correction loop.
- **enterprise-security-gate** — Autonomous Zero-Trust security enforcer complying with OWASP Top 10 for LLMs, NIST AI RMF, and SOC 2 Type II controls.
- **firebase-security-rules-auditor** — Audits Firebase (Firestore, Cloud Storage) security rules for vulnerabilities, privilege escalation, role bypasses, create vs update inconsistencies, resource e…
- **frontier-red-team-auditor** — Enforces mandatory Frontier LLM reasoning for security audits while backing it up with deterministic input validation and isolated Docker sandboxing.
- **security-and-hardening** — Hardens code against vulnerabilities.
- **security-review** — Security code review for vulnerabilities.

## Coding/SWE (17)

- **algorithm-design** — Design algorithms with LaTeX pseudocode and UML diagrams.
- **ast-codebase-graph-navigator** — Navigates multi-file codebases using Abstract Syntax Trees (AST), import graphs, and caller-callee traces instead of brute-force full-file loading.
- **atomic-decomposition** — Decompose research ideas into atomic, self-contained concepts with bidirectional math-code mapping.
- **code-debugging** — Debug experiment code with structured error analysis.
- **code-execution-guided-swemaster** — Closes the last measured gap vs frontier coding models: instead of plan-once-patch-once, we drive large code fixes with EXECUTION evidence and MEASURED results.
- **code-linter-python-js** — Deterministically lint and structurally check any JavaScript or Python written for n8n Code nodes before delivery.
- **codebase-mind-persistence** — Persistent on-disk codebase mind map (approximate 1M-token context emulation) built ONCE per codebase — symbol index, module-level summaries, dependency graph,…
- **experiment-code** — Write ML experiment code with iterative improvement.
- **paper-to-code** — Convert an ML research paper into a complete, runnable code repository.
- **root-cause-post-mortem-analyzer** — Performs rigorous root-cause analysis (RCA) on stack traces and runtime errors to prevent superficial band-aid fixes.
- **single-pass-frontier-emulator** — Emulates a frontier model's single-pass open-ended depth on a flash model: instead of greedily splitting a big open-ended task into tiny delegated pieces (which…
- **subagent-task-delegator** — Decomposes large multi-part jobs into isolated sub-tasks executed by sub-agents, preserving the main conversation context budget.
- **surgical-diff-patch-editor** — Enforces exact line-level search-and-replace block edits instead of rewriting whole files, preventing accidental code truncation.
- **swe-workflow** — REQUIRED for every code-related task.
- **tdd-sandbox-proof-engine** — Enforces Test-Driven Development (TDD) in a clean sandbox: code is only considered valid if companion unit tests pass 100% and the execution log is attached.
- **terminal-bash-executor-governor** — Executes CLI commands, inspects exit codes, manages tailing log output, and enforces safety gates for destructive terminal operations.
- **zero-trust-modular-decomposer** — Enforces strict modular architecture, breaking implementations into single-responsibility files (7-10 modules) with zero-trust isolation boundaries.

## Browser/Device (7)

- **claude-code-style-web-login** — Brows the web and logs into websites with the USER'S OWN accounts on THEIR device, replicating exactly how Claude Code does it — a visible local browser (Playwr…
- **desktop-gui-controller** — Controls the user's real X11 desktop session (DISPLAY=:0) like a human coworker: list/focus/resize windows with wmctrl, send keyboard and mouse events, capture…
- **hitl-captcha-auth-handler** — Detects CAPTCHAs, Cloudflare Turnstile, and 2FA SMS/Email verification prompts during browser automation, triggers a Human-in-the-Loop (HITL) pause, then resume…
- **persistent-browser-automation** — Drives a real Chromium browser (playwright or browser-use) so the agent can click, type, scroll, upload files, and extract pages exactly like a human — while re…
- **site-login-session-registry** — Logs into websites ONCE, persists the authenticated browser session as a named profile in a registry, and reuses it on later runs so the user is not asked for c…
- **stealth-browser-evasion** — Runs browser automation in stealth mode so WAF anti-bot systems (Cloudflare, Akamai, DataDome) do not flag the session: hardened Chromium launch flags, fingerpr…
- **visual-context-verifier** — Closes the 'blind spot' gap for a model that cannot see its own work: before anything visual is claimed, capture real pixels/HTML/DOM as evidence (screenshots r…

## Creative/Reasoning (15)

- **analogy** — Forced Analogy / Structural Transplant — map the problem onto a structurally similar system from a distant domain (immune system, air-traffic control, restauran…
- **concept-fan** — Edward de Bono's Concept Fan — climb from the current solution to the concept it serves by asking "what is this a way of doing?", then fan out alternative conce…
- **creative-problem-solver** — Generate a compact five-tier strategy portfolio when the next task is choosing among materially different paths.
- **creative-system-architect** — Forces the model to generate 3 distinct architectural options (Tree-of-Thought) and apply cross-domain principles to outperform conventional linear solutions.
- **emergent-reasoning-edge** — Beats a frontier model's parametric instinct at open-ended creativity and emergent reasoning by adding two things it cannot have: (1) LIVE world evidence — web/…
- **first-principles** — Break down complex problems to their fundamental truths, then reason up from there.
- **inversion** — Assumption Inversion — list the assumptions behind the current approach and flip each one, then ask where the flipped version could actually be true.
- **lateral** — Lateral thinking toolkit router — when you're stuck, going in circles, need fresh ideas, or standard brainstorming keeps producing predictable results, this dia…
- **llm-council** — Run any question, idea, or decision through a council of 5 AI advisors who independently analyze it, peer-review each other anonymously, and synthesize a final…
- **multi-agent-consensus-engine** — Simulates an expert panel (Software Architect, Security Engineer, QA Expert) to review, debate, and reach consensus on complex tasks before delivery.
- **provocation** — Edward de Bono's Provocation (Po) technique — state something deliberately wrong or absurd about the problem, then extract useful "movement" from it instead of…
- **random-stimulus** — Edward de Bono's Random Stimulus technique — force-fit a random unrelated object, place, or phenomenon onto a creative target to break familiar association patt…
- **scamper** — SCAMPER (Bob Eberle) — run one existing idea, product, or process through seven systematic transformations - Substitute, Combine, Adapt, Modify/Magnify, Put to…
- **six-hats** — Parallel thinking with six enforced perspectives, based on Edward de Bono's Six Thinking Hats® method - examine one decision through sequential passes for facts…
- **worst-idea** — Worst Possible Idea (reverse brainstorming) — deliberately design the most terrible solutions to the problem, name the mechanism that makes each one bad, then i…

## Delivery/Gates (19)

- **adversarial-self-falsifier** — Actively attacks and attempts to break generated code, math, or logic before finalizing the response.
- **best-practice-first-designer** — MANDATORY research-first gate before designing or building ANY n8n workflow or AI agent.
- **build-gates-pipeline** — MANDATORY pre-build gate pipeline for EVERY n8n workflow, AI agent, or automation artifact this agent produces.
- **clarify-before-execute** — The user's mandatory discovery loop: when they give a request, DO NOT start building.
- **compensatory-router** — Meta-skill that routes any incoming task to the right compensatory skill pack (deep reasoning / context budget / verification / long-horizon execution) so a fla…
- **dont-reinvent-the-wheel** — Research existing products, open-source projects, commercial script marketplaces such as CodeCanyon/Envato Market, SaaS tools, SDK features, APIs, webhooks, emb…
- **elite-verifier-delegation** — When a fast model must reach frontier-level certainty, delegate VERIFICATION (not generation) to a stronger model: generate cheap here, then have the strongest…
- **fable-5-playbook** — Applies the operational techniques from Anthropic's leaked Claude Fable 5 system prompt (120,000 chars, 1,580+ lines) to cheaper/flash-tier models so they behav…
- **find-skills** — Helps discover and install agent skills.
- **incremental-generation** — Build n8n workflows incrementally — one node (or one small chain) at a time, validating EACH node against the live schema cache and the installed node registry…
- **jit-pragmatic-architect** — World-class AI Automation System Architect.
- **litellm-tier-router** — Dynamic SLA-aware model routing and multi-provider failover engine.
- **n8n-delivery-verification-gate** — MANDATORY gate before delivering ANY n8n workflow to the user.
- **nvidia-nim-integrator** — Connects OpenCode to NVIDIA NIM API (Llama 3.3, Nemotron, DeepSeek) using the local NVIDIA_API_KEY environment variable.
- **obsidian-second-brain-vault** — Routes downloaded media transcripts and extracted knowledge notes into a local Obsidian vault under the three-section structure (01_Raw_Inbox / 02_Structured_Kn…
- **omni-request-orchestrator** — MANDATORY skill-synthesis orchestrator for EVERY user request, no exceptions.
- **proactive-spec-expander** — Automatically expands simple user prompts into enterprise-grade PRDs with implicit security, lockdown modes, rate limits, and edge-case requirements BEFORE writ…
- **reflection-and-audit-loop** — Impose a mandatory 4-stage structured workflow before delivering any n8n workflow JSON or Code-node script: plan the path, draft, structural self-critique, then…
- **tradeoff-and-postmortem-documenter** — Auto-generates production-ready documentation, architecture rationale, design trade-offs, and an explicit KNOWN_ISSUES.md for every implementation.

## Superpowers pack — obra (14)

- **brainstorming** — You MUST use this before any creative work - creating features, building components, adding functionality, or modifying behavior.
- **dispatching-parallel-agents** — Use when facing 2+ independent tasks that can be worked on without shared state or sequential dependencies
- **executing-plans** — Use when you have a written implementation plan to execute in a separate session with review checkpoints
- **finishing-a-development-branch** — Use when implementation is complete, all tests pass, and you need to decide how to integrate the work
- **receiving-code-review** — Use when receiving code review feedback, before implementing suggestions, especially if feedback seems unclear or technically questionable - requires technical…
- **requesting-code-review** — Use when completing tasks, implementing major features, or before merging to verify work meets requirements
- **subagent-driven-development** — Use when executing implementation plans with independent tasks in the current session
- **systematic-debugging** — Use when encountering any bug, test failure, or unexpected behavior, before proposing fixes
- **test-driven-development** — Use when implementing any feature or bugfix, before writing implementation code
- **using-git-worktrees** — Use when starting feature work that needs isolation from current workspace or before executing implementation plans - ensures an isolated workspace exists via n…
- **using-superpowers** — Use when starting any conversation - establishes how to find and use skills, requiring skill invocation before ANY response including clarifying questions
- **verification-before-completion** — Use when about to claim work is complete, fixed, or passing, before committing or creating PRs - requires running verification commands and confirming output be…
- **writing-plans** — Use when you have a spec or requirements for a multi-step task, before touching code
- **writing-skills** — Use when creating new skills, editing existing skills, or verifying skills work before deployment

## Video-pack extras (3)

- **impeccable** — Use when the user wants to design, redesign, shape, critique, audit, polish, clarify, distill, harden, optimize, adapt, animate, colorize, extract, or otherwise…
- **remembering-conversations** — You MUST invoke this skill before saying "I don't know," guessing, or treating any topic as new, no matter how trivial the question seems.
- **wizard** — Generate an interactive bash wizard that walks a human through steps only they can perform.

---
*Auto-generated by `scripts/skills_docs_generator.py` on 2026-08-17 12:00 — 268 skills, 18 families*
