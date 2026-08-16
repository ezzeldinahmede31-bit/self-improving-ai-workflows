"""Hybrid Speculative Model Routing.

Decides per-task whether work runs FULLY LOCAL (deterministic, zero token
cost) or must be escalated to a cloud reasoning model. Fits the premise that
n8n + Docker + Python gates are local, while deep architectural reasoning may
go to the cloud — but never at the cost of security determinism.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Optional


class ExecLocale(Enum):
    LOCAL = "local"              # deterministic: AST/jail/schema/gates — free
    LOCAL_MODEL = "local_model"  # small coder model via Ollama (optional)
    CLOUD_REASONING = "cloud"    # strong cloud model for architecture reasoning


@dataclass
class RoutingDecision:
    locale: ExecLocale
    reason: str
    cloud_allowed: bool = False
    needs_human: bool = False
    tags: list[str] = field(default_factory=list)


# Tasks that MUST stay deterministic and local — never tokens, never cloud
LOCAL_ONLY_FORMS = (
    "ast", "syntax", "schema", "json validation", "security scan",
    "risk score", "lint", "regex", "dedupe", "telemetry", "hash",
    "rate limit", "quirk lookup", "mock routing", "config parse",
)

# Task forms that hint real reasoning may be needed
CLOUD_REASONING_FORMS = (
    "design", "architecture", "tradeoff", "why", "root cause",
    "plan a migration", "recommend a topology",
)


class HybridRouter:
    """Maps a task description to an execution locale with safety rules."""

    def __init__(self, local_model_configured: bool = False,
                 cloud_capable: bool = True):
        self.local_model_configured = local_model_configured  # Ollama present
        self.cloud_capable = cloud_capable

    def route(self, task: str, security_sensitive: bool = False) -> RoutingDecision:
        task_lower = task.lower()

        # 1. Security-sensitive always local + human gate (never cloud-alone)
        if security_sensitive:
            return RoutingDecision(
                locale=ExecLocale.LOCAL, reason="security-sensitive: deterministic + human gate",
                cloud_allowed=False, needs_human=True, tags=["security", "hitl"],
            )

        # 2. Deterministic forms → fully local, free
        if any(f in task_lower for f in LOCAL_ONLY_FORMS):
            return RoutingDecision(
                locale=ExecLocale.LOCAL, reason="deterministic form",
                cloud_allowed=False, tags=["deterministic"],
            )

        # 3. Reasoning forms → local model first, cloud only if configured
        if any(f in task_lower for f in CLOUD_REASONING_FORMS):
            if self.local_model_configured:
                return RoutingDecision(
                    locale=ExecLocale.LOCAL_MODEL, reason="reasoning: local coder model preferred",
                    cloud_allowed=True, tags=["reasoning", "local-model"],
                )
            if self.cloud_capable:
                return RoutingDecision(
                    locale=ExecLocale.CLOUD_REASONING, reason="reasoning: cloud model",
                    cloud_allowed=True, tags=["reasoning", "cloud"],
                )
            return RoutingDecision(
                locale=ExecLocale.LOCAL, reason="reasoning but no model available",
                cloud_allowed=False, tags=["reasoning", "fallback"],
            )

        # 4. Default: cheap local default
        return RoutingDecision(
            locale=ExecLocale.LOCAL, reason="default local", cloud_allowed=True,
            tags=["default"],
        )


# ============================================================
# Practical mapping to the local GPU/Docker stack
# ============================================================
def ollama_command(model: str = "qwen2.5-coder:7b", prompt: str = "") -> list[str]:
    """Return the shell command that runs the small local coder model."""
    return ["ollama", "run", model, prompt]


if __name__ == "__main__":
    router = HybridRouter(local_model_configured=False)
    for task in [
        "run AST security scan on the workflow",
        "why would this architecture fail under load",
        "parse the docker-compose and check ports",
        "design a fanout topology for 4 SaaS providers",
    ]:
        print(task, "->", router.route(task))