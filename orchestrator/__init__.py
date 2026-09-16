"""Multi-Agent Orchestrator (MVP).

Deterministic orchestration core: the scheduler, DAG, state store and QA are
pure code. LLMs are used *inside* tasks only (via the task registry), never
for scheduling, merging or state decisions.
"""
from .scheduler import Orchestrator
from .state import StateStore
from . import dag, schema, worker, qa, gitiso, dashboard

__all__ = ["Orchestrator", "StateStore", "dag", "schema", "worker", "qa", "gitiso", "dashboard"]
