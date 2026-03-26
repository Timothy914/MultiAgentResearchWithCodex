from dyco_repair.orchestrator import BudgetController
from dyco_repair.types import AgentAction, TaskState


def test_budget_controller_stops_on_repeated_action() -> None:
    controller = BudgetController(max_steps=8, max_repeated_action=1)
    state = TaskState(
        issue_id="x",
        description="desc",
        difficulty="easy",
        target_files=["a.py"],
        success_patch_keywords=["fix"],
        budget_total=8,
        budget_remaining=4,
        last_action=AgentAction.DEVELOPER,
        call_counts={AgentAction.DEVELOPER.value: 2},
    )
    assert controller.should_stop(state) is True

