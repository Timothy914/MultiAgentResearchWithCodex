from __future__ import annotations

from dyco_repair.orchestrator.base import BaseOrchestratorPolicy
from dyco_repair.orchestrator.budget import BudgetController
from dyco_repair.orchestrator.policy import HeuristicOrchestrator


def build_orchestrator(
    policy_name: str = "heuristic",
    max_steps: int = 8,
    ensemble_threshold: float = 0.75,
    reflection_threshold: int = 1,
) -> BaseOrchestratorPolicy:
    if policy_name != "heuristic":
        raise ValueError(f"Unsupported policy: {policy_name}")
    return HeuristicOrchestrator(
        budget_controller=BudgetController(max_steps=max_steps),
        ensemble_threshold=ensemble_threshold,
        reflection_threshold=reflection_threshold,
    )

