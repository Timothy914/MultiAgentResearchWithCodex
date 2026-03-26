from __future__ import annotations

from dyco_repair.agents.base import BaseAgent
from dyco_repair.ensemble.ranker import PatchEnsembler
from dyco_repair.reflection.failures import detect_failure_labels
from dyco_repair.types import AgentResult, PatchCandidate, TaskState


class ManagerAgent(BaseAgent):
    def run(self, state: TaskState) -> AgentResult:
        summary = f"Plan repair for {state.issue_id}: inspect {', '.join(state.target_files)} and validate against failing tests."
        return AgentResult(agent_name=self.name, summary=summary, token_estimate=90)


class LocatorAgent(BaseAgent):
    def run(self, state: TaskState) -> AgentResult:
        if state.difficulty == "hard" and not state.reflection_notes and state.failure_count == 0:
            located_files = [state.target_files[0], "decoy_module.py"]
            summary = "Located likely files but confidence is low because the issue spans multiple call sites."
            uncertainty = 0.85
        else:
            located_files = list(state.target_files)
            summary = "Located the most relevant files for the failing behavior."
            uncertainty = 0.35 if state.difficulty == "easy" else 0.55
        return AgentResult(
            agent_name=self.name,
            summary=summary,
            metadata={"located_files": located_files, "uncertainty": uncertainty},
            token_estimate=140,
        )


class DeveloperAgent(BaseAgent):
    def run(self, state: TaskState) -> AgentResult:
        success_keywords = state.success_patch_keywords
        has_reflection = bool(state.reflection_notes)
        patch_is_good = state.difficulty == "easy" or has_reflection or len(state.patch_candidates) > 1
        candidate = PatchCandidate(
            candidate_id=f"patch-{len(state.patch_candidates) + 1}",
            diff=(
                f"fix({state.issue_id}): apply {' '.join(success_keywords)}"
                if patch_is_good
                else f"fix({state.issue_id}): partial change without {' '.join(success_keywords)}"
            ),
            score=0.82 if patch_is_good else 0.38,
            confidence=0.80 if patch_is_good else 0.42,
            touched_files=state.located_files or state.target_files,
            provenance=self.name,
        )
        summary = "Generated a candidate patch based on the current file hypotheses."
        return AgentResult(
            agent_name=self.name,
            summary=summary,
            patch_candidates=[candidate],
            token_estimate=220,
        )


class ReviewerAgent(BaseAgent):
    def run(self, state: TaskState) -> AgentResult:
        candidate = state.top_patch()
        note = "Patch looks aligned with the failing path."
        if candidate and any(keyword not in candidate.diff for keyword in state.success_patch_keywords):
            note = "Patch may miss an edge case from the failing tests."
        return AgentResult(
            agent_name=self.name,
            summary="Reviewed the current best patch.",
            review_notes=[note],
            token_estimate=120,
        )


class ReflectorAgent(BaseAgent):
    def run(self, state: TaskState) -> AgentResult:
        note = "Re-check failure edge cases and update the candidate to cover the missing success keywords."
        if not state.located_files:
            note = "Return to file localization before editing again."
        return AgentResult(
            agent_name=self.name,
            summary="Produced a strategy-level reflection for the next repair step.",
            reflection_notes=[note],
            token_estimate=110,
        )


class TesterAgent(BaseAgent):
    def __init__(self, name: str, ranker: PatchEnsembler) -> None:
        super().__init__(name)
        self.ranker = ranker

    def run(self, state: TaskState) -> AgentResult:
        candidate = self.ranker.rank(state.patch_candidates)[0] if state.patch_candidates else None
        passed = False
        tests_remaining = max(state.tests_remaining, 1)
        if candidate and all(keyword in candidate.diff for keyword in state.success_patch_keywords):
            passed = True
            tests_remaining = 0
        labels = detect_failure_labels(state, candidate)
        return AgentResult(
            agent_name=self.name,
            summary="Executed the mock test suite against the best patch candidate.",
            tests_passed=passed,
            tests_remaining=tests_remaining,
            failure_labels=labels,
            token_estimate=80,
        )


class EnsembleAgent(BaseAgent):
    def run(self, state: TaskState) -> AgentResult:
        fallback = PatchCandidate(
            candidate_id=f"patch-{len(state.patch_candidates) + 1}",
            diff=f"fix({state.issue_id}): apply {' '.join(state.success_patch_keywords)} with fallback guard",
            score=0.88,
            confidence=0.84,
            touched_files=state.target_files,
            provenance=self.name,
        )
        return AgentResult(
            agent_name=self.name,
            summary="Generated an alternative candidate for cost-aware patch ensembling.",
            patch_candidates=[fallback],
            token_estimate=150,
        )


def build_mock_agent_suite() -> dict[str, BaseAgent]:
    ranker = PatchEnsembler()
    return {
        "invoke_manager": ManagerAgent("manager"),
        "invoke_locator": LocatorAgent("locator"),
        "invoke_developer": DeveloperAgent("developer"),
        "invoke_reviewer": ReviewerAgent("reviewer"),
        "invoke_reflector": ReflectorAgent("reflector"),
        "invoke_tester": TesterAgent("tester", ranker),
        "invoke_ensemble": EnsembleAgent("ensemble"),
    }

