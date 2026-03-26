from __future__ import annotations

from dataclasses import asdict, dataclass, field
from enum import Enum
from typing import Any


class AgentAction(str, Enum):
    MANAGER = "invoke_manager"
    LOCATOR = "invoke_locator"
    DEVELOPER = "invoke_developer"
    REVIEWER = "invoke_reviewer"
    REFLECTOR = "invoke_reflector"
    TESTER = "invoke_tester"
    ENSEMBLE = "invoke_ensemble"
    TERMINATE = "terminate"


@dataclass
class PatchCandidate:
    candidate_id: str
    diff: str
    score: float
    confidence: float
    touched_files: list[str]
    provenance: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class RewardBreakdown:
    resolve_reward: float = 0.0
    test_improvement: float = 0.0
    patch_quality: float = 0.0
    early_stop_bonus: float = 0.0
    token_cost: float = 0.0
    call_cost: float = 0.0
    redundancy_penalty: float = 0.0

    @property
    def total(self) -> float:
        return (
            self.resolve_reward
            + self.test_improvement
            + self.patch_quality
            + self.early_stop_bonus
            - self.token_cost
            - self.call_cost
            - self.redundancy_penalty
        )

    def to_dict(self) -> dict[str, float]:
        data = asdict(self)
        data["total"] = self.total
        return data


@dataclass
class AgentResult:
    agent_name: str
    summary: str
    metadata: dict[str, Any] = field(default_factory=dict)
    patch_candidates: list[PatchCandidate] = field(default_factory=list)
    review_notes: list[str] = field(default_factory=list)
    reflection_notes: list[str] = field(default_factory=list)
    failure_labels: list[str] = field(default_factory=list)
    tests_passed: bool | None = None
    tests_remaining: int | None = None
    token_estimate: int = 0

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["patch_candidates"] = [candidate.to_dict() for candidate in self.patch_candidates]
        return data


@dataclass
class TaskState:
    issue_id: str
    description: str
    difficulty: str
    target_files: list[str]
    success_patch_keywords: list[str]
    budget_total: int
    budget_remaining: int
    step_index: int = 0
    located_files: list[str] = field(default_factory=list)
    patch_candidates: list[PatchCandidate] = field(default_factory=list)
    tests_passed: bool = False
    tests_remaining: int = 1
    failure_count: int = 0
    uncertainty: float = 0.5
    last_action: AgentAction | None = None
    history: list[str] = field(default_factory=list)
    review_notes: list[str] = field(default_factory=list)
    reflection_notes: list[str] = field(default_factory=list)
    failure_labels: list[str] = field(default_factory=list)
    call_counts: dict[str, int] = field(default_factory=dict)
    final_status: str = "running"

    def increment_action(self, action: AgentAction) -> None:
        self.call_counts[action.value] = self.call_counts.get(action.value, 0) + 1
        self.last_action = action
        self.step_index += 1
        self.budget_remaining -= 1

    def top_patch(self) -> PatchCandidate | None:
        if not self.patch_candidates:
            return None
        return sorted(self.patch_candidates, key=lambda candidate: (candidate.score, candidate.confidence), reverse=True)[0]

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["patch_candidates"] = [candidate.to_dict() for candidate in self.patch_candidates]
        data["last_action"] = self.last_action.value if self.last_action else None
        return data


@dataclass
class Transition:
    step: int
    action: AgentAction
    agent_result: AgentResult
    reward: RewardBreakdown
    state_snapshot: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return {
            "step": self.step,
            "action": self.action.value,
            "agent_result": self.agent_result.to_dict(),
            "reward": self.reward.to_dict(),
            "state_snapshot": self.state_snapshot,
        }
