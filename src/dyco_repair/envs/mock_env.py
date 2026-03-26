from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from dyco_repair.types import AgentResult, PatchCandidate, TaskState


@dataclass
class MockIssue:
    issue_id: str
    description: str
    difficulty: str
    target_files: list[str]
    success_patch_keywords: list[str]
    failing_tests: list[str]
    budget_total: int = 8

    @classmethod
    def from_path(cls, path: str | Path) -> "MockIssue":
        with Path(path).open("r", encoding="utf-8") as handle:
            data = json.load(handle)
        return cls(**data)

    def initial_state(self) -> TaskState:
        return TaskState(
            issue_id=self.issue_id,
            description=self.description,
            difficulty=self.difficulty,
            target_files=self.target_files,
            success_patch_keywords=self.success_patch_keywords,
            budget_total=self.budget_total,
            budget_remaining=self.budget_total,
            tests_remaining=len(self.failing_tests),
        )


class MockRepairEnv:
    def __init__(self, issue: MockIssue) -> None:
        self.issue = issue

    def apply_result(self, state: TaskState, result: AgentResult) -> TaskState:
        if "located_files" in result.metadata:
            state.located_files = result.metadata["located_files"]
        if "uncertainty" in result.metadata:
            state.uncertainty = result.metadata["uncertainty"]
        if result.patch_candidates:
            state.patch_candidates.extend(result.patch_candidates)
            state.uncertainty = max(0.2, state.uncertainty - 0.1)
        if result.review_notes:
            state.review_notes.extend(result.review_notes)
        if result.reflection_notes:
            state.reflection_notes.extend(result.reflection_notes)
            state.uncertainty = max(0.2, state.uncertainty - 0.25)
        if result.failure_labels:
            state.failure_labels.extend(result.failure_labels)
        if result.tests_passed is True:
            state.tests_passed = True
            state.tests_remaining = 0
            state.final_status = "resolved"
        elif result.tests_passed is False:
            state.failure_count += 1
            state.tests_remaining = result.tests_remaining if result.tests_remaining is not None else state.tests_remaining
            state.uncertainty = min(0.95, state.uncertainty + 0.15)
        state.history.append(result.summary)
        return state

    @staticmethod
    def snapshot(state: TaskState) -> dict:
        return state.to_dict()

    @staticmethod
    def best_patch(state: TaskState) -> PatchCandidate | None:
        return state.top_patch()
