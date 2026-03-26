from __future__ import annotations

from dyco_repair.types import PatchCandidate, TaskState


def detect_failure_labels(state: TaskState, candidate: PatchCandidate | None) -> list[str]:
    labels: list[str] = []
    if state.call_counts.get("invoke_locator", 0) > 1:
        labels.append("repeat_localization")
    if candidate is None:
        labels.append("missing_patch")
        return labels
    if any(keyword not in candidate.diff for keyword in state.success_patch_keywords):
        labels.append("wrong_verification")
    if state.reflection_notes and state.failure_count > 0:
        labels.append("high_reflection_cost")
    return labels

