"""Extended Thinking & Dual-Process Planning Engine.

Inspired by Kimi K1.5 / Claude Extended Thinking / DeepSeek R1:
- System 2: deep chain-of-thought planner — decomposes the task into a DAG,
  enumerates 3 architectural paths (Tree-of-Thought) with cost/risk scoring.
- System 1: fast tactical executor — turns the chosen plan into concrete
  build steps / node skeletons.

The planner NEVER writes raw code. It emits a plan the rest of the pipeline
will execute deterministically.
"""

from dataclasses import dataclass, field
from typing import Any, Callable, Optional


@dataclass
class DAGNode:
    id: str
    label: str
    deps: list[str] = field(default_factory=list)
    resource: str = ""          # service touched, e.g. "telegram"/"supabase"
    risk_factor: int = 0        # 0-10 advisory only


@dataclass
class ArchitectPath:
    name: str
    summary: str
    complexity: int             # 1 (simplest) .. 5
    est_tokens: int
    risk_index: int             # 0-10
    ops_cost_usd: float
    verdict: str = ""           # "REJECTED" / "CANDIDATE" / "SELECTED"


@dataclass
class DualPlan:
    dag: list[DAGNode]
    paths: list[ArchitectPath]
    selected: Optional[ArchitectPath] = None
    build_steps: list[str] = field(default_factory=list)
    rationale: str = ""


class ExtendedThinkingPlanner:
    """System-2 planner: decompose to DAG, run 3-path ToT, pick cheapest+safest."""

    def __init__(self, budget_usd: float = 20.0, token_cost_per_1k: float = 0.00028):
        self.budget_usd = budget_usd
        self.token_cost_per_1k = token_cost_per_1k

    # ---------- System 2 ----------

    def plan_dag(self, task_prompt: str, services: Optional[list[str]] = None) -> list[DAGNode]:
        """Decompose task into leaf nodes with dependency edges (as good as it
        gets deterministically: trigger, per-service call, join, output)."""
        services = services or []
        nodes = [DAGNode(id="trigger", label="Trigger (webhook/schedule)", risk_factor=0)]
        lhs = None
        for idx, svc in enumerate(services):
            nid = f"call_{idx}"
            deps = [nodes[-1].id] if lhs else []
            nodes.append(DAGNode(id=nid, label=f"Call {svc}", deps=deps,
                                 resource=svc, risk_factor=2 if svc in ("telegram",) else 1))
            lhs = nid
        nodes.append(DAGNode(id="join", label="Join / transform outputs",
                             deps=[n.id for n in nodes[1:]]))
        return nodes

    def micro_decompose(self, service: str) -> list[DAGNode]:
        """#5 — break ONE remote-service interaction into the smallest units
        each independently verifiable. A weak model is fine on one clear step;
        it drowns on multi-step chains. These micro-units map 1:1 to n8n nodes
        so every one can be checked by the verifier in isolation."""
        micro = [
            DAGNode(id=f"{service}_auth", label=f"Auth for {service} (credential)",
                    deps=[], resource=service, risk_factor=3),
            DAGNode(id=f"{service}_schema", label=f"Validate {service} payload schema",
                    deps=[f"{service}_auth"], resource=service, risk_factor=1),
            DAGNode(id=f"{service}_call", label=f"Single {service} API call",
                    deps=[f"{service}_schema"], resource=service, risk_factor=2),
            DAGNode(id=f"{service}_transform", label=f"Map {service} response to canonical shape",
                    deps=[f"{service}_call"], resource=service, risk_factor=1),
            DAGNode(id=f"{service}_error", label=f"{service} error handling + retry/backoff",
                    deps=[f"{service}_call"], resource=service, risk_factor=2),
        ]
        return micro

    def tree_of_thought(self, dag: list[DAGNode]) -> list[ArchitectPath]:
        """Three candidate architectures (Streamlined / Event-Driven / Unorthodox)."""
        n_services = max(0, len(dag) - 2)  # exclude trigger + join

        a1 = ArchitectPath(
            name="A: Streamlined", summary="Linear trigger→call→join. Minimal moving parts.",
            complexity=1, est_tokens=2000 + n_services * 400,
            risk_index=1, ops_cost_usd=0.0,
        )
        a2 = ArchitectPath(
            name="B: Async Event-Driven", summary="Decoupled sub-workflows + dead-letter; better at scale but more infra.",
            complexity=3, est_tokens=4000 + n_services * 800,
            risk_index=2, ops_cost_usd=5.0 if n_services >= 3 else 0.0,
        )
        a3 = ArchitectPath(
            name="C: Multi-Agent Hybrid", summary="Agent decision nodes + self-heal loops. Highest complexity.",
            complexity=5, est_tokens=12000 + n_services * 2000,
            risk_index=4, ops_cost_usd=10.0 if n_services >= 4 else 0.0,
        )
        return [a1, a2, a3]

    def score_and_select(self, paths: list[ArchitectPath], budget_usd: Optional[float] = None) -> Optional[ArchitectPath]:
        """Self-evaluate each path (cost = token cost + ops). Pick lowest cost +
        lowest risk unless an ops floor block exists."""
        budget = budget_usd or self.budget_usd
        for p in paths:
            p.est_usd = round(p.est_tokens / 1000 * self.token_cost_per_1k + p.ops_cost_usd, 3)
            p.verdict = "CANDIDATE"
            if p.est_usd > budget * 0.5:
                p.verdict = "REJECTED"
        viable = [p for p in paths if p.verdict == "CANDIDATE"]
        if not viable:
            # fall back to cheapest even if over budget — but flag it
            cheapest = min(paths, key=lambda p: (p.est_usd, p.risk_index))
            cheapest.verdict = "REJECTED(OVER_BUDGET)-CHEAPEST_FALLBACK"
            return cheapest
        # prefer minimal (complexity * risk) among viable
        viable.sort(key=lambda p: (p.est_usd, p.complexity * p.risk_index))
        selected = viable[0]
        selected.verdict = "SELECTED"
        return selected

    # ---------- System 1 ----------

    def tactical_build_steps(self, selected: ArchitectPath, services: Optional[list[str]] = None) -> list[str]:
        """Turn the selected path into concrete deterministic build steps."""
        steps = ["1. Create trigger node (webhook/schedule)."]
        for idx, svc in enumerate(services or []):
            steps.append(f"{idx + 2}. Add {svc} HTTP sub-workflow (ungated, mocked until approved).")
        steps.append(f"{len((services or [])) + 2}. Join + transform outputs.")
        steps.append(f"{len((services or [])) + 3}. Wire error handling (continueOnFail).")
        steps.append(f"{len((services or [])) + 4}. Route through SecurityGate + QualityGate.")
        steps.append(f"Selected path: {selected.name} (${selected.est_usd:.3f}/mo, risk {selected.risk_index}/10).")
        return steps

    def plan_task(self, task_prompt: str, services: Optional[list[str]] = None) -> DualPlan:
        """Full dual-process flow."""
        dag = self.plan_dag(task_prompt, services)
        paths = self.tree_of_thought(dag)
        selected = self.score_and_select(paths)
        steps = self.tactical_build_steps(selected, services)
        return DualPlan(
            dag=dag, paths=paths, selected=selected, build_steps=steps,
            rationale=(f"Selected {selected.name}: "
                       f"${selected.est_usd:.3f}/mo across {selected.est_tokens} tokens — "
                       f"lowest cost+risk trade-off for {len(services or [])} remote services."),
        )


# ============================================================
# Example
# ============================================================
if __name__ == "__main__":
    planner = ExtendedThinkingPlanner(budget_usd=20.0)
    plan = planner.plan_task("Telegram → Supabase order ingestion", ["telegram", "supabase"])
    print("DAG:", [(n.id, n.label, n.deps) for n in plan.dag])
    for p in plan.paths:
        print(f"{p.name}: ${p.est_usd:.3f}/mo, risk {p.risk_index}, {p.verdict}")
    print("BUILD STEPS:")
    for s in plan.build_steps:
        print("  ", s)