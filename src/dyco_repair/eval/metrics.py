from __future__ import annotations

from dyco_repair.types import Transition


def summarize_episode(transitions: list[Transition], final_status: str) -> dict[str, float | int | str]:
    total_reward = sum(transition.reward.total for transition in transitions)
    total_calls = len(transitions)
    total_tokens = sum(transition.agent_result.token_estimate for transition in transitions)
    redundant_steps = sum(1 for transition in transitions if transition.reward.redundancy_penalty > 0)
    reflection_steps = sum(1 for transition in transitions if transition.action.value == "invoke_reflector")
    return {
        "final_status": final_status,
        "total_reward": round(total_reward, 4),
        "total_calls": total_calls,
        "total_tokens": total_tokens,
        "redundant_steps": redundant_steps,
        "reflection_steps": reflection_steps,
    }

