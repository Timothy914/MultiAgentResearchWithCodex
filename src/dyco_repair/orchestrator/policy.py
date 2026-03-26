from __future__ import annotations

from dyco_repair.orchestrator.base import BaseOrchestratorPolicy
from dyco_repair.orchestrator.budget import BudgetController
from dyco_repair.types import AgentAction, TaskState


class HeuristicOrchestrator(BaseOrchestratorPolicy):
    def __init__(
        self,
        budget_controller: BudgetController | None = None,
        ensemble_threshold: float = 0.75,
        reflection_threshold: int = 1,
    ) -> None:
        self.budget_controller = budget_controller or BudgetController()
        self.ensemble_threshold = ensemble_threshold
        self.reflection_threshold = reflection_threshold

    def select(self, state: TaskState) -> AgentAction:
        if self.budget_controller.should_stop(state):
            return AgentAction.TERMINATE
        if not state.history:
            return AgentAction.MANAGER
        if not state.located_files:
            return AgentAction.LOCATOR
        if not state.patch_candidates:
            return AgentAction.DEVELOPER
        if (
            state.uncertainty >= self.ensemble_threshold
            and len(state.patch_candidates) < 2
            and state.last_action in {AgentAction.DEVELOPER, AgentAction.LOCATOR}
        ):
            return AgentAction.ENSEMBLE
        if state.failure_count >= self.reflection_threshold and not state.reflection_notes:
            return AgentAction.REFLECTOR
        if not state.review_notes and state.last_action in {AgentAction.DEVELOPER, AgentAction.ENSEMBLE, AgentAction.REFLECTOR}:
            return AgentAction.REVIEWER
        if state.last_action != AgentAction.TESTER:
            return AgentAction.TESTER
        if state.tests_passed:
            return AgentAction.TERMINATE
        if state.failure_count > 0 and not state.reflection_notes:
            return AgentAction.REFLECTOR
        if state.failure_count > 0 and len(state.patch_candidates) < 2 and state.uncertainty >= 0.6:
            return AgentAction.ENSEMBLE
        if state.failure_count > 0:
            return AgentAction.DEVELOPER
        return AgentAction.TERMINATE
