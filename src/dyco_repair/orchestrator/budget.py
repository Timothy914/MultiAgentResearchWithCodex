from __future__ import annotations

from dyco_repair.types import TaskState


class BudgetController:
    def __init__(self, max_steps: int = 8, max_repeated_action: int = 2) -> None:
        self.max_steps = max_steps
        self.max_repeated_action = max_repeated_action

    def should_stop(self, state: TaskState) -> bool:
        if state.tests_passed or state.budget_remaining <= 0 or state.step_index >= self.max_steps:
            return True
        if state.last_action and state.call_counts.get(state.last_action.value, 0) > self.max_repeated_action:
            return True
        return False

