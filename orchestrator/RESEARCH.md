# Pre-Build Research — permanent stage (not a side feature)

Flow position (binding):
Requirement Understanding -> RESEARCH -> Task Decomposition -> DAG -> Agents.

## How it runs
1. `submit_project` carries `research_attrs` (complexity, importance,
   security_sensitivity, dependencies, failure_cost).
2. `decide_depth(attrs)` -> light | deep | deep-security.
3. `plan_research()` emits one research task per topic (normal task
   contracts, kind=opencode, role=Research Agent, bounded like all tasks).
4. Workers write `findings/<topic>.json`; validation (`validate_finding`)
   rejects sourceless records and closed-source code.
5. Deterministic synthesis in code: `repeated_complaints` (>=2 distinct
   non-opinion sources), `license_verdict`, `reuse_verdict`,
   `propose_decision` (evidence mandatory; replacing our code needs a
   theirs-better comparison).
6. Human/operator approves decisions (proposed -> approved).
7. `apply_decisions()` yields decomposition inputs: extra tasks,
   constraints, approved reuses, avoided patterns.
8. `generate_report()` writes `research/<PROJECT>_RESEARCH.md` from state.
9. `research_kb` persists topic findings across projects with staleness
   flags; lookup before re-searching.

## Hard gates (code, never LLM judgment)
- No evidence -> no decision. No license ALLOW (+maintained+tests) -> no
  reuse. Closed source -> behavior notes only, reuse always denied.
- Popularity (stars) is a recorded signal, never proof; single opinions
  never become "repeated".
