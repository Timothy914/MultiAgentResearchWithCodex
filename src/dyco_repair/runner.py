from __future__ import annotations

from copy import deepcopy
from pathlib import Path

from dyco_repair.agents import build_mock_agent_suite
from dyco_repair.envs import MockIssue, MockRepairEnv
from dyco_repair.eval import summarize_episode
from dyco_repair.logging import RunLogger
from dyco_repair.orchestrator import BudgetController, HeuristicOrchestrator
from dyco_repair.orchestrator.reward import compute_reward
from dyco_repair.types import AgentAction, AgentResult, TaskState, Transition


def run_episode(
    issue: MockIssue,
    output_dir: str | Path | None = None,
    max_steps: int = 8,
    ensemble_threshold: float = 0.75,
) -> tuple[TaskState, list[Transition], dict]:
    env = MockRepairEnv(issue)
    state = issue.initial_state()
    orchestrator = HeuristicOrchestrator(
        budget_controller=BudgetController(max_steps=max_steps),
        ensemble_threshold=ensemble_threshold,
    )
    agents = build_mock_agent_suite()
    transitions: list[Transition] = []

    while True:
        action = orchestrator.select(state)
        if action == AgentAction.TERMINATE:
            terminal_result = AgentResult(
                agent_name="orchestrator",
                summary="Terminated the episode.",
                token_estimate=0,
            )
            state_before = deepcopy(state)
            state.increment_action(action)
            state.final_status = "resolved" if state.tests_passed else "stopped"
            terminal_transition = Transition(
                step=state.step_index,
                action=action,
                agent_result=terminal_result,
                reward=compute_reward(state_before, state, action, terminal_result),
                state_snapshot=env.snapshot(state),
            )
            transitions.append(terminal_transition)
            break

        state_before = deepcopy(state)
        agent = agents[action.value]
        result = agent.run(state)
        state.increment_action(action)
        env.apply_result(state, result)
        reward = compute_reward(state_before, state, action, result)
        transitions.append(
            Transition(
                step=state.step_index,
                action=action,
                agent_result=result,
                reward=reward,
                state_snapshot=env.snapshot(state),
            )
        )
        if state.tests_passed or state.budget_remaining <= 0:
            continue

    summary = summarize_episode(transitions, state.final_status)
    if output_dir is not None:
        logger = RunLogger(output_dir)
        logger.save_trajectory(transitions)
        logger.save_summary(summary)
    return state, transitions, summary
