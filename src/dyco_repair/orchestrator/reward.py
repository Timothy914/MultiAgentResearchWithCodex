from __future__ import annotations

from dyco_repair.types import AgentAction, AgentResult, RewardBreakdown, TaskState


def compute_reward(
    state_before: TaskState,
    state_after: TaskState,
    action: AgentAction,
    result: AgentResult,
) -> RewardBreakdown:
    reward = RewardBreakdown(
        token_cost=result.token_estimate / 1000.0,
        call_cost=0.05,
    )
    if result.patch_candidates:
        reward.patch_quality = max(candidate.score for candidate in result.patch_candidates)
    if state_before.tests_remaining > state_after.tests_remaining:
        reward.test_improvement = float(state_before.tests_remaining - state_after.tests_remaining) * 2.0
    if state_after.tests_passed:
        reward.resolve_reward = 10.0
    if action == AgentAction.TERMINATE and state_after.tests_passed:
        reward.early_stop_bonus = 0.5
    if action == state_before.last_action and action != AgentAction.TESTER:
        reward.redundancy_penalty = 0.75
    return reward

